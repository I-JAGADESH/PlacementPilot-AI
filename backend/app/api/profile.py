from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.profile.schemas import (
    CertificationCreate,
    CertificationResponse,
    ProjectCreate,
    ProjectResponse,
    SkillCreate,
    SkillResponse,
    StudentProfileResponse,
    StudentProfileUpdate,
)
from app.profile.service import (
    add_certification,
    add_project,
    add_skill,
    create_or_update_profile,
    delete_certification,
    delete_project,
    delete_skill,
    get_profile,
    update_skill,
)


router = APIRouter(
    prefix="/api/v1/profile",
    tags=["Student Profile"],
)


@router.get(
    "",
    response_model=StudentProfileResponse,
)
def get_student_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_profile(
        db,
        current_user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return profile


@router.put(
    "",
    response_model=StudentProfileResponse,
)
def update_student_profile(
    data: StudentProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_or_update_profile(
        db,
        current_user.id,
        data,
    )


@router.post(
    "/skills",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill(
    data: SkillCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = add_skill(
        db,
        current_user.id,
        data,
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create your student profile first",
        )

    return skill


@router.get(
    "/skills",
    response_model=list[SkillResponse],
)
def get_skills(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_profile(
        db,
        current_user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return profile.skills


@router.put(
    "/skills/{skill_id}",
    response_model=SkillResponse,
)
def edit_skill(
    skill_id: int,
    data: SkillCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = update_skill(
        db,
        current_user.id,
        skill_id,
        data,
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    return skill


@router.delete(
    "/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_skill(
    skill_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_skill(
        db,
        current_user.id,
        skill_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    return None


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = add_project(
        db,
        current_user.id,
        data,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create your student profile first",
        )

    return project


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def get_projects(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_profile(
        db,
        current_user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return profile.projects


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project(
    project_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_project(
        db,
        current_user.id,
        project_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return None


@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_certification(
    data: CertificationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    certification = add_certification(
        db,
        current_user.id,
        data,
    )

    if certification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create your student profile first",
        )

    return certification


@router.get(
    "/certifications",
    response_model=list[CertificationResponse],
)
def get_certifications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_profile(
        db,
        current_user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return profile.certifications


@router.delete(
    "/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_certification(
    certification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_certification(
        db,
        current_user.id,
        certification_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found",
        )

    return None