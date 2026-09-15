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
)

from app.interview.service import (
    get_questions,
    evaluate_answer,
    create_interview_session,
    get_interview_session,
    get_next_question,
    save_interview_evaluation,
    get_interview_summary,
)


router = APIRouter(
    prefix="/api/v1/interview",
    tags=["Interview"],
)


def _get_user_id(current_user) -> int:
    """
    Safely extract the authenticated user's ID.
    """
    user_id = getattr(current_user, "id", None)

    if user_id is None and isinstance(current_user, dict):
        user_id = current_user.get("id") or current_user.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID not available.",
        )

    return int(user_id)


@router.post(
    "/start",
    response_model=InterviewStartResponse,
)
def start_interview(
    request: InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Start a new database-persisted interview session.
    """
    user_id = _get_user_id(current_user)

    questions = get_questions(
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        company=request.company,
    )

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="No interview questions available.",
        )

    target_role = "Software Engineer"

    session = create_interview_session(
        db=db,
        questions=questions,
        target_role=target_role,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        company=request.company,
        user_id=user_id,
    )

    first_question = get_next_question(
        db=db,
        interview_id=session.id,
    )

    return InterviewStartResponse(
        interview_id=session.id,
        company=session.company,
        target_role=target_role,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        total_questions=len(questions),
        first_question=first_question,
    )


@router.post(
    "/answer",
    response_model=InterviewAnswerResponse,
)
def submit_answer(
    request: InterviewAnswerRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Submit an interview answer and persist evaluation.
    Verifies user ownership of the interview session.
    """
    user_id = _get_user_id(current_user)

    session = get_interview_session(
        db=db,
        interview_id=request.interview_id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this interview.",
        )

    current_question = get_next_question(
        db=db,
        interview_id=request.interview_id,
    )

    if current_question is None:
        raise HTTPException(
            status_code=400,
            detail="Interview is already completed.",
        )

    if current_question.question_id != request.question_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid question ID for this interview.",
        )

    answer = request.answer.strip()

    if not answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty.",
        )

    evaluation = evaluate_answer(
        question=current_question.question,
        answer=answer,
        category=current_question.category,
        company=session.company,
        difficulty=session.difficulty,
    )

    evaluation.question_id = request.question_id

    save_interview_evaluation(
        db=db,
        interview_id=request.interview_id,
        question_id=request.question_id,
        answer=answer,
        evaluation=evaluation,
    )

    next_question = get_next_question(
        db=db,
        interview_id=request.interview_id,
    )

    completed = next_question is None

    return InterviewAnswerResponse(
        interview_id=request.interview_id,
        question_id=request.question_id,
        evaluation=evaluation,
        next_question=next_question,
        completed=completed,
    )


@router.get(
    "/{interview_id}/summary",
    response_model=InterviewSummaryResponse,
)
def interview_summary(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get current/final interview summary with user ownership verification.
    """
    user_id = _get_user_id(current_user)

    session = get_interview_session(
        db=db,
        interview_id=interview_id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this interview.",
        )

    summary = get_interview_summary(
        db=db,
        interview_id=interview_id,
    )

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    return InterviewSummaryResponse(
        interview_id=summary["interview_id"],
        company=summary.get("company", "Generic"),
        target_role=summary["target_role"],
        interview_type=summary["interview_type"],
        difficulty=summary["difficulty"],
        completed_questions=summary["completed_questions"],
        total_questions=summary["total_questions"],
        average_score=summary["average_score"],
        completed=summary["completed"],
    )