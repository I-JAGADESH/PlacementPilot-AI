from typing import List

from pydantic import BaseModel, Field


class AssessmentQuestion(BaseModel):
    id: int
    skill: str
    topic: str
    question: str
    options: List[str]


class AssessmentStartRequest(BaseModel):
    skill: str = Field(..., min_length=1)


class AssessmentStartResponse(BaseModel):
    assessment_id: int
    skill: str
    total_questions: int
    questions: List[AssessmentQuestion]


class AssessmentAnswer(BaseModel):
    question_id: int
    selected_option: str


class AssessmentSubmitRequest(BaseModel):
    assessment_id: int
    answers: List[AssessmentAnswer]


class TopicPerformance(BaseModel):
    topic: str
    total_questions: int
    correct_answers: int
    score_percentage: float


class AssessmentResult(BaseModel):
    assessment_id: int
    skill: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    performance_level: str
    topic_performance: List[TopicPerformance]
    strong_topics: List[str]
    weak_topics: List[str]
    recommendations: List[str]