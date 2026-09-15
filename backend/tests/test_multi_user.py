import pytest


def get_auth_token(client, email, name="Test User"):
    # Register if not exists
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
    return resp.json()["access_token"]


def test_multi_user_data_isolation(client):
    token_a = get_auth_token(client, "usera@example.com", "User A")
    token_b = get_auth_token(client, "userb@example.com", "User B")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Profile Isolation
    # Create Profile for User A
    prof_a_resp = client.put(
        "/api/v1/profile",
        headers=headers_a,
        json={
            "cgpa": 9.2,
            "attendance": 95.0,
            "target_role": "Backend Engineer",
            "college": "Tech College A",
        },
    )
    assert prof_a_resp.status_code == 200

    # Create Profile for User B
    prof_b_resp = client.put(
        "/api/v1/profile",
        headers=headers_b,
        json={
            "cgpa": 7.5,
            "attendance": 80.0,
            "target_role": "Frontend Engineer",
            "college": "Tech College B",
        },
    )
    assert prof_b_resp.status_code == 200

    # Verify User A receives A's profile
    get_a_prof = client.get("/api/v1/profile", headers=headers_a).json()
    assert get_a_prof["target_role"] == "Backend Engineer"
    assert get_a_prof["college"] == "Tech College A"

    # Verify User B receives B's profile
    get_b_prof = client.get("/api/v1/profile", headers=headers_b).json()
    assert get_b_prof["target_role"] == "Frontend Engineer"
    assert get_b_prof["college"] == "Tech College B"

    # 2. Skills Isolation
    # Add Skill for A
    skill_a = client.post(
        "/api/v1/profile/skills",
        headers=headers_a,
        json={"name": "FastAPI", "category": "Backend", "proficiency": 90},
    ).json()

    # Add Skill for B
    skill_b = client.post(
        "/api/v1/profile/skills",
        headers=headers_b,
        json={"name": "React", "category": "Frontend", "proficiency": 85},
    ).json()

    # User A gets skills
    skills_a = client.get("/api/v1/profile/skills", headers=headers_a).json()
    assert len(skills_a) == 1
    assert skills_a[0]["name"] == "FastAPI"

    # User B gets skills
    skills_b = client.get("/api/v1/profile/skills", headers=headers_b).json()
    assert len(skills_b) == 1
    assert skills_b[0]["name"] == "React"

    # User B trying to edit User A's skill should be rejected (404/403)
    edit_skill_resp = client.put(
        f"/api/v1/profile/skills/{skill_a['id']}",
        headers=headers_b,
        json={"name": "Hacked", "category": "Hacked", "proficiency": 0},
    )
    assert edit_skill_resp.status_code == 404

    # User B trying to delete User A's skill should be rejected
    del_skill_resp = client.delete(
        f"/api/v1/profile/skills/{skill_a['id']}",
        headers=headers_b,
    )
    assert del_skill_resp.status_code == 404

    # 3. Projects & Certifications Isolation
    proj_a = client.post(
        "/api/v1/profile/projects",
        headers=headers_a,
        json={"title": "PlacementPilot Backend", "technologies": "Python, FastAPI"},
    ).json()

    proj_b = client.post(
        "/api/v1/profile/projects",
        headers=headers_b,
        json={"title": "UI Design System", "technologies": "React, CSS"},
    ).json()

    projs_a = client.get("/api/v1/profile/projects", headers=headers_a).json()
    assert len(projs_a) == 1
    assert projs_a[0]["title"] == "PlacementPilot Backend"

    projs_b = client.get("/api/v1/profile/projects", headers=headers_b).json()
    assert len(projs_b) == 1
    assert projs_b[0]["title"] == "UI Design System"

    del_proj_resp = client.delete(
        f"/api/v1/profile/projects/{proj_a['id']}",
        headers=headers_b,
    )
    assert del_proj_resp.status_code == 404

    # 4. Assessment History Isolation
    # Start assessment for A
    start_a = client.post(
        "/api/v1/assessment/start",
        headers=headers_a,
        json={"skill": "Python"},
    ).json()

    # User A assessment history
    hist_a = client.get("/api/v1/assessment/history", headers=headers_a).json()
    assert len(hist_a) == 1

    # User B assessment history should be empty
    hist_b = client.get("/api/v1/assessment/history", headers=headers_b).json()
    assert len(hist_b) == 0

    # User B submitting User A's assessment should fail
    sub_fail = client.post(
        "/api/v1/assessment/submit",
        headers=headers_b,
        json={"assessment_id": start_a["assessment_id"], "answers": []},
    )
    assert sub_fail.status_code == 404

    # 5. Interview Session & Summary Isolation
    int_start_a = client.post(
        "/api/v1/interview/start",
        headers=headers_a,
        json={
            "company": "Amazon",
            "job_description": "Software Engineer role requiring Python and Algorithms",
            "interview_type": "technical",
            "difficulty": "medium",
        },
    ).json()

    # User B attempting to get User A's interview summary should be forbidden (403/404)
    summary_b = client.get(
        f"/api/v1/interview/{int_start_a['interview_id']}/summary",
        headers=headers_b,
    )
    assert summary_b.status_code in (403, 404)

    # 6. Training Progress Isolation
    client.post(
        "/api/v1/training/complete",
        headers=headers_a,
        json={"skill": "Python", "topic": "Functions and Modules", "completed": True},
    )

    tr_a = client.get("/api/v1/training/Python", headers=headers_a).json()
    assert tr_a["completed_topics"] == 1

    tr_b = client.get("/api/v1/training/Python", headers=headers_b).json()
    assert tr_b["completed_topics"] == 0

    # 7. Placement Readiness Isolation
    read_a = client.get("/api/v1/readiness", headers=headers_a).json()
    read_b = client.get("/api/v1/readiness", headers=headers_b).json()

    assert read_a["target"]["role"] == "Backend Engineer"
    assert read_b["target"]["role"] == "Frontend Engineer"

    # 8. GitHub Connection Status Isolation
    gh_a = client.get("/api/v1/github/status", headers=headers_a).json()
    gh_b = client.get("/api/v1/github/status", headers=headers_b).json()

    assert gh_a["connected"] is False
    assert gh_b["connected"] is False
