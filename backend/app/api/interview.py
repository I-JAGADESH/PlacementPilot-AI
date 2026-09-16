from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db

from app.interview.schemas import (
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewSummaryResponse,
    InterviewConfigResponse,
    InterviewHistoryItem,
)
from app.interview.service import (
    get_interview_config,
    create_interview_session,
    get_interview_session,
    get_next_question,
    evaluate_answer,
    save_interview_evaluation,
    get_interview_summary,
    get_user_interview_history,
    get_user_recommendations,
)


router = APIRouter(
    prefix="/api/v1/interview",
    tags=["Interview"],
)


def _get_user_id(current_user) -> int:
    """Safely extract the authenticated user's ID."""
    user_id = getattr(current_user, "id", None)
    if user_id is None and isinstance(current_user, dict):
        user_id = current_user.get("id") or current_user.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID not available.",
        )
    return int(user_id)


@router.get(
    "/config",
    response_model=InterviewConfigResponse,
)
def get_config(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return available interview config options and current user's profile summary."""
    user_id = _get_user_id(current_user)
    config = get_interview_config(db=db, user_id=user_id)
    return config


@router.post(
    "/start",
    response_model=InterviewStartResponse,
)
def start_interview(
    request: InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Start a new user-isolated, profile-aware interview session."""
    user_id = _get_user_id(current_user)

    session = create_interview_session(
        db=db,
        request=request,
        user_id=user_id,
    )

    first_question = get_next_question(
        db=db,
        interview_id=session.id,
    )

    return InterviewStartResponse(
        interview_id=session.id,
        company=session.company,
        target_role=session.target_role,
        experience_level=session.experience_level,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        domain=session.domain,
        total_questions=session.total_questions,
        first_question=first_question,
    )


@router.get(
    "/history",
    response_model=List[InterviewHistoryItem],
)
def get_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retrieve all past interview results for the authenticated user."""
    user_id = _get_user_id(current_user)
    return get_user_interview_history(db=db, user_id=user_id)


@router.get(
    "/recommendations",
)
def get_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get aggregate weak areas and preparation roadmap for the authenticated user."""
    user_id = _get_user_id(current_user)
    return get_user_recommendations(db=db, user_id=user_id)


@router.get(
    "/{interview_id}",
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get active interview session status and current question with ownership verification."""
    user_id = _get_user_id(current_user)

    session = get_interview_session(db=db, interview_id=interview_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this interview session.")

    current_q = get_next_question(db=db, interview_id=interview_id)
    return {
        "interview_id": session.id,
        "company": session.company,
        "target_role": session.target_role,
        "experience_level": session.experience_level,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "domain": session.domain,
        "current_index": session.current_index,
        "total_questions": session.total_questions,
        "status": session.status,
        "current_question": current_q,
    }


@router.post(
    "/answer",
    response_model=InterviewAnswerResponse,
)
def submit_answer(
    request: InterviewAnswerRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Submit an interview answer, evaluate against rubric, apply adaptive flow, and return next question."""
    user_id = _get_user_id(current_user)

    session = get_interview_session(db=db, interview_id=request.interview_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this interview session.")

    current_question = get_next_question(db=db, interview_id=request.interview_id)
    if current_question is None:
        raise HTTPException(status_code=400, detail="Interview is already completed.")

    if current_question.question_id != request.question_id:
        raise HTTPException(status_code=400, detail="Invalid question ID for this session.")

    answer_text = request.answer.strip()
    if not answer_text:
        raise HTTPException(status_code=400, detail="Answer cannot be empty.")

    evaluation = evaluate_answer(
        question=current_question.question,
        answer=answer_text,
        category=current_question.category,
        company=session.company,
        difficulty=session.difficulty,
        question_type=current_question.question_type,
        rubric=current_question.rubric,
    )
    evaluation.question_id = request.question_id

    updated_session = save_interview_evaluation(
        db=db,
        interview_id=request.interview_id,
        question_id=request.question_id,
        answer=answer_text,
        evaluation=evaluation,
    )

    next_q = get_next_question(db=db, interview_id=request.interview_id)
    completed = next_q is None

    return InterviewAnswerResponse(
        interview_id=request.interview_id,
        question_id=request.question_id,
        evaluation=evaluation,
        next_question=next_q,
        completed=completed,
        adaptation_notice=evaluation.adaptation_reason,
    )


@router.post(
    "/{interview_id}/complete",
)
def complete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Manually complete an active interview session."""
    user_id = _get_user_id(current_user)

    session = get_interview_session(db=db, interview_id=interview_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this interview session.")

    session.status = "completed"
    db.commit()
    summary = get_interview_summary(db=db, interview_id=interview_id)
    return summary


@router.get(
    "/{interview_id}/summary",
    response_model=InterviewSummaryResponse,
)
def interview_summary(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get complete interview evaluation summary report with user ownership verification."""
    user_id = _get_user_id(current_user)

    session = get_interview_session(db=db, interview_id=interview_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this interview session.")

    summary = get_interview_summary(db=db, interview_id=interview_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Interview summary not available.")

    return InterviewSummaryResponse(**summary)