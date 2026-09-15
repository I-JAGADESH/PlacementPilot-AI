from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# INTERVIEW START REQUEST
# ============================================================

class InterviewStartRequest(BaseModel):
    company: str = Field(
        default="Generic",
        description="Target company for the interview",
    )

    job_description: str = Field(
        ...,
        min_length=10,
        description="Target job description",
    )

    interview_type: str = Field(
        default="technical",
        description="Interview type: technical, hr, or behavioral",
    )

    difficulty: str = Field(
        default="medium",
        description="Interview difficulty: easy, medium, or hard",
    )


# ============================================================
# INTERVIEW QUESTION
# ============================================================

class InterviewQuestion(BaseModel):
    question_id: int
    question: str
    category: str
    difficulty: str

    # Company associated with this question
    company: Optional[str] = None


# ============================================================
# ANSWER SUBMISSION
# ============================================================

class InterviewAnswerRequest(BaseModel):
    interview_id: int = Field(
        ...,
        description="Active interview session ID",
    )

    question_id: int = Field(
        ...,
        description="Question ID being answered",
    )

    answer: str = Field(
        ...,
        min_length=1,
        description="Student's interview answer",
    )


# ============================================================
# INTERVIEW EVALUATION
# ============================================================

class InterviewEvaluation(BaseModel):
    question_id: int = 0

    score: float = Field(
        ge=0,
        le=100,
    )

    strengths: list[str] = []

    weaknesses: list[str] = []

    feedback: str

    ideal_answer: str


# ============================================================
# INTERVIEW START RESPONSE
# ============================================================

class InterviewStartResponse(BaseModel):
    interview_id: int

    company: str

    target_role: str

    interview_type: str

    difficulty: str

    total_questions: int

    first_question: Optional[InterviewQuestion] = None


# ============================================================
# INTERVIEW ANSWER RESPONSE
# ============================================================

class InterviewAnswerResponse(BaseModel):
    interview_id: int

    question_id: int

    evaluation: InterviewEvaluation

    next_question: Optional[InterviewQuestion] = None

    completed: bool


# ============================================================
# INTERVIEW SUMMARY RESPONSE
# ============================================================

class InterviewSummaryResponse(BaseModel):
    interview_id: int

    company: str

    target_role: str

    interview_type: str

    difficulty: str

    completed_questions: int

    total_questions: int

    average_score: float

    completed: bool