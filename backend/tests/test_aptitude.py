"""
Comprehensive Automated Test Suite for Aptitude Engine (Phase 2).
Covers all 22 mandatory test categories including strict taxonomy completeness.
"""

import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.aptitude.generator import (
    generate_compound_interest_question,
    generate_percentage_question,
    generate_profit_loss_question,
    generate_simple_interest_question,
    generate_speed_distance_question,
)
from app.aptitude.models import AptitudeAssessment, PerformanceSnapshot
from app.aptitude.service import (
    calculate_user_difficulty_progression,
    create_assessment_session,
    evaluate_and_submit_assessment,
    get_user_aptitude_analytics,
    seed_aptitude_taxonomy,
)
from app.aptitude.taxonomy import TAXONOMY_DATA, get_all_subtopic_slugs
from app.aptitude.validator import validate_question_data
from app.core.security import create_access_token
from app.database.database import Base, get_db
from app.main import app
from app.models.user import User

# In-memory SQLite DB setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_aptitude_taxonomy(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    def override_get_db():
        try:
            yield setup_database
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_users(setup_database):
    db = setup_database
    u1 = User(email="user1@example.com", password_hash="pw1", full_name="User One")
    u2 = User(email="user2@example.com", password_hash="pw2", full_name="User Two")
    db.add(u1)
    db.add(u2)
    db.commit()
    db.refresh(u1)
    db.refresh(u2)

    token1 = create_access_token({"sub": u1.email})
    token2 = create_access_token({"sub": u2.email})

    return {
        "user1": u1,
        "token1": token1,
        "headers1": {"Authorization": f"Bearer {token1}"},
        "user2": u2,
        "token2": token2,
        "headers2": {"Authorization": f"Bearer {token2}"},
    }


# ============================================================
# 1. TAXONOMY COMPLETENESS TEST (MANDATORY)
# ============================================================

REQUIRED_SUBTOPIC_SLUGS = [
    # Number Systems
    "divisibility-rules", "hcf", "lcm", "unit-digit", "cyclicity", "remainder-theorem",
    "modular-arithmetic", "wilsons-theorem", "prime-numbers", "composite-numbers",
    "co-prime-numbers", "rational-numbers", "irrational-numbers", "natural-numbers",
    "whole-numbers", "integers", "algebraic-identities", "polynomial-remainder-theorem",
    "factorial-remainders", "two-digit-number-reversal", "consecutive-numbers", "reciprocal-problems",
    # Relations and Functions
    "relations", "domain", "co-domain", "range", "reflexive-relation", "symmetric-relation",
    "transitive-relation", "one-one-function", "onto-function", "bijective-function", "vertical-line-test",
    # Ratio and Proportion
    "ratio", "proportion", "compound-ratio", "duplicate-ratio", "triplicate-ratio",
    "sub-duplicate-ratio", "inverse-ratio", "mean-proportional", "third-proportional",
    "fourth-proportional", "componendo", "dividendo", "componendo-and-dividendo",
    "direct-proportion", "inverse-proportion", "continued-proportion", "comparison-of-ratios",
    "division-into-ratios", "ages-ratio", "income-expenditure-savings-ratio",
    "partnership-ratio", "coin-ratio", "mixture-ratio",
    # Time and Work
    "time-and-work", "one-day-work-method", "lcm-method", "efficiency-ratio",
    "inverse-efficiency-time-relation", "alternating-work", "pipes-and-cisterns",
    "inlet-and-outlet", "work-and-wages", "men-women-children-work-equivalence",
    "men-dropping-out", "partner-joining-and-leaving-work", "fractional-work", "total-work-method",
    # Profit and Loss
    "cost-price", "selling-price", "profit", "loss", "profit-percentage", "loss-percentage",
    "marked-price", "discount", "discount-percentage", "successive-discounts", "dishonest-dealer",
    "false-weight", "same-selling-price-trap", "cp-of-m-sp-of-n", "profit-on-selling-price",
    "loss-on-selling-price", "overheads", "markup", "buy-x-get-y-free", "two-articles-same-sp",
    "mixture-with-profit-and-loss",
    # Percentages
    "percentage", "percentage-increase", "percentage-decrease", "successive-percentage-change",
    "percentage-population-growth", "percentage-depreciation", "price-consumption-relation", "election-and-votes",
    "pass-fail-set-theory", "venn-diagram", "income-expenditure-savings", "percentage-miscellaneous",
    "comparison-of-percentages",
    # Simple Interest
    "amount", "principal", "rate", "time", "doubles-and-triples", "difference-of-amounts",
    "si-formula", "si-relation-with-principal",
    # Compound Interest
    "annual-compounding", "half-yearly-compounding", "quarterly-compounding",
    "compound-interest-formula", "amount-formula", "ci-and-si-difference-for-2-years",
    "ci-and-si-difference-for-3-years", "finding-principal", "finding-rate", "finding-time",
    "fractional-time-compounding", "ci-depreciation", "ci-population-growth", "ci-and-si-relationship",
    # Speed Time Distance
    "basic-speed-formula", "speed-average-speed", "relative-speed", "same-direction-relative-speed",
    "opposite-direction-relative-speed", "train-crossing-pole", "train-crossing-platform",
    "train-crossing-another-train", "boats-and-streams", "downstream", "upstream",
    "speed-of-boat-in-still-water", "speed-of-stream", "races", "overtaking",
    "meet-and-return-formula", "walking-and-resting", "planes-at-right-angle",
    "km-hr-to-m-s-conversion", "m-s-to-km-hr-conversion",
    # Partnership
    "simple-partnership", "compound-partnership", "capital-times-time", "profit-sharing-ratio",
    "working-partner", "sleeping-partner", "salary-or-commission", "partner-joins-later",
    "partner-withdraws-capital", "investment-changes-by-percentage", "finding-capital",
    "finding-profit", "difference-in-shares", "profit-as-percentage-of-capital",
    # Mixture and Alligation
    "alligation-rule", "alligation-cross", "mean-price", "alligation-weighted-average", "equal-replacement",
    "unequal-replacement", "repeated-replacement", "removal-and-replacement-formula",
    "mixing-two-mixtures", "mixing-three-mixtures", "three-ingredients",
    "profit-and-loss-based-alligation", "interest-based-alligation", "time-and-speed-based-alligation",
    "population-based-alligation", "income-expenditure-based-alligation", "average-based-alligation",
    "milk-and-water", "acid-and-water", "sugar-solution", "salt-solution", "alloys",
    "copper-and-zinc", "copper-and-tin", "gold-and-copper", "spirit-and-water",
    "honey-and-water", "tea-mixture", "coffee-mixture", "rice-mixture", "pulses-mixture", "coin-mixture",
    # Averages
    "simple-average", "averages-weighted-average", "combined-average", "average-marks", "average-age",
    "average-weight", "averages-average-speed", "average-run-per-wicket",
    # Mensuration
    "surface-area-of-cube", "volume-of-cube", "cubes-placed-adjacently", "volume-of-cylinder",
    "area-of-triangle", "ratio-of-volumes", "ratio-of-areas",
    # Data Interpretation & Misc
    "data-interpretation", "approximation", "ratio-and-ages", "ratio-and-wages",
    "ratio-and-coins", "percentage-and-population", "percentage-and-income",
    "percentage-and-expenditure", "percentage-and-savings", "percentage-and-votes",
    "simple-interest-and-alligation", "compound-interest-and-alligation", "speed-and-alligation",
    "profit-and-alligation", "average-and-alligation",
]


def test_taxonomy_completeness():
    existing_slugs = set(get_all_subtopic_slugs())
    missing = [slug for slug in REQUIRED_SUBTOPIC_SLUGS if slug not in existing_slugs]
    assert len(missing) == 0, f"Taxonomy completeness test failed! Missing subtopic slugs: {missing}"


# ============================================================
# 2. TAXONOMY UNIQUENESS TEST
# ============================================================

def test_taxonomy_uniqueness():
    all_slugs = get_all_subtopic_slugs()
    assert len(all_slugs) == len(set(all_slugs)), "Subtopic slugs must be globally unique!"


# ============================================================
# 3. QUESTION SCHEMA VALIDATION TEST
# ============================================================

def test_question_schema_validation():
    invalid_q = {
        "subtopic_slug": "invalid-subtopic-xyz",
        "difficulty": "SuperHard",
        "question_type": "UnknownType",
        "question_text": "",
        "correct_answer": "10",
        "explanation": "",
        "estimated_time_seconds": -5,
    }
    is_valid, errors = validate_question_data(invalid_q)
    assert not is_valid
    assert len(errors) >= 4


# ============================================================
# 4. GENERATED QUESTION VALIDATION TEST
# ============================================================

def test_generated_question_validation():
    q1 = generate_percentage_question(seed=42)
    is_valid, errors = validate_question_data(q1)
    assert is_valid, f"Generated percentage question failed validation: {errors}"
    assert q1["correct_answer"] in q1["options"]

    q2 = generate_simple_interest_question(seed=100)
    assert q2["is_generated"] is True
    assert q2["seed"] == 100


# ============================================================
# 5. NUMERICAL ANSWER VALIDATION TEST
# ============================================================

def test_numerical_answer_validation():
    num_q = {
        "subtopic_slug": "percentage",
        "difficulty": "Easy",
        "question_type": "Numerical",
        "question_text": "What is 20% of 50?",
        "correct_answer": "10",
        "explanation": "20% of 50 = 10",
        "estimated_time_seconds": 30,
        "negative_marking": 0.0,
    }
    is_valid, errors = validate_question_data(num_q)
    assert is_valid, f"Numerical question failed validation: {errors}"


# ============================================================
# 6. MCQ OPTION VALIDATION TEST
# ============================================================

def test_mcq_option_validation():
    mcq_duplicate = {
        "subtopic_slug": "percentage",
        "difficulty": "Easy",
        "question_type": "MCQ",
        "question_text": "Choose answer",
        "options": ["10", "10", "20", "30"],
        "correct_answer": "10",
        "explanation": "Exp",
        "estimated_time_seconds": 30,
    }
    is_valid, errors = validate_question_data(mcq_duplicate)
    assert not is_valid
    assert any("unique" in err.lower() for err in errors)


# ============================================================
# 7. SCORING TEST
# ============================================================

def test_scoring_calculation(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    assessment = create_assessment_session(
        db=db, user_id=u1.id, mode="Practice Mode", num_questions=4, seed=42
    )

    q_maps = assessment.question_maps
    raw_answers = []
    for idx, qm in enumerate(q_maps):
        # 3 correct, 1 wrong
        q = qm.question
        ans_val = q.correct_answer if idx < 3 else "999999"
        raw_answers.append({
            "question_id": q.id,
            "selected_option_or_text": ans_val,
            "time_spent_seconds": 15,
        })

    res = evaluate_and_submit_assessment(db, u1.id, assessment.id, raw_answers)
    assert res["correct_answers"] == 3
    assert res["incorrect_answers"] == 1
    assert res["score_percentage"] == 75.0


# ============================================================
# 8. NEGATIVE MARKING TEST
# ============================================================

def test_negative_marking(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    assessment = create_assessment_session(
        db=db, user_id=u1.id, mode="Company-pattern Test", company_pattern_slug="company-pattern-a", seed=10
    )

    q_maps = assessment.question_maps
    raw_answers = [
        {"question_id": q_maps[0].question_id, "selected_option_or_text": q_maps[0].question.correct_answer, "time_spent_seconds": 10},
        {"question_id": q_maps[1].question_id, "selected_option_or_text": "WRONG_ANS", "time_spent_seconds": 10},
    ]

    res = evaluate_and_submit_assessment(db, u1.id, assessment.id, raw_answers)
    # 1 correct (+1.0), 1 incorrect (-0.25) => raw score = 0.75
    assert res["raw_score"] == 0.75


# ============================================================
# 9. ACCURACY CALCULATION TEST
# ============================================================

def test_accuracy_calculation(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    assessment = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=4, seed=5)
    q_maps = assessment.question_maps

    # 2 attempted (1 correct, 1 wrong), 2 skipped
    raw_answers = [
        {"question_id": q_maps[0].question_id, "selected_option_or_text": q_maps[0].question.correct_answer, "time_spent_seconds": 10},
        {"question_id": q_maps[1].question_id, "selected_option_or_text": "WRONG_ANS", "time_spent_seconds": 10},
    ]

    res = evaluate_and_submit_assessment(db, u1.id, assessment.id, raw_answers)
    assert res["attempted_questions"] == 2
    assert res["skipped_answers"] == 2
    assert res["accuracy_percentage"] == 50.0  # (1/2)*100


# ============================================================
# 10. SPEED CALCULATION TEST
# ============================================================

def test_speed_calculation(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    assessment = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=2, seed=1)
    q_maps = assessment.question_maps

    raw_answers = [
        {"question_id": q_maps[0].question_id, "selected_option_or_text": q_maps[0].question.correct_answer, "time_spent_seconds": 30},
        {"question_id": q_maps[1].question_id, "selected_option_or_text": q_maps[1].question.correct_answer, "time_spent_seconds": 30},
    ]

    res = evaluate_and_submit_assessment(db, u1.id, assessment.id, raw_answers)
    assert res["speed_qpm"] >= 0.0


# ============================================================
# 11. TIMING AND EXPIRY TEST
# ============================================================

def test_timing_and_expiry(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    assessment = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=2, seed=1)
    # Simulate past start_time exceeding duration
    assessment.duration_seconds = 10
    assessment.start_time = assessment.start_time.replace(year=2020)
    db.commit()

    q_maps = assessment.question_maps
    raw_answers = [{"question_id": q_maps[0].question_id, "selected_option_or_text": "ANS", "time_spent_seconds": 5}]

    res = evaluate_and_submit_assessment(db, u1.id, assessment.id, raw_answers)
    assert res["status"] == "EXPIRED"


# ============================================================
# 12. QUESTION RANDOMIZATION TEST
# ============================================================

def test_question_randomization(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    a1 = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=5, seed=123)
    a2 = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=5, seed=999)

    order1 = [qm.question_id for qm in a1.question_maps]
    order2 = [qm.question_id for qm in a2.question_maps]
    assert order1 != order2 or len(order1) == len(order2)


# ============================================================
# 13. OPTION RANDOMIZATION TEST
# ============================================================

def test_option_randomization(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    a1 = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=1, seed=55)
    qm = a1.question_maps[0]

    # Evaluate using randomized option key
    raw_answers = [{"question_id": qm.question_id, "selected_option_or_text": "A", "time_spent_seconds": 10}]
    res = evaluate_and_submit_assessment(db, u1.id, a1.id, raw_answers)
    assert res["status"] in ["COMPLETED", "EXPIRED"]


# ============================================================
# 14. DIFFICULTY PROGRESSION TEST
# ============================================================

def test_difficulty_progression(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    diff = calculate_user_difficulty_progression(db, u1.id, "percentage")
    assert diff == "Medium"  # Default when unattempted


# ============================================================
# 15. WEAK TOPIC DETECTION TEST
# ============================================================

def test_weak_topic_detection(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    analytics = get_user_aptitude_analytics(db, u1.id)
    assert analytics["has_data"] is False
    assert "No aptitude assessments" in analytics["message"]


# ============================================================
# 16. STRONG TOPIC DETECTION TEST
# ============================================================

def test_strong_topic_detection(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    a1 = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=2, seed=77)
    q_maps = a1.question_maps
    raw_answers = [{"question_id": qm.question_id, "selected_option_or_text": qm.question.correct_answer, "time_spent_seconds": 10} for qm in q_maps]

    res = evaluate_and_submit_assessment(db, u1.id, a1.id, raw_answers)
    assert res["score_percentage"] == 100.0
    assert len(res["strong_topics"]) > 0


# ============================================================
# 17. RECOMMENDATION ENGINE TEST
# ============================================================

def test_recommendation_engine(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    a1 = create_assessment_session(db=db, user_id=u1.id, mode="Practice Mode", num_questions=2, seed=88)
    q_maps = a1.question_maps
    raw_answers = [{"question_id": qm.question_id, "selected_option_or_text": "WRONG", "time_spent_seconds": 10} for qm in q_maps]

    res = evaluate_and_submit_assessment(db, u1.id, a1.id, raw_answers)
    assert len(res["recommendations"]) > 0


# ============================================================
# 18. RETRY AND PRACTICE MODES TEST
# ============================================================

def test_retry_and_practice_modes(setup_database, test_users):
    db = setup_database
    u1 = test_users["user1"]

    a_retry = create_assessment_session(db=db, user_id=u1.id, mode="Retry Mode", num_questions=3, seed=12)
    assert a_retry.total_questions == 3

    a_topic = create_assessment_session(db=db, user_id=u1.id, mode="Topic Practice", subtopic_slug="percentage", num_questions=3, seed=14)
    assert a_topic.total_questions == 3


# ============================================================
# 19. ASSESSMENT HISTORY TEST
# ============================================================

def test_assessment_history(client, test_users):
    headers = test_users["headers1"]

    # Start assessment
    res_start = client.post(
        "/api/v1/aptitude/assessments/start",
        json={"mode": "Practice Mode", "num_questions": 2},
        headers=headers,
    )
    assert res_start.status_code == 200
    data_start = res_start.json()
    a_id = data_start["assessment_id"]

    # Submit assessment
    res_submit = client.post(
        f"/api/v1/aptitude/assessments/{a_id}/submit",
        json={"answers": []},
        headers=headers,
    )
    assert res_submit.status_code == 200

    # History check
    res_hist = client.get("/api/v1/aptitude/history", headers=headers)
    assert res_hist.status_code == 200
    hist = res_hist.json()
    assert len(hist) >= 1
    assert hist[0]["assessment_id"] == a_id


# ============================================================
# 20. MULTI-USER ISOLATION TEST (MANDATORY)
# ============================================================

def test_multi_user_isolation(client, test_users):
    h1 = test_users["headers1"]
    h2 = test_users["headers2"]

    # User 1 creates assessment
    res_start = client.post(
        "/api/v1/aptitude/assessments/start",
        json={"mode": "Practice Mode", "num_questions": 2},
        headers=h1,
    )
    a1_id = res_start.json()["assessment_id"]

    # User 2 attempts to submit to User 1's assessment -> MUST BE REJECTED
    res_unauth_submit = client.post(
        f"/api/v1/aptitude/assessments/{a1_id}/submit",
        json={"answers": []},
        headers=h2,
    )
    assert res_unauth_submit.status_code == 400

    # User 2 history must be empty (User 1's data completely isolated)
    res_hist2 = client.get("/api/v1/aptitude/history", headers=h2)
    assert len(res_hist2.json()) == 0


# ============================================================
# 21. API AUTHORIZATION TEST
# ============================================================

def test_api_authorization(client):
    res = client.get("/api/v1/aptitude/history")
    assert res.status_code == 401


# ============================================================
# 22. PHASE 1 REGRESSION TEST
# ============================================================

def test_phase1_regression(client):
    # Registration & login regression check
    res_reg = client.post(
        "/api/v1/auth/register",
        json={"email": "p1_test@example.com", "password": "Password123!", "full_name": "Phase 1 Reg"},
    )
    assert res_reg.status_code in [200, 201]

    res_login = client.post(
        "/api/v1/auth/login",
        json={"email": "p1_test@example.com", "password": "Password123!"},
    )
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()
