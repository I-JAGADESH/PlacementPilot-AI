from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Academic information
    cgpa = Column(Float, nullable=True)
    attendance = Column(Float, nullable=True)
    backlogs = Column(Integer, nullable=False, default=0)

    # Placement preparation scores
    aptitude_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)

    # Career information
    target_role = Column(String(100), nullable=True)
    target_company = Column(String(150), nullable=True)

    # Additional profile information
    phone = Column(String(20), nullable=True)
    college = Column(String(200), nullable=True)
    degree = Column(String(100), nullable=True)
    graduation_year = Column(Integer, nullable=True)

    # Professional links
    github_url = Column(String(300), nullable=True)
    linkedin_url = Column(String(300), nullable=True)
    portfolio_url = Column(String(300), nullable=True)

    bio = Column(Text, nullable=True)

    # Profile completion
    is_complete = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    skills = relationship(
        "StudentSkill",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    projects = relationship(
        "StudentProject",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    certifications = relationship(
        "StudentCertification",
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)

    # Skill proficiency from 0 to 100
    proficiency = Column(Float, nullable=False, default=50)

    profile = relationship(
        "StudentProfile",
        back_populates="skills",
    )


class StudentProject(Base):
    __tablename__ = "student_projects"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(String(500), nullable=True)
    github_url = Column(String(300), nullable=True)
    live_url = Column(String(300), nullable=True)

    profile = relationship(
        "StudentProfile",
        back_populates="projects",
    )


class StudentCertification(Base):
    __tablename__ = "student_certifications"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    issuer = Column(String(150), nullable=True)
    issue_year = Column(Integer, nullable=True)
    credential_url = Column(String(300), nullable=True)

    profile = relationship(
        "StudentProfile",
        back_populates="certifications",
    )