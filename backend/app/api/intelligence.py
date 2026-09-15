from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db

from app.intelligence.schemas import (
    SkillGapRequest,
    SkillIntelligenceResponse,
)

from app.intelligence.service import (
    analyze_skill_intelligence,
)


router = APIRouter(
    prefix="/api/v1/intelligence",
    tags=["Skill Intelligence"],
)


@router.post(
    "/skill-gap",
    response_model=SkillIntelligenceResponse,
)
def analyze_skill_gap(
    request: SkillGapRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze the student's skills and identify strong,
    weak, and missing skills.
    """

    result = analyze_skill_intelligence(
        db=db,
        user_id=current_user.id,
        job_description=request.job_description,
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found",
        )

    return result