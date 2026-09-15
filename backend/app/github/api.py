from __future__ import annotations

import secrets
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.github.service import (
    build_authorization_url,
    calculate_repository_statistics,
    disconnect_github_account,
    exchange_code_for_token,
    get_github_account,
    get_github_profile,
    get_github_repositories,
    save_github_account,
    sync_github_account,
)


router = APIRouter(
    prefix="/api/v1/github",
    tags=["GitHub Integration"],
)


# Temporary OAuth state storage for local development.
# The state is tied to the authenticated PlacementPilot user.
OAUTH_STATES: Dict[str, int] = {}


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def _get_user_id(current_user: Any) -> int:
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    if isinstance(current_user, dict):
        user_id = current_user.get("id") or current_user.get("user_id")
    else:
        user_id = getattr(
            current_user,
            "id",
            None,
        ) or getattr(
            current_user,
            "user_id",
            None,
        )

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Unable to determine authenticated user.",
        )

    return int(user_id)


def _get_current_user_dependency():
    """
    Resolve the project's existing authentication dependency.

    The project already exposes get_current_user through the auth API.
    Importing it here keeps GitHub protected by the same JWT system.
    """
    try:
        from app.api.auth import get_current_user

        return get_current_user
    except ImportError:
        try:
            from app.auth.dependencies import get_current_user

            return get_current_user
        except ImportError:
            return None


_current_user_dependency = _get_current_user_dependency()


def require_current_user():
    if _current_user_dependency is None:
        raise HTTPException(
            status_code=500,
            detail="Authentication dependency could not be loaded.",
        )

    return _current_user_dependency


@router.get("/connect")
def connect_github(
    current_user: Any = Depends(require_current_user()),
):
    """
    Start GitHub OAuth authorization.
    """
    user_id = _get_user_id(current_user)

    state = secrets.token_urlsafe(32)
    OAUTH_STATES[state] = user_id

    authorization_url = build_authorization_url(state)

    return {
        "authorization_url": authorization_url,
        "message": "Open authorization_url to connect your GitHub account.",
    }


@router.get("/callback")
def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    GitHub OAuth callback.

    GitHub redirects the browser here after authorization.
    """
    user_id = OAUTH_STATES.pop(state, None)

    if user_id is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state.",
        )

    try:
        access_token = exchange_code_for_token(code)

        profile = get_github_profile(access_token)

        repositories = get_github_repositories(
            access_token,
            profile.get("login"),
        )

        statistics = calculate_repository_statistics(
            repositories
        )

        account = save_github_account(
            db=db,
            user_id=user_id,
            access_token=access_token,
            profile=profile,
            statistics=statistics,
        )

        return {
            "success": True,
            "message": "GitHub account connected successfully.",
            "github": {
                "id": account.github_user_id,
                "username": account.username,
                "profile_url": account.profile_url,
                "avatar_url": account.avatar_url,
                "public_repositories": account.public_repositories,
                "total_stars": account.total_stars,
                "total_forks": account.total_forks,
            },
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub connection failed: {str(exc)}",
        )


@router.post("/sync")
def sync_github(
    current_user: Any = Depends(require_current_user()),
    db: Session = Depends(get_db),
):
    """
    Re-fetch GitHub profile and repository information.
    """
    user_id = _get_user_id(current_user)

    account = get_github_account(
        db=db,
        user_id=user_id,
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="GitHub account is not connected.",
        )

    try:
        result = sync_github_account(
            db=db,
            account=account,
        )

        return {
            "success": True,
            "message": "GitHub data synchronized successfully.",
            **result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub synchronization failed: {str(exc)}",
        )


@router.get("/status")
def github_status(
    current_user: Any = Depends(require_current_user()),
    db: Session = Depends(get_db),
):
    """
    Return the current GitHub connection status.
    """
    user_id = _get_user_id(current_user)

    account = get_github_account(
        db=db,
        user_id=user_id,
    )

    if account is None:
        return {
            "connected": False,
            "github": None,
        }

    return {
        "connected": True,
        "github": {
            "id": account.github_user_id,
            "username": account.username,
            "profile_url": account.profile_url,
            "avatar_url": account.avatar_url,
            "public_repositories": account.public_repositories,
            "total_stars": account.total_stars,
            "total_forks": account.total_forks,
            "last_synced_at": (
                account.last_synced_at.isoformat()
                if account.last_synced_at
                else None
            ),
        },
    }


@router.delete("/disconnect")
def github_disconnect(
    current_user: Any = Depends(require_current_user()),
    db: Session = Depends(get_db),
):
    """
    Disconnect the user's GitHub account.
    """
    user_id = _get_user_id(current_user)

    disconnected = disconnect_github_account(
        db=db,
        user_id=user_id,
    )

    if not disconnected:
        raise HTTPException(
            status_code=404,
            detail="GitHub account is not connected.",
        )

    return {
        "success": True,
        "message": "GitHub account disconnected successfully.",
    }
