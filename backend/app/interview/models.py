from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.database.database import Base


class InterviewResult(Base):
    __tablename__ = "interview_results"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False, index=True)

    interview_id = Column(Integer, nullable=False, index=True)

    company = Column(
        String(100),
        nullable=False,
        default="Generic",
    )

    target_role = Column(
        String(150),
        nullable=False,
        default="Software Engineer",
    )

    interview_type = Column(
        String(50),
        nullable=False,
        default="technical",
    )

    difficulty = Column(
        String(50),
        nullable=False,
        default="medium",
    )

    completed_questions = Column(
        Integer,
        nullable=False,
        default=0,
    )

    total_questions = Column(
        Integer,
        nullable=False,
        default=0,
    )

    average_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    performance_level = Column(
        String(50),
        nullable=False,
        default="needs_improvement",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )