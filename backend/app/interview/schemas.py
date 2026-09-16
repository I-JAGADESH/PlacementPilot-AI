from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

FRAMING_DISCLAIMER = "realistic company-style interview questions based on role expectations and standard interview patterns"


# ============================================================
# CONFIG & SELECTION SCHEMAS
# ============================================================

class InterviewConfigResponse(BaseModel):
    roles: List[str]
    experience_levels: List[str]
    interview_rounds: List[str]
    difficulties: List[str]
    domains: List[str]
    user_profile_summary: Optional[Dict[str, Any]] = None


class InterviewStartRequest(BaseModel):
    company: str = Field(
        default="Generic",
        description="Target company for the interview preparation",
    )

    role: str = Field(
        default="Software Engineer",
        description="Target role for the interview",
    )

    experience_level: str = Field(
        default="Entry Level",
        description="Experience level: Student / Fresher, Entry Level, Intermediate, Advanced",
    )

    interview_round: str = Field(
        default="Technical MCQ",
        description="Interview round out of the 11 supported rounds",
    )

    difficulty: str = Field(
        default="Medium",
        description="Interview difficulty: Easy, Medium, Hard, Expert",
    )

    domain: Optional[str] = Field(
        default="DSA",
        description="Technical domain for the interview",
    )

    job_description: Optional[str] = Field(
        default="Standard role expectations and technical patterns.",
        description="Optional target job description",
    )

    # Legacy compatibility fallback mapping
    interview_type: Optional[str] = Field(
        default=None,
        description="Legacy field for interview type compatibility",
    )


# ============================================================
# INTERVIEW QUESTION SCHEMA
# ============================================================

class InterviewQuestion(BaseModel):
    question_id: int
    question: str
    category: str
    difficulty: str

    company: Optional[str] = None
    round: Optional[str] = None
    role: Optional[str] = None
    experience_level: Optional[str] = None
    domain: Optional[str] = None

    question_type: str = "short_answer"
    options: Optional[List[str]] = None
    expected_answer_type: Optional[str] = None
    rubric: Optional[str] = None
    concepts_tested: List[str] = []
    estimated_time: Optional[str] = "5 mins"

    profile_relevance: Optional[Dict[str, Any]] = None
    disclaimer: str = FRAMING_DISCLAIMER


# ============================================================
# ANSWER SUBMISSION & EVALUATION
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


class InterviewEvaluation(BaseModel):
    question_id: int = 0

    score: float = Field(ge=0, le=100)
    technical_score: float = Field(default=0.0, ge=0, le=100)
    communication_score: float = Field(default=0.0, ge=0, le=100)

    strengths: List[str] = []
    weaknesses: List[str] = []
    technical_gaps: List[str] = []
    communication_feedback: List[str] = []
    missed_concepts: List[str] = []

    feedback: str
    ideal_answer: str
    adaptation_reason: Optional[str] = None


# ============================================================
# INTERVIEW RESPONSES
# ============================================================

class InterviewStartResponse(BaseModel):
    interview_id: int
    company: str
    target_role: str
    experience_level: str
    interview_type: str
    difficulty: str
    domain: Optional[str] = None
    total_questions: int
    first_question: Optional[InterviewQuestion] = None
    profile_signals: Optional[Dict[str, Any]] = None


class InterviewAnswerResponse(BaseModel):
    interview_id: int
    question_id: int
    evaluation: InterviewEvaluation
    next_question: Optional[InterviewQuestion] = None
    completed: bool
    adaptation_notice: Optional[str] = None


class InterviewSummaryResponse(BaseModel):
    interview_id: int
    company: str
    target_role: str
    experience_level: str
    interview_type: str
    difficulty: str
    domain: Optional[str] = None
    completed_questions: int
    total_questions: int
    average_score: float
    communication_score: float
    performance_level: str
    completed: bool

    strengths: List[str] = []
    weaknesses: List[str] = []
    technical_gaps: List[str] = []
    communication_feedback: List[str] = []
    missed_concepts: List[str] = []
    recommended_topics: List[str] = []
    next_recommended_difficulty: str = "Medium"
    preparation_roadmap: List[str] = []


class InterviewHistoryItem(BaseModel):
    id: int
    company: str
    target_role: str
    experience_level: str
    interview_type: str
    difficulty: str
    domain: Optional[str] = None
    average_score: float
    performance_level: str
    created_at: str