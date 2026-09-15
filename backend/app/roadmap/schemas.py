from pydantic import BaseModel, Field
from typing import List


class RoadmapRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=10,
        description="Target job description",
    )


class RoadmapTask(BaseModel):
    skill: str
    priority: str
    duration_days: int
    topics: List[str]
    reason: str


class RoadmapResponse(BaseModel):
    target_role: str
    overall_skill_score: float
    total_days: int
    tasks: List[RoadmapTask]
    daily_plan: List[str]
    recommendations: List[str]