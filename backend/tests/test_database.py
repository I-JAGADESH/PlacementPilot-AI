import pytest
from app.models.user import User
from app.profile.models import StudentProfile, StudentSkill
from app.assessment.models import AssessmentAttempt
from app.interview.models import InterviewResult, InterviewSession
from app.ats.models import ATSResult
from app.training.models import TrainingProgress
from app.github.models import GitHubAccount, OAuthState
from app.core.security import hash_password


def test_user_cascading_deletes(db_session):
    # 1. Create a user with bcrypt hashed password
    user = User(
        full_name="Delete Test User",
        email="delete_user@example.com",
        password_hash=hash_password("Password123!"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id

    # 2. Add profile & skill
    profile = StudentProfile(user_id=user_id, target_role="Tester")
    db_session.add(profile)
    db_session.commit()

    skill = StudentSkill(profile_id=profile.id, name="Python", proficiency=80.0)
    db_session.add(skill)

    # 3. Add assessment attempt
    attempt = AssessmentAttempt(user_id=user_id, skill="Python", total_questions=5, performance_level="Strong")
    db_session.add(attempt)

    # 4. Add ATS result
    ats = ATSResult(user_id=user_id, filename="resume.pdf", ats_score=85.0)
    db_session.add(ats)

    # 5. Add interview session & result
    int_sess = InterviewSession(user_id=user_id, company="TestCo", questions_json="[]")
    db_session.add(int_sess)

    int_res = InterviewResult(user_id=user_id, interview_id=1, average_score=80.0)
    db_session.add(int_res)

    # 6. Add training progress
    tr = TrainingProgress(user_id=user_id, skill="Python", topic="Basics", completed=True)
    db_session.add(tr)

    # 7. Add GitHub account
    gh = GitHubAccount(user_id=user_id, github_user_id="99999", username="testuser", access_token="secret_token")
    db_session.add(gh)

    db_session.commit()

    # Verify records created
    assert db_session.query(StudentProfile).filter(StudentProfile.user_id == user_id).first() is not None
    assert db_session.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == user_id).first() is not None
    assert db_session.query(ATSResult).filter(ATSResult.user_id == user_id).first() is not None
    assert db_session.query(InterviewSession).filter(InterviewSession.user_id == user_id).first() is not None
    assert db_session.query(InterviewResult).filter(InterviewResult.user_id == user_id).first() is not None
    assert db_session.query(TrainingProgress).filter(TrainingProgress.user_id == user_id).first() is not None
    assert db_session.query(GitHubAccount).filter(GitHubAccount.user_id == user_id).first() is not None

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Verify cascading deletion
    assert db_session.query(StudentProfile).filter(StudentProfile.user_id == user_id).first() is None
    assert db_session.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == user_id).first() is None
    assert db_session.query(ATSResult).filter(ATSResult.user_id == user_id).first() is None
    assert db_session.query(InterviewSession).filter(InterviewSession.user_id == user_id).first() is None
    assert db_session.query(InterviewResult).filter(InterviewResult.user_id == user_id).first() is None
    assert db_session.query(TrainingProgress).filter(TrainingProgress.user_id == user_id).first() is None
    assert db_session.query(GitHubAccount).filter(GitHubAccount.user_id == user_id).first() is None
