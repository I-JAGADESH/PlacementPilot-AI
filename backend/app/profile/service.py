from typing import Optional

from sqlalchemy.orm import Session

from app.profile.models import (
    StudentCertification,
    StudentProfile,
    StudentProject,
    StudentSkill,
)
from app.profile.schemas import (
    CertificationCreate,
    ProjectCreate,
    SkillCreate,
    StudentProfileUpdate,
)


def get_profile(
    db: Session,
    user_id: int,
) -> Optional[StudentProfile]:
    return (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == user_id)
        .first()
    )


def calculate_profile_completion(
    profile: StudentProfile,
) -> bool:
    required_fields = [
        profile.cgpa,
        profile.attendance,
        profile.target_role,
        profile.aptitude_score,
        profile.communication_score,
    ]

    has_basic_fields = all(
        value is not None
        for value in required_fields
    )

    has_skills = len(profile.skills) > 0
    has_project = len(profile.projects) > 0

    return (
        has_basic_fields
        and has_skills
        and has_project
    )


def create_or_update_profile(
    db: Session,
    user_id: int,
    data: StudentProfileUpdate,
) -> StudentProfile:

    profile = get_profile(db, user_id)

    if profile is None:
        profile = StudentProfile(
            user_id=user_id,
        )
        db.add(profile)

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        if field in {
            "github_url",
            "linkedin_url",
            "portfolio_url",
        }:
            value = str(value) if value is not None else None

        setattr(profile, field, value)

    db.flush()

    profile.is_complete = calculate_profile_completion(
        profile
    )

    db.commit()
    db.refresh(profile)

    return profile


def add_skill(
    db: Session,
    user_id: int,
    data: SkillCreate,
) -> Optional[StudentSkill]:

    profile = get_profile(db, user_id)

    if profile is None:
        return None

    skill = StudentSkill(
        profile_id=profile.id,
        name=data.name.strip(),
        category=data.category,
        proficiency=data.proficiency,
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    profile.is_complete = calculate_profile_completion(
        profile
    )
    db.commit()

    return skill


def update_skill(
    db: Session,
    user_id: int,
    skill_id: int,
    data: SkillCreate,
) -> Optional[StudentSkill]:

    profile = get_profile(db, user_id)

    if profile is None:
        return None

    skill = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.id == skill_id,
            StudentSkill.profile_id == profile.id,
        )
        .first()
    )

    if skill is None:
        return None

    skill.name = data.name.strip()
    skill.category = data.category
    skill.proficiency = data.proficiency

    db.commit()
    db.refresh(skill)

    profile.is_complete = calculate_profile_completion(
        profile
    )
    db.commit()

    return skill


def delete_skill(
    db: Session,
    user_id: int,
    skill_id: int,
) -> bool:

    profile = get_profile(db, user_id)

    if profile is None:
        return False

    skill = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.id == skill_id,
            StudentSkill.profile_id == profile.id,
        )
        .first()
    )

    if skill is None:
        return False

    db.delete(skill)
    db.commit()

    profile.is_complete = calculate_profile_completion(
        profile
    )
    db.commit()

    return True


def add_project(
    db: Session,
    user_id: int,
    data: ProjectCreate,
) -> Optional[StudentProject]:

    profile = get_profile(db, user_id)

    if profile is None:
        return None

    project = StudentProject(
        profile_id=profile.id,
        title=data.title.strip(),
        description=data.description,
        technologies=data.technologies,
        github_url=(
            str(data.github_url)
            if data.github_url
            else None
        ),
        live_url=(
            str(data.live_url)
            if data.live_url
            else None
        ),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    profile.is_complete = calculate_profile_completion(
        profile
    )
    db.commit()

    return project


def delete_project(
    db: Session,
    user_id: int,
    project_id: int,
) -> bool:

    profile = get_profile(db, user_id)

    if profile is None:
        return False

    project = (
        db.query(StudentProject)
        .filter(
            StudentProject.id == project_id,
            StudentProject.profile_id == profile.id,
        )
        .first()
    )

    if project is None:
        return False

    db.delete(project)
    db.commit()

    profile.is_complete = calculate_profile_completion(
        profile
    )
    db.commit()

    return True


def add_certification(
    db: Session,
    user_id: int,
    data: CertificationCreate,
) -> Optional[StudentCertification]:

    profile = get_profile(db, user_id)

    if profile is None:
        return None

    certification = StudentCertification(
        profile_id=profile.id,
        name=data.name.strip(),
        issuer=data.issuer,
        issue_year=data.issue_year,
        credential_url=(
            str(data.credential_url)
            if data.credential_url
            else None
        ),
    )

    db.add(certification)
    db.commit()
    db.refresh(certification)

    return certification


def delete_certification(
    db: Session,
    user_id: int,
    certification_id: int,
) -> bool:

    profile = get_profile(db, user_id)

    if profile is None:
        return False

    certification = (
        db.query(StudentCertification)
        .filter(
            StudentCertification.id == certification_id,
            StudentCertification.profile_id == profile.id,
        )
        .first()
    )

    if certification is None:
        return False

    db.delete(certification)
    db.commit()

    return True