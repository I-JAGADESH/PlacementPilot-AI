from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests
from sqlalchemy.orm import Session

from app.github.models import GitHubAccount


GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_BASE = "https://api.github.com"

GITHUB_USER_SCOPE = "read:user user:email"


def _get_setting(name: str, default: str = "") -> str:
    try:
        from app.core.config import settings

        value = getattr(settings, name, None)
        if value:
            return str(value)
    except Exception:
        pass

    try:
        from app.config import settings

        value = getattr(settings, name, None)
        if value:
            return str(value)
    except Exception:
        pass

    import os

    return os.getenv(name, default)


def get_github_client_id() -> str:
    return _get_setting("GITHUB_CLIENT_ID")


def get_github_client_secret() -> str:
    return _get_setting("GITHUB_CLIENT_SECRET")


def get_github_redirect_uri() -> str:
    return _get_setting(
        "GITHUB_REDIRECT_URI",
        "http://127.0.0.1:8000/api/v1/github/callback",
    )


def build_authorization_url(state: str) -> str:
    params = {
        "client_id": get_github_client_id(),
        "redirect_uri": get_github_redirect_uri(),
        "scope": GITHUB_USER_SCOPE,
        "state": state,
    }

    return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> str:
    client_id = get_github_client_id()
    client_secret = get_github_client_secret()

    if not client_id:
        raise RuntimeError("GITHUB_CLIENT_ID is not configured.")

    if not client_secret:
        raise RuntimeError("GITHUB_CLIENT_SECRET is not configured.")

    response = requests.post(
        GITHUB_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": get_github_redirect_uri(),
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "PlacementPilot-AI",
        },
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    access_token = data.get("access_token")

    if not access_token:
        error = data.get("error", "unknown_error")
        description = data.get(
            "error_description",
            "GitHub did not return an access token.",
        )
        raise RuntimeError(f"GitHub OAuth error: {error} - {description}")

    return str(access_token)


def _github_headers(access_token: str) -> Dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PlacementPilot-AI",
    }


def get_github_profile(access_token: str) -> Dict[str, Any]:
    response = requests.get(
        f"{GITHUB_API_BASE}/user",
        headers=_github_headers(access_token),
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


def get_github_repositories(
    access_token: str,
    username: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params = {
        "per_page": 100,
        "sort": "updated",
        "direction": "desc",
    }

    if username:
        params["username"] = username

    response = requests.get(
        f"{GITHUB_API_BASE}/user/repos",
        headers=_github_headers(access_token),
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        return []

    return data


def calculate_repository_statistics(
    repositories: List[Dict[str, Any]],
) -> Dict[str, Any]:
    public_repositories = 0
    total_stars = 0
    total_forks = 0
    languages: Dict[str, int] = {}
    technologies: List[str] = []
    repository_summaries: List[Dict[str, Any]] = []

    for repo in repositories:
        if repo.get("private") is not True:
            public_repositories += 1

        total_stars += int(repo.get("stargazers_count") or 0)
        total_forks += int(repo.get("forks_count") or 0)

        language = repo.get("language")

        if language:
            languages[language] = languages.get(language, 0) + 1

            if language not in technologies:
                technologies.append(language)

        repository_summaries.append(
            {
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "html_url": repo.get("html_url"),
                "language": repo.get("language"),
                "stars": int(repo.get("stargazers_count") or 0),
                "forks": int(repo.get("forks_count") or 0),
                "topics": repo.get("topics") or [],
                "updated_at": repo.get("updated_at"),
                "created_at": repo.get("created_at"),
                "private": bool(repo.get("private")),
            }
        )

    return {
        "public_repositories": public_repositories,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "languages": languages,
        "technologies": sorted(technologies),
        "repositories": repository_summaries,
    }


def save_github_account(
    db: Session,
    user_id: int,
    access_token: str,
    profile: Dict[str, Any],
    statistics: Dict[str, Any],
) -> GitHubAccount:
    github_user_id = str(profile.get("id"))

    if not github_user_id or github_user_id == "None":
        raise RuntimeError("GitHub profile did not contain a user ID.")

    account = (
        db.query(GitHubAccount)
        .filter(GitHubAccount.user_id == user_id)
        .first()
    )

    if account is None:
        account = (
            db.query(GitHubAccount)
            .filter(
                GitHubAccount.github_user_id == github_user_id
            )
            .first()
        )

    if account is None:
        account = GitHubAccount(
            user_id=user_id,
            github_user_id=github_user_id,
            username=str(profile.get("login") or ""),
            access_token=access_token,
        )
        db.add(account)

    account.user_id = user_id
    account.github_user_id = github_user_id
    account.username = str(profile.get("login") or "")
    account.profile_url = profile.get("html_url")
    account.avatar_url = profile.get("avatar_url")
    account.access_token = access_token

    account.public_repositories = int(
        statistics.get("public_repositories", 0)
    )
    account.total_stars = int(statistics.get("total_stars", 0))
    account.total_forks = int(statistics.get("total_forks", 0))
    account.last_synced_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(account)

    return account


def sync_github_account(
    db: Session,
    account: GitHubAccount,
) -> Dict[str, Any]:
    profile = get_github_profile(account.access_token)

    repositories = get_github_repositories(
        account.access_token,
        profile.get("login"),
    )

    statistics = calculate_repository_statistics(repositories)

    account.username = str(profile.get("login") or account.username)
    account.profile_url = profile.get(
        "html_url",
        account.profile_url,
    )
    account.avatar_url = profile.get(
        "avatar_url",
        account.avatar_url,
    )
    account.public_repositories = int(
        statistics["public_repositories"]
    )
    account.total_stars = int(statistics["total_stars"])
    account.total_forks = int(statistics["total_forks"])
    account.last_synced_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(account)

    return {
        "profile": {
            "github_user_id": str(profile.get("id")),
            "username": profile.get("login"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "email": profile.get("email"),
            "profile_url": profile.get("html_url"),
            "avatar_url": profile.get("avatar_url"),
            "public_repositories": profile.get(
                "public_repos",
                statistics["public_repositories"],
            ),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
        },
        "statistics": statistics,
        "synced_at": account.last_synced_at.isoformat()
        if account.last_synced_at
        else None,
    }


def get_github_account(
    db: Session,
    user_id: int,
) -> Optional[GitHubAccount]:
    return (
        db.query(GitHubAccount)
        .filter(GitHubAccount.user_id == user_id)
        .first()
    )


def disconnect_github_account(
    db: Session,
    user_id: int,
) -> bool:
    account = get_github_account(db, user_id)

    if account is None:
        return False

    db.delete(account)
    db.commit()

    return True
