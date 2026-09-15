from typing import Optional

from pydantic import BaseModel, Field


class ATSAnalyzeResponse(BaseModel):
    filename: str
    text_length: int
    page_count: int

    extracted_text: str = Field(
        description="Normalized text extracted from the resume."
    )

    ats_score: Optional[float] = Field(
        default=None,
        description="ATS compatibility score from 0 to 100."
    )

    matched_skills: list[str] = Field(
        default_factory=list,
        description="Skills detected in the resume."
    )

    missing_skills: list[str] = Field(
        default_factory=list,
        description="Skills missing from the resume."
    )

    sections_found: list[str] = Field(
        default_factory=list,
        description="Resume sections detected."
    )

    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations for improving the resume."
    )