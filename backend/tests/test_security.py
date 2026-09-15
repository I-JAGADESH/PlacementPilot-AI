from datetime import datetime, timedelta, timezone
from jose import jwt
import pytest

from app.core.config import settings
from app.core.security import ALGORITHM


def test_missing_and_invalid_jwt(client):
    # 1. Missing Authorization header
    resp_no_token = client.get("/api/v1/profile")
    assert resp_no_token.status_code == 401

    # 2. Invalid JWT token
    headers_invalid = {"Authorization": "Bearer invalid.jwt.token"}
    resp_invalid = client.get("/api/v1/profile", headers=headers_invalid)
    assert resp_invalid.status_code == 401

    # 3. Expired JWT token
    expired_payload = {
        "sub": "usera@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    headers_expired = {"Authorization": f"Bearer {expired_token}"}

    resp_expired = client.get("/api/v1/profile", headers=headers_expired)
    assert resp_expired.status_code == 401


def test_github_token_redaction(client):
    # Register and login user
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "GitHub Security Test User",
            "email": "gh_user@example.com",
            "password": "Password123!",
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "gh_user@example.com",
            "password": "Password123!",
        },
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify /api/v1/github/status response does not contain access_token
    status_resp = client.get("/api/v1/github/status", headers=headers)
    assert status_resp.status_code == 200
    res_json = status_resp.json()
    assert "access_token" not in res_json
    assert "access_token" not in str(res_json)
