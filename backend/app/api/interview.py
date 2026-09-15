from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user

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


# ============================================================
# HELPER — GET USER ID
# ============================================================

def _get_user_id(current_user) -> int:
    """
    Safely extract the authenticated user's ID.
    """

    user_id = getattr(current_user, "id", None)

    if user_id is None and isinstance(current_user, dict):
        user_id = current_user.get("id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID not available.",
        )

    return int(user_id)


# ============================================================
# START INTERVIEW
# ============================================================

@router.post(
    "/start",
    response_model=InterviewStartResponse,
)
def start_interview(
    request: InterviewStartRequest,
    current_user=Depends(get_current_user),
):
    """
    Start a new interview session.

    The interview is based on:
    - Company
    - Job description
    - Interview type
    - Difficulty
    """

    # --------------------------------------------------------
    # Get authenticated user ID
    # --------------------------------------------------------

    user_id = _get_user_id(current_user)

    # --------------------------------------------------------
    # Generate company-specific questions
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Determine target role
    # --------------------------------------------------------

    target_role = "Software Engineer"

    # --------------------------------------------------------
    # Create interview session
    # --------------------------------------------------------

    session = create_interview_session(
        questions=questions,
        target_role=target_role,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        company=request.company,
        user_id=user_id,
    )

    # --------------------------------------------------------
    # Get first question
    # --------------------------------------------------------

    first_question = get_next_question(
        session["interview_id"]
    )

    return InterviewStartResponse(
        interview_id=session["interview_id"],
        company=session["company"],
        target_role=target_role,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        total_questions=len(questions),
        first_question=first_question,
    )


# ============================================================
# SUBMIT ANSWER
# ============================================================

@router.post(
    "/answer",
    response_model=InterviewAnswerResponse,
)
def submit_answer(
    request: InterviewAnswerRequest,
    current_user=Depends(get_current_user),
):
    """
    Submit an interview answer.

    The answer is evaluated by the AI evaluator.
    Gemini is used when configured.
    Otherwise the fallback evaluator is used.
    """

    # --------------------------------------------------------
    # Get authenticated user ID
    # --------------------------------------------------------

    user_id = _get_user_id(current_user)

    # --------------------------------------------------------
    # Get interview session
    # --------------------------------------------------------

    session = get_interview_session(
        request.interview_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    # --------------------------------------------------------
    # Security — verify interview belongs to current user
    # --------------------------------------------------------

    session_user_id = session.get("user_id")

    if session_user_id is not None and session_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this interview.",
        )

    # --------------------------------------------------------
    # Get current question
    # --------------------------------------------------------

    current_question = get_next_question(
        request.interview_id
    )

    if current_question is None:
        raise HTTPException(
            status_code=400,
            detail="Interview is already completed.",
        )

    # --------------------------------------------------------
    # Validate question ID
    # --------------------------------------------------------

    if current_question.question_id != request.question_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid question ID for this interview.",
        )

    # --------------------------------------------------------
    # Validate answer
    # --------------------------------------------------------

    answer = request.answer.strip()

    if not answer:
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty.",
        )

    # --------------------------------------------------------
    # Evaluate answer
    # --------------------------------------------------------

    evaluation = evaluate_answer(
        question=current_question.question,
        answer=answer,
        category=current_question.category,
        company=session.get(
            "company",
            "Generic",
        ),
        difficulty=session.get(
            "difficulty",
            "medium",
        ),
    )

    # --------------------------------------------------------
    # Make sure evaluation belongs to question
    # --------------------------------------------------------

    evaluation.question_id = request.question_id

    # --------------------------------------------------------
    # Save evaluation
    # --------------------------------------------------------

    save_interview_evaluation(
        interview_id=request.interview_id,
        question_id=request.question_id,
        answer=answer,
        evaluation=evaluation,
    )

    # --------------------------------------------------------
    # Get next question
    # --------------------------------------------------------

    next_question = get_next_question(
        request.interview_id
    )

    completed = next_question is None

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return InterviewAnswerResponse(
        interview_id=request.interview_id,
        question_id=request.question_id,
        evaluation=evaluation,
        next_question=next_question,
        completed=completed,
    )


# ============================================================
# GET INTERVIEW SUMMARY
# ============================================================

@router.get(
    "/{interview_id}/summary",
    response_model=InterviewSummaryResponse,
)
def interview_summary(
    interview_id: int,
    current_user=Depends(get_current_user),
):
    """
    Get the current/final interview summary.
    """

    # --------------------------------------------------------
    # Get authenticated user ID
    # --------------------------------------------------------

    user_id = _get_user_id(current_user)

    # --------------------------------------------------------
    # Verify session exists and belongs to user
    # --------------------------------------------------------

    session = get_interview_session(
        interview_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    session_user_id = session.get("user_id")

    if session_user_id is not None and session_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this interview.",
        )

    # --------------------------------------------------------
    # Get summary
    # --------------------------------------------------------

    summary = get_interview_summary(
        interview_id
    )

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Interview session not found.",
        )

    # --------------------------------------------------------
    # Return summary
    # --------------------------------------------------------

    return InterviewSummaryResponse(
        interview_id=summary["interview_id"],
        company=summary.get(
            "company",
            "Generic",
        ),
        target_role=summary["target_role"],
        interview_type=summary["interview_type"],
        difficulty=summary["difficulty"],
        completed_questions=summary["completed_questions"],
        total_questions=summary["total_questions"],
        average_score=summary["average_score"],
        completed=summary["completed"],
    )