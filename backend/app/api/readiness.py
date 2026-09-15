from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.assessment.models import AssessmentAttempt
from app.ats.models import ATSResult
from app.core.security import get_current_user
from app.database.database import get_db
from app.interview.models import InterviewResult
from app.ml.readiness import readiness_model
from app.profile.models import StudentProfile
from app.training.models import TrainingProgress


router = APIRouter(
    prefix="/api/v1/readiness",
    tags=["Placement Readiness"],
)


def _average(
    values: List[float],
    default: float = 0.0,
) -> float:
    valid_values = [
        float(value)
        for value in values
        if value is not None
    ]

    if not valid_values:
        return default

    return sum(valid_values) / len(valid_values)


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(
        minimum,
        min(float(value), maximum),
    )


def _get_value(
    obj: Any,
    names: List[str],
    default: float = 0.0,
) -> float:
    for name in names:
        value = getattr(obj, name, None)

        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                continue

    return default


def _calculate_skill_score(
    profile: Any,
) -> float:
    skills = getattr(
        profile,
        "skills",
        [],
    ) or []

    if not skills:
        return 0.0

    proficiency_values = []

    for skill in skills:
        proficiency = getattr(
            skill,
            "proficiency",
            None,
        )

        if proficiency is not None:
            try:
                proficiency_values.append(
                    float(proficiency)
                )
            except (TypeError, ValueError):
                pass

    return round(
        _average(proficiency_values),
        2,
    )


def _calculate_dsa_score(
    profile: Any,
) -> float:
    skills = getattr(
        profile,
        "skills",
        [],
    ) or []

    dsa_names = {
        "data structures",
        "data structures and algorithms",
        "dsa",
        "algorithms",
    }

    for skill in skills:
        name = str(
            getattr(
                skill,
                "name",
                "",
            )
        ).strip().lower()

        if name in dsa_names:
            proficiency = getattr(
                skill,
                "proficiency",
                0,
            )

            try:
                return round(
                    _clamp(
                        float(proficiency),
                    ),
                    2,
                )
            except (
                TypeError,
                ValueError,
            ):
                return 0.0

    return 0.0


def _calculate_project_score(
    profile: Any,
) -> float:
    projects = getattr(
        profile,
        "projects",
        [],
    ) or []

    if not projects:
        return 0.0

    project_count = len(projects)

    return round(
        min(
            100.0,
            50.0 + project_count * 15.0,
        ),
        2,
    )


def _calculate_certification_score(
    profile: Any,
) -> float:
    certifications = getattr(
        profile,
        "certifications",
        [],
    ) or []

    if not certifications:
        return 0.0

    certification_count = len(
        certifications
    )

    return round(
        min(
            100.0,
            40.0 + certification_count * 20.0,
        ),
        2,
    )


def _calculate_ats_score(
    db: Session,
    user_id: int,
) -> Optional[float]:
    """
    Get the latest persisted ATS score for the authenticated user.
    Returns None if the user has not completed an ATS resume scan.
    """
    result = (
        db.query(ATSResult)
        .filter(
            ATSResult.user_id == user_id,
            ATSResult.ats_score >= 0,
        )
        .order_by(
            ATSResult.created_at.desc(),
            ATSResult.id.desc(),
        )
        .first()
    )

    if result is None:
        return None

    return round(
        _clamp(
            float(result.ats_score or 0.0)
        ),
        2,
    )


def _calculate_interview_score(
    db: Session,
    user_id: int,
) -> Optional[float]:
    """
    Get the latest completed interview score for the authenticated user.
    Returns None if the user has not completed a mock interview.
    """
    result = (
        db.query(InterviewResult)
        .filter(
            InterviewResult.user_id == user_id,
            InterviewResult.completed_questions > 0,
            InterviewResult.total_questions > 0,
        )
        .order_by(
            InterviewResult.created_at.desc(),
            InterviewResult.id.desc(),
        )
        .first()
    )

    if result is None:
        return None

    return round(
        _clamp(
            float(result.average_score or 0.0)
        ),
        2,
    )


def _calculate_training_score(
    db: Session,
    user_id: int,
) -> float:
    progress_rows = (
        db.query(TrainingProgress)
        .filter(
            TrainingProgress.user_id == user_id,
        )
        .all()
    )

    if not progress_rows:
        return 0.0

    total_topics = len(progress_rows)

    completed_topics = sum(
        1
        for row in progress_rows
        if row.completed
    )

    if total_topics == 0:
        return 0.0

    return round(
        (completed_topics / total_topics) * 100.0,
        2,
    )


def _calculate_assessment_score(
    db: Session,
    user_id: int,
) -> float:
    attempts = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.performance_level != "In Progress",
        )
        .order_by(
            AssessmentAttempt.created_at.desc()
        )
        .all()
    )

    if not attempts:
        return 0.0

    latest_scores = []
    seen_skills = set()

    for attempt in attempts:
        skill = str(
            attempt.skill or ""
        ).strip().lower()

        if skill in seen_skills:
            continue

        seen_skills.add(skill)

        latest_scores.append(
            float(
                attempt.score_percentage or 0.0
            )
        )

    return round(
        _average(latest_scores),
        2,
    )


def _calculate_assessment_by_skill(
    db: Session,
    user_id: int,
) -> Dict[str, float]:
    attempts = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.performance_level != "In Progress",
        )
        .order_by(
            AssessmentAttempt.created_at.desc()
        )
        .all()
    )

    scores: Dict[str, float] = {}

    for attempt in attempts:
        skill = str(
            attempt.skill or ""
        ).strip().lower()

        if not skill or skill in scores:
            continue

        scores[skill] = round(
            float(
                attempt.score_percentage or 0.0
            ),
            2,
        )

    return scores


def _calculate_dynamic_skill_score(
    profile: Any,
    assessment_score: float,
    training_score: float,
) -> float:
    profile_skill_score = _calculate_skill_score(
        profile
    )

    components = [
        profile_skill_score,
    ]

    if assessment_score > 0:
        components.append(assessment_score)

    if training_score > 0:
        components.append(training_score)

    return round(
        _average(
            components,
            default=profile_skill_score,
        ),
        2,
    )


def _calculate_dynamic_dsa_score(
    profile: Any,
    assessment_by_skill: Dict[str, float],
) -> float:
    profile_dsa = _calculate_dsa_score(
        profile
    )

    assessment_dsa_scores = []

    for skill_name, score in assessment_by_skill.items():
        if (
            skill_name in {
                "algorithms",
                "data structures",
                "data structures and algorithms",
                "dsa",
            }
        ):
            assessment_dsa_scores.append(score)

    if not assessment_dsa_scores:
        return profile_dsa

    assessment_dsa = _average(
        assessment_dsa_scores,
        default=profile_dsa,
    )

    if profile_dsa <= 0:
        return round(
            assessment_dsa,
            2,
        )

    return round(
        _average(
            [
                profile_dsa,
                assessment_dsa,
            ]
        ),
        2,
    )


def _build_strong_areas(
    factors: Dict[str, float],
) -> List[str]:
    labels = {
        "cgpa": "Academic performance",
        "attendance": "Attendance",
        "aptitude": "Aptitude",
        "communication": "Communication",
        "skills": "Technical skills",
        "projects": "Projects",
        "certifications": "Certifications",
        "ats": "Resume / ATS",
        "interview": "Interview performance",
    }

    strong = []

    for key, value in factors.items():
        if (
            key in labels
            and value >= 75
        ):
            strong.append(
                labels[key]
            )

    return strong[:5]


def _build_weak_areas(
    factors: Dict[str, float],
) -> List[str]:
    labels = {
        "cgpa": "Academic performance",
        "attendance": "Attendance",
        "aptitude": "Aptitude",
        "communication": "Communication",
        "skills": "Technical skills",
        "projects": "Projects",
        "certifications": "Certifications",
        "ats": "Resume / ATS",
        "interview": "Interview performance",
    }

    weak = []

    for key, value in factors.items():
        if (
            key in labels
            and value < 60
        ):
            weak.append(
                labels[key]
            )

    return weak[:5]


def _build_priority_gaps(
    factors: Dict[str, float],
) -> List[Dict[str, Any]]:
    labels = {
        "skills": "Technical skills",
        "aptitude": "Aptitude",
        "communication": "Communication",
        "projects": "Projects",
        "certifications": "Certifications",
        "ats": "Resume / ATS",
        "interview": "Interview preparation",
    }

    gaps = []

    for key, value in factors.items():
        if (
            key in labels
            and value < 70
        ):
            gaps.append(
                {
                    "area": labels[key],
                    "current_score": round(
                        value,
                        2,
                    ),
                    "target_score": 70,
                    "gap": round(
                        70.0 - value,
                        2,
                    ),
                }
            )

    gaps.sort(
        key=lambda item: item[
            "current_score"
        ]
    )

    return gaps[:5]


def _build_recommendations(
    prediction_recommendations: List[str],
    priority_gaps: List[Dict[str, Any]],
    training_score: float,
    assessment_score: float,
    ats_attempted: bool,
    interview_attempted: bool,
) -> List[str]:
    recommendations = list(
        prediction_recommendations
    )

    if not ats_attempted:
        recommendations.append(
            "Upload your resume to ATS Analyzer to unlock resume readiness feedback."
        )

    if not interview_attempted:
        recommendations.append(
            "Complete a mock interview to evaluate your interview readiness."
        )

    if training_score > 0 and training_score < 70:
        recommendations.append(
            "Continue completing personalized training topics to strengthen weak areas."
        )

    if assessment_score > 0 and assessment_score < 70:
        recommendations.append(
            "Retake skill assessments after training to verify improvement."
        )

    for gap in priority_gaps:
        area = gap["area"]

        if area == "Technical skills":
            recommendations.append(
                "Strengthen job-relevant technical skills through targeted practice."
            )

        elif area == "Aptitude":
            recommendations.append(
                "Practice quantitative aptitude, logical reasoning and placement-style problems."
            )

        elif area == "Communication":
            recommendations.append(
                "Practice structured answers and mock HR interviews."
            )

        elif area == "Projects":
            recommendations.append(
                "Build or improve projects with clear technologies and measurable outcomes."
            )

        elif area == "Resume / ATS" and ats_attempted:
            recommendations.append(
                "Improve resume keywords and project evidence for the target role."
            )

        elif area == "Interview preparation" and interview_attempted:
            recommendations.append(
                "Complete technical and behavioral mock interviews."
            )

    if not recommendations:
        recommendations.append(
            "Continue target-role practice and complete regular assessments."
        )

    unique = []

    for recommendation in recommendations:
        if recommendation not in unique:
            unique.append(recommendation)

    return unique[:8]


@router.get("")
def get_placement_readiness(
    db: Session = Depends(get_db),
    current_user: Any = Depends(
        get_current_user
    ),
):
    """
    Calculate placement readiness using
    the authenticated student's real profile,
    training progress and completed assessments.
    No hardcoded defaults are used for unattempted modules.
    """

    user_id = getattr(
        current_user,
        "id",
        None,
    )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authenticated user.",
        )

    profile = (
        db.query(StudentProfile)
        .filter(
            StudentProfile.user_id == user_id
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found.",
        )

    cgpa = _get_value(
        profile,
        ["cgpa"],
        0.0,
    )

    attendance = _get_value(
        profile,
        ["attendance"],
        0.0,
    )

    backlogs_value = getattr(
        profile,
        "backlogs",
        0,
    )

    try:
        backlogs = max(
            0,
            int(backlogs_value or 0),
        )
    except (
        TypeError,
        ValueError,
    ):
        backlogs = 0

    aptitude_score = _get_value(
        profile,
        [
            "aptitude_score",
            "aptitude",
        ],
        0.0,
    )

    communication_score = _get_value(
        profile,
        [
            "communication_score",
            "communication",
        ],
        0.0,
    )

    profile_skill_score = _calculate_skill_score(
        profile
    )

    training_score = _calculate_training_score(
        db=db,
        user_id=int(user_id),
    )

    assessment_score = _calculate_assessment_score(
        db=db,
        user_id=int(user_id),
    )

    assessment_by_skill = _calculate_assessment_by_skill(
        db=db,
        user_id=int(user_id),
    )

    skill_score = _calculate_dynamic_skill_score(
        profile=profile,
        assessment_score=assessment_score,
        training_score=training_score,
    )

    dsa_score = _calculate_dynamic_dsa_score(
        profile=profile,
        assessment_by_skill=assessment_by_skill,
    )

    project_score = _calculate_project_score(
        profile
    )

    certification_score = (
        _calculate_certification_score(
            profile
        )
    )

    # Real persisted module results. Explicit None if unattempted.
    ats_result_score = _calculate_ats_score(
        db=db,
        user_id=int(user_id),
    )

    ats_attempted = ats_result_score is not None
    ats_score = ats_result_score if ats_attempted else 0.0

    interview_result_score = _calculate_interview_score(
        db=db,
        user_id=int(user_id),
    )

    interview_attempted = interview_result_score is not None
    interview_score = interview_result_score if interview_attempted else 0.0

    prediction = readiness_model.predict(
        cgpa=cgpa,
        attendance=attendance,
        backlogs=backlogs,
        aptitude_score=aptitude_score,
        communication_score=communication_score,
        skill_score=skill_score,
        project_score=project_score,
        certification_score=certification_score,
        ats_score=ats_score,
        interview_score=interview_score,
    )

    factors = prediction.factors

    strong_areas = _build_strong_areas(
        factors
    )

    weak_areas = _build_weak_areas(
        factors
    )

    priority_gaps = _build_priority_gaps(
        factors
    )

    recommendations = _build_recommendations(
        prediction.recommendations,
        priority_gaps,
        training_score,
        assessment_score,
        ats_attempted,
        interview_attempted,
    )

    target_role = getattr(
        profile,
        "target_role",
        None,
    )

    target_company = getattr(
        profile,
        "target_company",
        None,
    )

    return {
        "overall_score": prediction.score,
        "level": prediction.level,
        "probability": prediction.probability,

        "target": {
            "role": target_role,
            "company": target_company,
        },

        "breakdown": {
            "technical_score": round(
                skill_score,
                2,
            ),

            "dsa_score": round(
                dsa_score,
                2,
            ),

            "resume_score": ats_result_score,
            "resume_attempted": ats_attempted,

            "project_score": round(
                project_score,
                2,
            ),

            "communication_score": round(
                communication_score,
                2,
            ),

            "aptitude_score": round(
                aptitude_score,
                2,
            ),

            "interview_score": interview_result_score,
            "interview_attempted": interview_attempted,

            "academic_score": round(
                min(
                    100.0,
                    cgpa / 10.0 * 100.0,
                ),
                2,
            ),

            "attendance_score": round(
                attendance,
                2,
            ),

            "certification_score": round(
                certification_score,
                2,
            ),

            "training_score": round(
                training_score,
                2,
            ),

            "assessment_score": round(
                assessment_score,
                2,
            ),
        },

        "factors": factors,

        "strong_areas": strong_areas,

        "weak_areas": weak_areas,

        "priority_gaps": priority_gaps,

        "recommendations": recommendations,

        "learning_evidence": {
            "profile_skill_score": round(
                profile_skill_score,
                2,
            ),
            "training_score": round(
                training_score,
                2,
            ),
            "assessment_score": round(
                assessment_score,
                2,
            ),
            "completed_assessment_skills": len(
                assessment_by_skill
            ),
        },
    }