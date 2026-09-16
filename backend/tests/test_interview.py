import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_auth_headers(email: str, name: str = "Test User"):
    # Register user (ignore 400 if already exists)
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": name,
            "email": email,
            "password": "Password123!",
        },
    )
    # Login
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!",
        },
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_interview_config():
    headers = get_auth_headers("user_config@example.com", "Config User")

    res = client.get("/api/v1/interview/config", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "roles" in data
    assert "Software Engineer" in data["roles"]
    assert "interview_rounds" in data
    assert len(data["interview_rounds"]) == 11
    assert "domains" in data
    assert len(data["domains"]) == 16


def test_interview_start_and_answer_flow():
    headers = get_auth_headers("user_flow@example.com", "Flow User")

    start_payload = {
        "company": "Amazon",
        "role": "Backend Developer",
        "experience_level": "Intermediate",
        "interview_round": "Technical MCQ",
        "difficulty": "Hard",
        "domain": "SQL",
    }

    res = client.post("/api/v1/interview/start", json=start_payload, headers=headers)
    assert res.status_code == 200
    s_data = res.json()

    interview_id = s_data["interview_id"]
    assert s_data["company"] == "Amazon"
    assert s_data["target_role"] == "Backend Developer"
    assert s_data["total_questions"] == 5
    assert s_data["first_question"] is not None
    q1 = s_data["first_question"]

    # Submit answer for Question 1
    answer_payload = {
        "interview_id": interview_id,
        "question_id": q1["question_id"],
        "answer": "A SQL Join combines rows from two or more tables based on a related column between them, such as INNER JOIN, LEFT JOIN, or FULL JOIN.",
    }

    ans_res = client.post("/api/v1/interview/answer", json=answer_payload, headers=headers)
    assert ans_res.status_code == 200
    a_data = ans_res.json()

    assert a_data["question_id"] == q1["question_id"]
    assert "evaluation" in a_data
    assert a_data["evaluation"]["score"] >= 0
    assert "technical_score" in a_data["evaluation"]
    assert "communication_score" in a_data["evaluation"]
    assert a_data["next_question"] is not None


def test_profile_aware_project_round():
    headers = get_auth_headers("proj_user@example.com", "Project User")

    # Update profile with project
    client.put(
        "/api/v1/profile",
        headers=headers,
        json={
            "target_role": "Backend Developer",
            "target_company": "Zoho",
        },
    )

    client.post(
        "/api/v1/profile/projects",
        headers=headers,
        json={
            "title": "Payment Gateway Engine",
            "description": "High throughput transaction processing using FastAPI and Redis",
            "technologies": "Python, FastAPI, Redis, PostgreSQL",
        },
    )

    start_payload = {
        "company": "Zoho",
        "role": "Backend Developer",
        "experience_level": "Entry Level",
        "interview_round": "Project Discussion",
        "difficulty": "Medium",
    }

    res = client.post("/api/v1/interview/start", json=start_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    q1 = data["first_question"]
    assert "Payment Gateway Engine" in q1["question"]
    assert "FastAPI" in q1["question"]


def test_full_interview_completion_and_summary():
    headers = get_auth_headers("summary_user@example.com", "Summary User")

    res = client.post(
        "/api/v1/interview/start",
        json={
            "company": "Microsoft",
            "role": "SDE",
            "experience_level": "Entry Level",
            "interview_round": "DSA",
            "difficulty": "Medium",
            "domain": "DSA",
        },
        headers=headers,
    )
    interview_id = res.json()["interview_id"]

    for i in range(1, 6):
        client.post(
            "/api/v1/interview/answer",
            json={
                "interview_id": interview_id,
                "question_id": i,
                "answer": f"Detailed algorithmic explanation for question {i} utilizing hash map data structures for optimal O(N) execution time.",
            },
            headers=headers,
        )

    sum_res = client.get(f"/api/v1/interview/{interview_id}/summary", headers=headers)
    assert sum_res.status_code == 200
    s_data = sum_res.json()

    assert s_data["completed"] is True
    assert s_data["completed_questions"] == 5
    assert s_data["average_score"] > 0
    assert len(s_data["preparation_roadmap"]) > 0
    assert "next_recommended_difficulty" in s_data


def test_multi_user_isolation():
    headers_a = get_auth_headers("usera_inv@example.com", "User A")
    headers_b = get_auth_headers("userb_inv@example.com", "User B")

    # User A starts interview
    res_a = client.post(
        "/api/v1/interview/start",
        json={"company": "TCS", "role": "Software Engineer", "interview_round": "HR / Behavioral"},
        headers=headers_a,
    )
    interview_id_a = res_a.json()["interview_id"]

    # User B attempts to access User A's interview session -> 403 Forbidden
    access_res = client.get(f"/api/v1/interview/{interview_id_a}", headers=headers_b)
    assert access_res.status_code == 403

    # User B attempts to submit answer to User A's interview -> 403 Forbidden
    ans_res = client.post(
        "/api/v1/interview/answer",
        json={"interview_id": interview_id_a, "question_id": 1, "answer": "Malicious attempt"},
        headers=headers_b,
    )
    assert ans_res.status_code == 403

    # User B attempts to view User A's summary -> 403 Forbidden
    sum_res = client.get(f"/api/v1/interview/{interview_id_a}/summary", headers=headers_b)
    assert sum_res.status_code == 403
