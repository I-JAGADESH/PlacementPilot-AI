"""
Profile Context Aggregator for PlacementPilot AI Interview System.

Aggregates authenticated user profile data, projects, skills, certifications,
GitHub activity, ATS resume signals, and assessment weak areas into a structured context object.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.profile.models import StudentProfile, StudentSkill, StudentProject, StudentCertification
from app.github.models import GitHubAccount
from app.ats.models import ATSResult
from app.aptitude.models import PerformanceSnapshot, AptitudeSubtopic, AptitudeTopic
from app.assessment.models import AssessmentAttempt
from app.interview.models import InterviewResult


def build_user_profile_context(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Build a safe, read-only dictionary of the user's authentic profile data.
    If data is missing, empty lists/defaults are returned so generators can fall back gracefully.
    """
    context: Dict[str, Any] = {
        "user_id": user_id,
        "target_company": None,
        "target_role": None,
        "bio": None,
        "skills": [],
        "projects": [],
        "certifications": [],
        "github": None,
        "ats_summary": None,
        "weak_topics": [],
        "previous_interview_weaknesses": [],
    }

    # 1. Profile, Skills, Projects, Certifications
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if profile:
        context["target_company"] = profile.target_company
        context["target_role"] = profile.target_role
        context["bio"] = profile.bio

        skills = db.query(StudentSkill).filter(StudentSkill.profile_id == profile.id).all()
        for s in skills:
            context["skills"].append({
                "name": s.name,
                "category": s.category or "General",
                "proficiency": s.proficiency or 50.0,
            })

        projects = db.query(StudentProject).filter(StudentProject.profile_id == profile.id).all()
        for p in projects:
            context["projects"].append({
                "title": p.title,
                "description": p.description or "",
                "technologies": [tech.strip() for tech in (p.technologies or "").split(",") if tech.strip()],
                "github_url": p.github_url,
            })

        certs = db.query(StudentCertification).filter(StudentCertification.profile_id == profile.id).all()
        for c in certs:
            context["certifications"].append({
                "name": c.name,
                "issuer": c.issuer or "",
            })

    # 2. GitHub
    gh = db.query(GitHubAccount).filter(GitHubAccount.user_id == user_id).first()
    if gh:
        context["github"] = {
            "username": gh.username,
            "public_repositories": gh.public_repositories,
            "total_stars": gh.total_stars,
        }

    # 3. ATS Resume
    ats = (
        db.query(ATSResult)
        .filter(ATSResult.user_id == user_id)
        .order_by(ATSResult.created_at.desc())
        .first()
    )
    if ats:
        context["ats_summary"] = {
            "filename": ats.filename,
            "ats_score": ats.ats_score,
            "performance_level": ats.performance_level,
        }

    # 4. Assessment Weak Areas (Aptitude & Technical)
    snapshots = (
        db.query(PerformanceSnapshot, AptitudeSubtopic.name.label("subtopic_name"))
        .join(AptitudeSubtopic, PerformanceSnapshot.subtopic_id == AptitudeSubtopic.id, isouter=True)
        .filter(PerformanceSnapshot.user_id == user_id)
        .all()
    )
    for snap, subtopic_name in snapshots:
        if snap.accuracy < 65.0 and subtopic_name:
            context["weak_topics"].append(subtopic_name)

    # Legacy assessment attempts check
    attempts = (
        db.query(AssessmentAttempt)
        .filter(AssessmentAttempt.user_id == user_id)
        .order_by(AssessmentAttempt.created_at.desc())
        .limit(5)
        .all()
    )
    for att in attempts:
        if att.score_percentage < 60.0 and att.skill:
            if att.skill not in context["weak_topics"]:
                context["weak_topics"].append(att.skill)


    # 5. Previous Interview Gaps
    past_interviews = (
        db.query(InterviewResult)
        .filter(InterviewResult.user_id == user_id, InterviewResult.average_score < 65.0)
        .limit(5)
        .all()
    )
    for pi in past_interviews:
        context["previous_interview_weaknesses"].append(f"{pi.interview_type} ({pi.target_role})")

    return context
