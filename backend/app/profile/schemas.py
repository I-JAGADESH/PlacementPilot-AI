from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# ============================================================
# SKILL SCHEMAS
# ============================================================

class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    proficiency: float = Field(
        default=50,
        ge=0,
        le=100,
    )


class SkillResponse(SkillCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PROJECT SCHEMAS
# ============================================================

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    technologies: Optional[str] = None
    github_url: Optional[HttpUrl] = None
    live_url: Optional[HttpUrl] = None


class ProjectResponse(ProjectCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CERTIFICATION SCHEMAS
# ============================================================

class CertificationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    issuer: Optional[str] = Field(
        default=None,
        max_length=150,
    )
    issue_year: Optional[int] = Field(
        default=None,
        ge=1950,
        le=2100,
    )
    credential_url: Optional[HttpUrl] = None


class CertificationResponse(CertificationCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# STUDENT PROFILE
# ============================================================

class StudentProfileUpdate(BaseModel):
    cgpa: Optional[float] = Field(
        default=None,
        ge=0,
        le=10,
    )

    attendance: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    backlogs: int = Field(
        default=0,
        ge=0,
    )

    aptitude_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    communication_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    target_role: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    target_company: Optional[str] = Field(
        default=None,
        max_length=150,
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    college: Optional[str] = Field(
        default=None,
        max_length=200,
    )

    degree: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    graduation_year: Optional[int] = Field(
        default=None,
        ge=2000,
        le=2100,
    )

    github_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None

    bio: Optional[str] = None


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int

    cgpa: Optional[float]
    attendance: Optional[float]
    backlogs: int

    aptitude_score: Optional[float]
    communication_score: Optional[float]

    target_role: Optional[str]
    target_company: Optional[str]

    phone: Optional[str]
    college: Optional[str]
    degree: Optional[str]
    graduation_year: Optional[int]

    github_url: Optional[HttpUrl]
    linkedin_url: Optional[HttpUrl]
    portfolio_url: Optional[HttpUrl]

    bio: Optional[str]

    is_complete: bool

    skills: List[SkillResponse]
    projects: List[ProjectResponse]
    certifications: List[CertificationResponse]

    model_config = ConfigDict(from_attributes=True)