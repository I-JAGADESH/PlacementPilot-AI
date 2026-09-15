import pytest


def test_register_and_login(client):
    # 1. Register User A
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "User A",
            "email": "usera@example.com",
            "password": "Password123!",
        },
    )
    assert register_response.status_code == 201
    user_a = register_response.json()
    assert user_a["email"] == "usera@example.com"
    assert "id" in user_a

    # 2. Register Duplicate Email Error
    duplicate_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate User",
            "email": "usera@example.com",
            "password": "Password123!",
        },
    )
    assert duplicate_response.status_code == 400

    # 3. Login User A
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "usera@example.com",
            "password": "Password123!",
        },
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data

    # 4. Verify /me endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "usera@example.com"
    assert me_data["full_name"] == "User A"
