from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.roadmap.schemas import RoadmapRequest, RoadmapResponse
from app.roadmap.service import generate_roadmap


router = APIRouter(
    prefix="/api/v1/roadmap",
    tags=["Preparation Roadmap"],
)


@router.post(
    "/generate",
    response_model=RoadmapResponse,
)
def generate_student_roadmap(
    request: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        roadmap = generate_roadmap(
            db=db,
            user_id=current_user.id,
            job_description=request.job_description,
        )

        return roadmap

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
