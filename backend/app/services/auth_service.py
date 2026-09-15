from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by email.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserRegister):
    """
    Register a new user.
    """

    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        return None

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),
        role="student",
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    """
    Authenticate a user.
    """

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user