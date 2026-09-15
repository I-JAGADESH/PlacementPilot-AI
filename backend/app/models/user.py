from sqlalchemy import Column, Integer, String, DateTime
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

    def __repr__(self):
        return (
            f"<User(id={self.id}, "
            f"name='{self.full_name}', "
            f"email='{self.email}', "
            f"role='{self.role}')>"
        )