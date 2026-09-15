from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database.database import Base


class GitHubAccount(Base):
    __tablename__ = "github_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)

    github_user_id = Column(String(100), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False)
    profile_url = Column(String(500), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    access_token = Column(Text, nullable=False)

    public_repositories = Column(Integer, nullable=False, default=0)
    total_stars = Column(Integer, nullable=False, default=0)
    total_forks = Column(Integer, nullable=False, default=0)

    last_synced_at = Column(DateTime(timezone=True), nullable=True)
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
