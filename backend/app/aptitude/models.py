"""
SQLAlchemy Database Models for Aptitude Preparation Engine (Phase 2).
Preserves Phase 1 CASCADE Foreign Keys and User Isolation.
"""

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


class AptitudeDomain(Base):
    __tablename__ = "aptitude_domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True, index=True)
    slug = Column(String(150), nullable=False, unique=True, index=True)

    topics = relationship(
        "AptitudeTopic", back_populates="domain", cascade="all, delete-orphan"
    )


class AptitudeTopic(Base):
    __tablename__ = "aptitude_topics"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(
        Integer,
        ForeignKey("aptitude_domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(150), nullable=False, index=True)
    slug = Column(String(150), nullable=False, unique=True, index=True)

    domain = relationship("AptitudeDomain", back_populates="topics")
    subtopics = relationship(
        "AptitudeSubtopic", back_populates="topic", cascade="all, delete-orphan"
    )


class AptitudeSubtopic(Base):
    __tablename__ = "aptitude_subtopics"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(
        Integer,
        ForeignKey("aptitude_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(150), nullable=False, index=True)
    slug = Column(String(150), nullable=False, unique=True, index=True)

    topic = relationship("AptitudeTopic", back_populates="subtopics")
    questions = relationship(
        "AptitudeQuestion", back_populates="subtopic", cascade="all, delete-orphan"
    )


class DIDataset(Base):
    __tablename__ = "di_datasets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    dataset_type = Column(String(50), nullable=False, default="table")  # table, chart, mixed
    content_json = Column(Text, nullable=False)

    questions = relationship("AptitudeQuestion", back_populates="di_dataset")


class AptitudeQuestion(Base):
    __tablename__ = "aptitude_questions"

    id = Column(Integer, primary_key=True, index=True)
    subtopic_id = Column(
        Integer,
        ForeignKey("aptitude_subtopics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    di_dataset_id = Column(
        Integer,
        ForeignKey("di_datasets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    difficulty = Column(String(50), nullable=False, default="Medium")  # Easy, Medium, Hard, Expert
    question_type = Column(String(50), nullable=False, default="MCQ")  # MCQ, Numerical, Data Interpretation, Multi-step Reasoning
    question_text = Column(Text, nullable=False)
    correct_answer = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    formula_concept = Column(Text, nullable=True)

    estimated_time_seconds = Column(Integer, nullable=False, default=60)
    negative_marking = Column(Float, nullable=False, default=0.0)

    tags_json = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False, default="static")  # static, generated
    company_relevance_json = Column(Text, nullable=True)
    generation_strategy = Column(String(100), nullable=True)
    is_generated = Column(Boolean, nullable=False, default=False)
    seed = Column(Integer, nullable=True)
    validation_status = Column(String(50), nullable=False, default="VALIDATED")

    subtopic = relationship("AptitudeSubtopic", back_populates="questions")
    di_dataset = relationship("DIDataset", back_populates="questions")
    options = relationship(
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(
        Integer,
        ForeignKey("aptitude_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_key = Column(String(10), nullable=False)  # A, B, C, D
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)

    question = relationship("AptitudeQuestion", back_populates="options")


class CompanyPattern(Base):
    __tablename__ = "company_patterns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    slug = Column(String(150), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    total_questions = Column(Integer, nullable=False, default=30)
    duration_minutes = Column(Integer, nullable=False, default=30)
    negative_marking = Column(Float, nullable=False, default=0.25)
    sections_config_json = Column(Text, nullable=False)
    topic_distribution_json = Column(Text, nullable=False)


class AptitudeAssessment(Base):
    __tablename__ = "aptitude_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    mode = Column(String(50), nullable=False, index=True)  # Practice, Retry, Topic, Weak, Mock, Placement, Company
    title = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="IN_PROGRESS", index=True)  # IN_PROGRESS, COMPLETED, EXPIRED
    company_pattern_slug = Column(String(150), nullable=True)

    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=False, default=1800)

    total_questions = Column(Integer, nullable=False, default=0)
    attempted_questions = Column(Integer, nullable=False, default=0)
    correct_answers = Column(Integer, nullable=False, default=0)
    incorrect_answers = Column(Integer, nullable=False, default=0)
    skipped_answers = Column(Integer, nullable=False, default=0)

    raw_score = Column(Float, nullable=False, default=0.0)
    score_percentage = Column(Float, nullable=False, default=0.0)
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    avg_time_per_question = Column(Float, nullable=False, default=0.0)
    accuracy_percentage = Column(Float, nullable=False, default=0.0)
    speed_qpm = Column(Float, nullable=False, default=0.0)

    domain_performance_json = Column(Text, nullable=True)
    topic_performance_json = Column(Text, nullable=True)
    subtopic_performance_json = Column(Text, nullable=True)
    difficulty_performance_json = Column(Text, nullable=True)
    question_type_performance_json = Column(Text, nullable=True)

    sections = relationship(
        "AssessmentSection", back_populates="assessment", cascade="all, delete-orphan"
    )
    question_maps = relationship(
        "AssessmentQuestionMap", back_populates="assessment", cascade="all, delete-orphan"
    )
    answers = relationship(
        "AssessmentAnswer", back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentSection(Base):
    __tablename__ = "assessment_sections"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("aptitude_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(150), nullable=False)
    domain_id = Column(
        Integer,
        ForeignKey("aptitude_domains.id", ondelete="SET NULL"),
        nullable=True,
    )
    duration_seconds = Column(Integer, nullable=False, default=600)
    section_order = Column(Integer, nullable=False, default=1)

    assessment = relationship("AptitudeAssessment", back_populates="sections")


class AssessmentQuestionMap(Base):
    __tablename__ = "assessment_question_maps"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("aptitude_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_id = Column(
        Integer,
        ForeignKey("assessment_sections.id", ondelete="CASCADE"),
        nullable=True,
    )
    question_id = Column(
        Integer,
        ForeignKey("aptitude_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_order = Column(Integer, nullable=False)
    options_order_json = Column(Text, nullable=True)  # JSON list of randomized option keys or objects
    seed = Column(Integer, nullable=True)

    assessment = relationship("AptitudeAssessment", back_populates="question_maps")
    question = relationship("AptitudeQuestion")


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(
        Integer,
        ForeignKey("aptitude_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        Integer,
        ForeignKey("aptitude_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option_or_text = Column(String(255), nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    score_delta = Column(Float, nullable=False, default=0.0)

    assessment = relationship("AptitudeAssessment", back_populates="answers")
    question = relationship("AptitudeQuestion")


class PerformanceSnapshot(Base):
    __tablename__ = "performance_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain_id = Column(
        Integer,
        ForeignKey("aptitude_domains.id", ondelete="CASCADE"),
        nullable=False,
    )
    subtopic_id = Column(
        Integer,
        ForeignKey("aptitude_subtopics.id", ondelete="CASCADE"),
        nullable=True,
    )

    total_attempted = Column(Integer, nullable=False, default=0)
    total_correct = Column(Integer, nullable=False, default=0)
    accuracy = Column(Float, nullable=False, default=0.0)
    avg_speed_seconds = Column(Float, nullable=False, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
