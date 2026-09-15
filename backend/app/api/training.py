from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import get_current_user
from app.training.models import TrainingProgress
from app.training.schemas import (
    TopicCompletionRequest,
    TopicCompletionResponse,
    TrainingResponse,
)
from app.training.service import build_training_response, get_training_content


router = APIRouter(
    prefix="/api/v1/training",
    tags=["Training"],
)


def _get_user_id(current_user) -> int:
    user_id = getattr(current_user, "id", None)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID is unavailable.",
        )

    return int(user_id)


def _get_completed_topics(
    db: Session,
    user_id: int,
    skill: str,
) -> list[str]:
    rows = (
        db.query(TrainingProgress)
        .filter(
            TrainingProgress.user_id == user_id,
            TrainingProgress.skill == skill,
            TrainingProgress.completed.is_(True),
        )
        .all()
    )

    return [row.topic for row in rows]


@router.get(
    "/{skill}",
    response_model=TrainingResponse,
)
def get_training(
    skill: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    skill = skill.strip()

    if not skill:
        raise HTTPException(
            status_code=400,
            detail="Skill is required.",
        )

    content = get_training_content(skill)

    if not content:
        raise HTTPException(
            status_code=404,
            detail=f"No training content available for skill: {skill}",
        )

    user_id = _get_user_id(current_user)

    completed_topics = _get_completed_topics(
        db=db,
        user_id=user_id,
        skill=skill,
    )

    return build_training_response(
        skill=skill,
        completed_topics=completed_topics,
    )


@router.post(
    "/complete",
    response_model=TopicCompletionResponse,
)
def complete_training_topic(
    request: TopicCompletionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    skill = request.skill.strip()
    topic = request.topic.strip()

    if not skill:
        raise HTTPException(
            status_code=400,
            detail="Skill is required.",
        )

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic is required.",
        )

    content = get_training_content(skill)

    if not content:
        raise HTTPException(
            status_code=404,
            detail=f"No training content available for skill: {skill}",
        )

    valid_topics = {
        item["topic"]
        for item in content
    }

    if topic not in valid_topics:
        raise HTTPException(
            status_code=404,
            detail=f"Topic '{topic}' was not found for skill '{skill}'.",
        )

    user_id = _get_user_id(current_user)

    progress = (
        db.query(TrainingProgress)
        .filter(
            TrainingProgress.user_id == user_id,
            TrainingProgress.skill == skill,
            TrainingProgress.topic == topic,
        )
        .first()
    )

    if progress is None:
        progress = TrainingProgress(
            user_id=user_id,
            skill=skill,
            topic=topic,
            completed=request.completed,
            completed_at=(
                datetime.now(timezone.utc)
                if request.completed
                else None
            ),
        )

        db.add(progress)

    else:
        progress.completed = request.completed
        progress.completed_at = (
            datetime.now(timezone.utc)
            if request.completed
            else None
        )

    db.commit()
    db.refresh(progress)

    completed_topics = _get_completed_topics(
        db=db,
        user_id=user_id,
        skill=skill,
    )

    total_topics = len(content)

    progress_percentage = (
        round(
            (len(completed_topics) / total_topics) * 100,
            2,
        )
        if total_topics
        else 0.0
    )

    return TopicCompletionResponse(
        skill=skill,
        topic=topic,
        completed=progress.completed,
        progress_percentage=progress_percentage,
        completed_topics=len(completed_topics),
        total_topics=total_topics,
    )