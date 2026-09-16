"""
FastAPI Router for Production Aptitude Preparation Engine (Phase 2).
Provides endpoints for taxonomy, formulas, company patterns, assessments, scoring, and analytics.
"""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.aptitude.formulas import get_formula_for_subtopic
from app.aptitude.models import (
    AptitudeAssessment,
    AssessmentQuestionMap,
    CompanyPattern,
    DIDataset,
    QuestionOption,
)
from app.aptitude.schemas import (
    AptitudeQuestionSchema,
    CompanyPatternSchema,
    FormulaReferenceSchema,
    QuestionOptionSchema,
    StartAssessmentRequest,
    StartAssessmentResponse,
    SubmitAssessmentRequest,
    UserAnalyticsResponse,
)
from app.aptitude.service import (
    create_assessment_session,
    evaluate_and_submit_assessment,
    get_user_aptitude_analytics,
    seed_aptitude_taxonomy,
)
from app.aptitude.taxonomy import TAXONOMY_DATA
from app.core.security import get_current_user
from app.database.database import get_db

router = APIRouter(
    prefix="/api/v1/aptitude",
    tags=["Aptitude Engine"],
)


def _get_user_id(current_user) -> int:
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID is unavailable.",
        )
    return int(user_id)


@router.get("/taxonomy")
def get_aptitude_taxonomy(
    current_user=Depends(get_current_user),
):
    return TAXONOMY_DATA


@router.get("/formulas/{subtopic_slug}", response_model=FormulaReferenceSchema)
def get_subtopic_formula(
    subtopic_slug: str,
    current_user=Depends(get_current_user),
):
    return get_formula_for_subtopic(subtopic_slug)


@router.get("/patterns", response_model=List[CompanyPatternSchema])
def get_company_patterns(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    seed_aptitude_taxonomy(db)
    patterns = db.query(CompanyPattern).all()
    return patterns


@router.post("/assessments/start", response_model=StartAssessmentResponse)
def start_aptitude_assessment(
    request: StartAssessmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = _get_user_id(current_user)

    assessment = create_assessment_session(
        db=db,
        user_id=user_id,
        mode=request.mode,
        subtopic_slug=request.subtopic_slug,
        domain_slug=request.domain_slug,
        company_pattern_slug=request.company_pattern_slug,
        num_questions=request.num_questions,
    )

    q_maps = (
        db.query(AssessmentQuestionMap)
        .filter(AssessmentQuestionMap.assessment_id == assessment.id)
        .order_by(AssessmentQuestionMap.question_order.asc())
        .all()
    )

    questions_res = []
    for qm in q_maps:
        q = qm.question
        opts_raw = json.loads(qm.options_order_json) if qm.options_order_json else []

        di_data = None
        if q.di_dataset:
            di_data = {
                "title": q.di_dataset.title,
                "description": q.di_dataset.description,
                "content": json.loads(q.di_dataset.content_json),
            }

        questions_res.append(
            AptitudeQuestionSchema(
                question_id=q.id,
                question_order=qm.question_order,
                difficulty=q.difficulty,
                question_type=q.question_type,
                question_text=q.question_text,
                options=[QuestionOptionSchema(key=o["key"], text=o["text"]) for o in opts_raw],
                estimated_time_seconds=q.estimated_time_seconds,
                negative_marking=q.negative_marking,
                subtopic_name=q.subtopic.name if q.subtopic else None,
                subtopic_slug=q.subtopic.slug if q.subtopic else None,
                di_dataset=di_data,
            )
        )

    return StartAssessmentResponse(
        assessment_id=assessment.id,
        mode=assessment.mode,
        title=assessment.title,
        duration_seconds=assessment.duration_seconds,
        total_questions=assessment.total_questions,
        start_time=assessment.start_time,
        questions=questions_res,
    )


@router.post("/assessments/{assessment_id}/submit")
def submit_aptitude_assessment(
    assessment_id: int,
    request: SubmitAssessmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = _get_user_id(current_user)

    raw_answers = [
        {
            "question_id": a.question_id,
            "selected_option_or_text": a.selected_option_or_text,
            "time_spent_seconds": a.time_spent_seconds,
        }
        for a in request.answers
    ]

    try:
        result = evaluate_and_submit_assessment(
            db=db,
            user_id=user_id,
            assessment_id=assessment_id,
            raw_answers=raw_answers,
        )
        return result
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/history")
def get_aptitude_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = _get_user_id(current_user)

    attempts = (
        db.query(AptitudeAssessment)
        .filter(AptitudeAssessment.user_id == user_id)
        .order_by(AptitudeAssessment.start_time.desc())
        .all()
    )

    return [
        {
            "assessment_id": a.id,
            "mode": a.mode,
            "title": a.title,
            "status": a.status,
            "total_questions": a.total_questions,
            "attempted_questions": a.attempted_questions,
            "correct_answers": a.correct_answers,
            "score_percentage": a.score_percentage,
            "accuracy_percentage": a.accuracy_percentage,
            "speed_qpm": a.speed_qpm,
            "created_at": a.start_time,
        }
        for a in attempts
    ]


@router.get("/analytics", response_model=UserAnalyticsResponse)
def get_aptitude_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = _get_user_id(current_user)
    return get_user_aptitude_analytics(db, user_id)
