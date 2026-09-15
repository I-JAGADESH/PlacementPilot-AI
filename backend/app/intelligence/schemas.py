from pydantic import BaseModel
from typing import Optional


class SkillGapRequest(BaseModel):
    job_description: Optional[str] = None


class SkillAnalysisItem(BaseModel):
    name: str
    proficiency: float
    status: str
    priority: str
    evidence: list[str]
    reason: str


class SkillGapItem(BaseModel):
    name: str
    status: str
    priority: str
    evidence: list[str]
    reason: str


class SkillIntelligenceResponse(BaseModel):
    overall_skill_score: float

    strong_skills: list[SkillAnalysisItem]
    weak_skills: list[SkillAnalysisItem]

    missing_skills: list[SkillGapItem]

    recommendations: list[str]

    total_profile_skills: int
    total_missing_skills: int