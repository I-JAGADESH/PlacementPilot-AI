from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.database import Base


class InterviewResult(Base):
    __tablename__ = "interview_results"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company = Column(String(100), nullable=False, default="Generic")
    target_role = Column(String(150), nullable=False, default="Software Engineer")
    interview_type = Column(String(50), nullable=False, default="technical")
    difficulty = Column(String(50), nullable=False, default="medium")
    current_index = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False, default=0)
    questions_json = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="in_progress")
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

    answers = relationship(
        "InterviewQuestionAnswer",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class InterviewQuestionAnswer(Base):
    __tablename__ = "interview_question_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    user_answer = Column(Text, nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    evaluation_json = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    session = relationship("InterviewSession", back_populates="answers")