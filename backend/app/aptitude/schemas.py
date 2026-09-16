"""
Pydantic Schemas for Aptitude Preparation Engine (Phase 2).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaxonomySubtopicSchema(BaseModel):
    name: str
    slug: str


class TaxonomyTopicSchema(BaseModel):
    name: str
    slug: str
    subtopics: List[TaxonomySubtopicSchema]


class TaxonomyDomainSchema(BaseModel):
    name: str
    slug: str
    topics: List[TaxonomyTopicSchema]


class FormulaReferenceSchema(BaseModel):
    title: str
    formula: str
    concept_summary: str
    when_to_use: str
    important_notes: str
    common_traps: str


class CompanyPatternSchema(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    total_questions: int
    duration_minutes: int
    negative_marking: float


class QuestionOptionSchema(BaseModel):
    key: str
    text: str


class AptitudeQuestionSchema(BaseModel):
    question_id: int
    question_order: int
    difficulty: str
    question_type: str
    question_text: str
    options: List[QuestionOptionSchema] = []
    estimated_time_seconds: int
    negative_marking: float
    subtopic_name: Optional[str] = None
    subtopic_slug: Optional[str] = None
    di_dataset: Optional[Dict[str, Any]] = None


class StartAssessmentRequest(BaseModel):
    mode: str = Field(..., description="Practice Mode, Retry Mode, Topic Practice, Weak Topic Practice, Full Mock Test, Placement Test, Company-pattern Test")
    subtopic_slug: Optional[str] = None
    domain_slug: Optional[str] = None
    company_pattern_slug: Optional[str] = None
    num_questions: int = Field(10, ge=1, le=50)


class StartAssessmentResponse(BaseModel):
    assessment_id: int
    mode: str
    title: str
    duration_seconds: int
    total_questions: int
    start_time: datetime
    questions: List[AptitudeQuestionSchema]


class SubmitSingleAnswerRequest(BaseModel):
    question_id: int
    selected_option_or_text: str
    time_spent_seconds: int = 0


class SubmitAssessmentRequest(BaseModel):
    answers: List[SubmitSingleAnswerRequest]


class AssessmentResultResponse(BaseModel):
    assessment_id: int
    mode: str
    title: str
    status: str
    total_questions: int
    attempted_questions: int
    correct_answers: int
    incorrect_answers: int
    skipped_answers: int
    raw_score: float
    score_percentage: float
    accuracy_percentage: float
    speed_qpm: float
    time_spent_seconds: int
    domain_performance: Dict[str, Any]
    subtopic_performance: Dict[str, Any]
    strong_topics: List[str]
    weak_topics: List[str]
    recommendations: List[str]


class UserAnalyticsResponse(BaseModel):
    has_data: bool
    message: Optional[str] = None
    overall_score: float = 0.0
    overall_accuracy: float = 0.0
    total_attempts: int = 0
    strongest_subtopics: List[Dict[str, Any]] = []
    weakest_subtopics: List[Dict[str, Any]] = []
    recent_attempts: List[Dict[str, Any]] = []
    recommendations: List[str] = []
