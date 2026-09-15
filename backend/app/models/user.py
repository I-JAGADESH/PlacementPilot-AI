from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # User Information
    full_name = Column(String(100), nullable=False)

    email = Column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )

    # Hashed Password
    password_hash = Column(
        String(255),
        nullable=False,
    )

    # User Role
    role = Column(
        String(20),
        nullable=False,
        default="student",
    )

    # Timestamps
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

    profile = relationship(
        "StudentProfile",
        uselist=False,
        cascade="all, delete-orphan",
    )

    assessment_attempts = relationship(
        "AssessmentAttempt",
        cascade="all, delete-orphan",
    )

    interview_results = relationship(
        "InterviewResult",
        cascade="all, delete-orphan",
    )

    interview_sessions = relationship(
        "InterviewSession",
        cascade="all, delete-orphan",
    )

    ats_results = relationship(
        "ATSResult",
        cascade="all, delete-orphan",
    )

    training_progress = relationship(
        "TrainingProgress",
        cascade="all, delete-orphan",
    )

    github_account = relationship(
        "GitHubAccount",
        uselist=False,
        cascade="all, delete-orphan",
    )

    oauth_states = relationship(
        "OAuthState",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<User(id={self.id}, "
            f"name='{self.full_name}', "
            f"email='{self.email}', "
            f"role='{self.role}')>"
        )