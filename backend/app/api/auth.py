from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
)
from app.database.database import get_db
from app.schemas.user import (
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    db_user = create_user(
        db,
        user,
    )

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return db_user


# ============================================================
# NORMAL JSON LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=Token,
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Normal application login.

    Accepts JSON:
    {
        "email": "...",
        "password": "..."
    }
    """

    authenticated_user = authenticate_user(
        db,
        user.email,
        user.password,
    )

    if authenticated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={
            "sub": authenticated_user.email,
            "role": authenticated_user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# OAUTH2 / SWAGGER LOGIN
# ============================================================

@router.post(
    "/token",
    response_model=Token,
)
def token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login endpoint.

    Swagger sends:
        username = user email
        password = user password
    """

    authenticated_user = authenticate_user(
        db,
        username,
        password,
    )

    if authenticated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token = create_access_token(
        data={
            "sub": authenticated_user.email,
            "role": authenticated_user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user=Depends(get_current_user),
):
    return current_user