from pydantic import BaseModel, Field
from typing import List


class TrainingTopic(BaseModel):
    skill: str
    topic: str
    explanation: str
    key_points: List[str]
    practice_questions: List[str]


class TrainingResponse(BaseModel):
    skill: str
    total_topics: int
    completed_topics: int
    progress_percentage: float
    topics: List[TrainingTopic]


class TopicCompletionRequest(BaseModel):
    skill: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    completed: bool = True


class TopicCompletionResponse(BaseModel):
    skill: str
    topic: str
    completed: bool
    progress_percentage: float
    completed_topics: int
    total_topics: int