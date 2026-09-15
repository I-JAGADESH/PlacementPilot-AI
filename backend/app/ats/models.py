from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func

from app.database.database import Base


class ATSResult(Base):
    __tablename__ = "ats_results"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    filename = Column(
        String(300),
        nullable=True,
    )

    job_description_provided = Column(
        Integer,
        nullable=False,
        default=0,
    )

    ats_score = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    matched_skills_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    missing_skills_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    sections_count = Column(
        Integer,
        nullable=False,
        default=0,
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