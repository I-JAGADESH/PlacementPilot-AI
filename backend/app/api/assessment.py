import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.assessment.models import AssessmentAttempt
from app.assessment.question_bank import get_available_skills
from app.assessment.schemas import (
    AssessmentResult,
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSubmitRequest,
)
from app.assessment.service import (
    build_assessment_questions,
    evaluate_assessment,
)
from app.core.security import get_current_user
from app.database.database import get_db


router = APIRouter(
    prefix="/api/v1/assessment",
    tags=["Assessment"],
)


def _get_user_id(current_user) -> int:
    user_id = getattr(current_user, "id", None)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID is unavailable.",
        )

    return int(user_id)


@router.get("/skills")
def get_assessment_skills(
    current_user=Depends(get_current_user),
):
    return {
        "skills": get_available_skills(),
    }


@router.post(
    "/start",
    response_model=AssessmentStartResponse,
)
def start_assessment(
    request: AssessmentStartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    skill = request.skill.strip()

    if not skill:
        raise HTTPException(
            status_code=400,
            detail="Skill is required.",
        )

    questions = build_assessment_questions(skill)

    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"No assessment available for skill: {skill}",
        )

    user_id = _get_user_id(current_user)

    assessment = AssessmentAttempt(
        user_id=user_id,
        skill=skill,
        total_questions=len(questions),
        correct_answers=0,
        score_percentage=0.0,
        performance_level="In Progress",
        strong_topics=None,
        weak_topics=None,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return AssessmentStartResponse(
        assessment_id=assessment.id,
        skill=skill,
        total_questions=len(questions),
        questions=questions,
    )


@router.post(
    "/submit",
    response_model=AssessmentResult,
)
def submit_assessment(
    request: AssessmentSubmitRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = _get_user_id(current_user)

    assessment = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.id == request.assessment_id,
            AssessmentAttempt.user_id == user_id,
        )
        .first()
    )

    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment attempt not found.",
        )

    if assessment.performance_level != "In Progress":
        raise HTTPException(
            status_code=400,
            detail="This assessment has already been submitted.",
        )

    answers = [
        {
            "question_id": answer.question_id,
            "selected_option": answer.selected_option,
        }
        for answer in request.answers
    ]

    result = evaluate_assessment(
        skill=assessment.skill,
        answers=answers,
    )

    assessment.correct_answers = result["correct_answers"]
    assessment.score_percentage = result["score_percentage"]
    assessment.performance_level = result["performance_level"]

    assessment.strong_topics = json.dumps(
        result["strong_topics"]
    )

    assessment.weak_topics = json.dumps(
        result["weak_topics"]
    )

    db.commit()
    db.refresh(assessment)

    return AssessmentResult(
        assessment_id=assessment.id,
        skill=result["skill"],
        total_questions=result["total_questions"],
        correct_answers=result["correct_answers"],
        score_percentage=result["score_percentage"],
        performance_level=result["performance_level"],
        topic_performance=result["topic_performance"],
        strong_topics=result["strong_topics"],
        weak_topics=result["weak_topics"],
        recommendations=result["recommendations"],
    )


@router.get("/history")
def get_assessment_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = _get_user_id(current_user)

    attempts = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id == user_id
        )
        .order_by(
            AssessmentAttempt.created_at.desc()
        )
        .all()
    )

    return [
        {
            "assessment_id": attempt.id,
            "skill": attempt.skill,
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
            "score_percentage": attempt.score_percentage,
            "performance_level": attempt.performance_level,
            "created_at": attempt.created_at,
        }
        for attempt in attempts
    ]