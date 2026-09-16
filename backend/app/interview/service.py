import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.interview.schemas import (
    InterviewQuestion,
    InterviewEvaluation,
    InterviewStartRequest,
)
from app.ai.evaluator import evaluator
from app.interview.models import (
    InterviewResult,
    InterviewSession,
    InterviewQuestionAnswer,
)
from app.interview.context import build_user_profile_context
from app.interview.generators import (
    generate_interview_questions,
    ROLES,
    EXPERIENCE_LEVELS,
    INTERVIEW_ROUNDS,
    DIFFICULTIES,
    DOMAINS,
)


def normalize_company(company: Optional[str]) -> str:
    """Normalize company name."""
    if not company or not company.strip():
        return "Generic"
    c_clean = company.strip()
    return c_clean



def get_interview_config(db: Session, user_id: int) -> Dict[str, Any]:
    """Return available interview config parameters and current user profile context summary."""
    profile_ctx = build_user_profile_context(db, user_id)
    return {
        "roles": ROLES,
        "experience_levels": EXPERIENCE_LEVELS,
        "interview_rounds": INTERVIEW_ROUNDS,
        "difficulties": DIFFICULTIES,
        "domains": DOMAINS,
        "user_profile_summary": {
            "target_company": profile_ctx.get("target_company"),
            "target_role": profile_ctx.get("target_role"),
            "projects_count": len(profile_ctx.get("projects", [])),
            "skills_count": len(profile_ctx.get("skills", [])),
            "weak_topics": profile_ctx.get("weak_topics", []),
        },
    }


def get_questions(
    interview_type: str = "Technical MCQ",
    difficulty: str = "Medium",
    company: Optional[str] = None,
    role: str = "Software Engineer",
    experience_level: str = "Entry Level",
    domain: Optional[str] = "DSA",
    profile_context: Optional[Dict[str, Any]] = None,
) -> List[InterviewQuestion]:
    """Generate company-style interview questions."""
    norm_company = normalize_company(company)
    return generate_interview_questions(
        round_type=interview_type,
        role=role,
        experience_level=experience_level,
        difficulty=difficulty,
        domain=domain,
        company=norm_company,
        profile_context=profile_context,
        count=5,
    )


def create_interview_session(
    db: Session,
    request: InterviewStartRequest,
    user_id: int,
) -> InterviewSession:
    """Create and persist a new user-isolated interview session with profile awareness."""
    profile_ctx = build_user_profile_context(db, user_id)

    round_type = request.interview_round or request.interview_type or "Technical MCQ"
    role = request.role or "Software Engineer"
    exp_level = request.experience_level or "Entry Level"
    diff = request.difficulty or "Medium"
    dom = request.domain or "DSA"
    comp = normalize_company(request.company or profile_ctx.get("target_company"))

    questions = generate_interview_questions(
        round_type=round_type,
        role=role,
        experience_level=exp_level,
        difficulty=diff,
        domain=dom,
        company=comp,
        profile_context=profile_ctx,
        count=5,
    )

    questions_data = [q.model_dump() for q in questions]

    session = InterviewSession(
        user_id=user_id,
        company=comp,
        target_role=role,
        experience_level=exp_level,
        interview_type=round_type,
        difficulty=diff,
        domain=dom,
        current_index=0,
        total_questions=len(questions),
        questions_json=json.dumps(questions_data),
        profile_context_json=json.dumps(profile_ctx),
        status="in_progress",
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_interview_session(db: Session, interview_id: int) -> Optional[InterviewSession]:
    """Retrieve an active or completed interview session from database."""
    return db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()


def get_next_question(db: Session, interview_id: int) -> Optional[InterviewQuestion]:
    """Return the next unanswered question for an interview session."""
    session = get_interview_session(db, interview_id)
    if session is None:
        return None

    questions_data = json.loads(session.questions_json)
    if session.current_index >= len(questions_data):
        return None

    q_data = questions_data[session.current_index]
    return InterviewQuestion(**q_data)


def save_interview_evaluation(
    db: Session,
    interview_id: int,
    question_id: int,
    answer: str,
    evaluation: InterviewEvaluation,
) -> Optional[InterviewSession]:
    """Save evaluation, execute adaptive difficulty check, and persist progression."""
    session = get_interview_session(db, interview_id)
    if session is None:
        return None

    questions_data = json.loads(session.questions_json)
    q_data = None
    for q in questions_data:
        if q.get("question_id") == question_id:
            q_data = q
            break

    question_text = q_data.get("question", "") if q_data else ""
    category = q_data.get("category", "General") if q_data else "General"
    q_type = q_data.get("question_type", "short_answer") if q_data else "short_answer"

    # Adaptive Check for Next Question
    adaptation_reason = None
    if evaluation.score < 50.0:
        adaptation_reason = "Adaptive engine: Candidate struggled (score < 50). Foundational concepts reinforced for remaining questions."
    elif evaluation.score > 85.0:
        adaptation_reason = "Adaptive engine: Strong candidate performance (score > 85). Advanced application depth enabled."

    evaluation.adaptation_reason = adaptation_reason

    qa = InterviewQuestionAnswer(
        session_id=session.id,
        question_id=question_id,
        question_text=question_text,
        round_type=session.interview_type,
        category=category,
        question_type=q_type,
        user_answer=answer,
        score=float(evaluation.score),
        communication_score=float(evaluation.communication_score),
        technical_score=float(evaluation.technical_score),
        evaluation_json=json.dumps(evaluation.model_dump()),
        missed_concepts_json=json.dumps(evaluation.missed_concepts),
        adaptation_reason=adaptation_reason,
    )
    db.add(qa)

    session.current_index += 1
    if session.current_index >= len(questions_data):
        session.status = "completed"
        db.commit()
        db.refresh(session)
        _persist_interview_result(db, session)
    else:
        db.commit()
        db.refresh(session)

    return session


def _get_performance_level(score: float) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "developing"
    return "needs_improvement"


def _persist_interview_result(db: Session, session: InterviewSession) -> None:
    """Persist completed interview result with comprehensive metrics and preparation roadmap."""
    user_id = session.user_id
    if user_id is None:
        return

    answers = (
        db.query(InterviewQuestionAnswer)
        .filter(InterviewQuestionAnswer.session_id == session.id)
        .all()
    )
    if not answers:
        return

    avg_score = round(sum(a.score for a in answers) / len(answers), 2)
    comm_score = round(sum(a.communication_score for a in answers) / len(answers), 2)

    # Consolidate feedback across answers
    strengths, weaknesses, tech_gaps, comm_feedback, missed_concepts = [], [], [], [], []

    for a in answers:
        if a.evaluation_json:
            try:
                e = json.loads(a.evaluation_json)
                strengths.extend(e.get("strengths", []))
                weaknesses.extend(e.get("weaknesses", []))
                tech_gaps.extend(e.get("technical_gaps", []))
                comm_feedback.extend(e.get("communication_feedback", []))
                missed_concepts.extend(e.get("missed_concepts", []))
            except Exception:
                pass

    # Unique filtering
    strengths = list(dict.fromkeys(strengths))[:6]
    weaknesses = list(dict.fromkeys(weaknesses))[:6]
    tech_gaps = list(dict.fromkeys(tech_gaps))[:6]
    comm_feedback = list(dict.fromkeys(comm_feedback))[:6]
    missed_concepts = list(dict.fromkeys(missed_concepts))[:6]

    # Recommended Topics & Roadmap derivation
    recommended_topics = list(dict.fromkeys(tech_gaps + missed_concepts))[:5]
    if not recommended_topics:
        recommended_topics = [session.domain or "Core CS Fundamentals", "System Architecture"]

    next_diff = "Hard" if avg_score >= 80 else ("Medium" if avg_score >= 50 else "Easy")

    roadmap = [
        f"Review core principles in {session.domain or 'CS Topics'}.",
        f"Practice STAR-method structured responses for {session.interview_type}.",
    ]
    if tech_gaps:
        roadmap.append(f"Address technical gap: {tech_gaps[0]}")
    if missed_concepts:
        roadmap.append(f"Revisit missed concept: {missed_concepts[0]}")

    result = (
        db.query(InterviewResult)
        .filter(
            InterviewResult.user_id == user_id,
            InterviewResult.interview_id == session.id,
        )
        .first()
    )

    if result is None:
        result = InterviewResult(user_id=user_id, interview_id=session.id)
        db.add(result)

    questions = json.loads(session.questions_json)

    result.company = session.company
    result.target_role = session.target_role
    result.experience_level = session.experience_level
    result.interview_type = session.interview_type
    result.difficulty = session.difficulty
    result.domain = session.domain
    result.completed_questions = len(answers)
    result.total_questions = len(questions)
    result.average_score = avg_score
    result.communication_score = comm_score
    result.performance_level = _get_performance_level(avg_score)
    result.strengths_json = json.dumps(strengths)
    result.weaknesses_json = json.dumps(weaknesses)
    result.technical_gaps_json = json.dumps(tech_gaps)
    result.communication_feedback_json = json.dumps(comm_feedback)
    result.missed_concepts_json = json.dumps(missed_concepts)
    result.recommended_topics_json = json.dumps(recommended_topics)
    result.next_recommended_difficulty = next_diff
    result.preparation_roadmap_json = json.dumps(roadmap)

    db.commit()


def evaluate_answer(
    question: str,
    answer: str,
    category: str,
    company: Optional[str] = None,
    difficulty: str = "Medium",
    question_type: str = "short_answer",
    rubric: Optional[str] = None,
) -> InterviewEvaluation:
    """Evaluate an interview answer using the AI evaluator."""
    return evaluator.evaluate(
        question=question,
        answer=answer,
        category=category,
        company=company,
        difficulty=difficulty,
        question_type=question_type,
        rubric=rubric,
    )


def get_interview_summary(db: Session, interview_id: int) -> Optional[Dict[str, Any]]:
    """Calculate and return full interview summary from persistent session and result records."""
    session = get_interview_session(db, interview_id)
    if session is None:
        return None

    answers = (
        db.query(InterviewQuestionAnswer)
        .filter(InterviewQuestionAnswer.session_id == session.id)
        .all()
    )

    completed_cnt = len(answers)
    questions = json.loads(session.questions_json)
    total_cnt = len(questions)

    if completed_cnt > 0 and completed_cnt >= total_cnt:
        _persist_interview_result(db, session)

    res = (
        db.query(InterviewResult)
        .filter(InterviewResult.interview_id == session.id)
        .first()
    )

    if res:
        return {
            "interview_id": session.id,
            "company": session.company,
            "target_role": session.target_role,
            "experience_level": session.experience_level,
            "interview_type": session.interview_type,
            "difficulty": session.difficulty,
            "domain": session.domain,
            "completed_questions": completed_cnt,
            "total_questions": total_cnt,
            "average_score": res.average_score,
            "communication_score": res.communication_score,
            "performance_level": res.performance_level,
            "completed": completed_cnt >= total_cnt,
            "strengths": json.loads(res.strengths_json) if res.strengths_json else [],
            "weaknesses": json.loads(res.weaknesses_json) if res.weaknesses_json else [],
            "technical_gaps": json.loads(res.technical_gaps_json) if res.technical_gaps_json else [],
            "communication_feedback": json.loads(res.communication_feedback_json) if res.communication_feedback_json else [],
            "missed_concepts": json.loads(res.missed_concepts_json) if res.missed_concepts_json else [],
            "recommended_topics": json.loads(res.recommended_topics_json) if res.recommended_topics_json else [],
            "next_recommended_difficulty": res.next_recommended_difficulty or "Medium",
            "preparation_roadmap": json.loads(res.preparation_roadmap_json) if res.preparation_roadmap_json else [],
        }

    # In-progress fallback return
    avg_score = round(sum(a.score for a in answers) / completed_cnt, 2) if completed_cnt else 0.0
    comm_score = round(sum(a.communication_score for a in answers) / completed_cnt, 2) if completed_cnt else 0.0

    return {
        "interview_id": session.id,
        "company": session.company,
        "target_role": session.target_role,
        "experience_level": session.experience_level,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "domain": session.domain,
        "completed_questions": completed_cnt,
        "total_questions": total_cnt,
        "average_score": avg_score,
        "communication_score": comm_score,
        "performance_level": _get_performance_level(avg_score),
        "completed": completed_cnt >= total_cnt,
        "strengths": [],
        "weaknesses": [],
        "technical_gaps": [],
        "communication_feedback": [],
        "missed_concepts": [],
        "recommended_topics": [],
        "next_recommended_difficulty": "Medium",
        "preparation_roadmap": [],
    }


def get_user_interview_history(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Get history of interview sessions for authenticated user."""
    results = (
        db.query(InterviewResult)
        .filter(InterviewResult.user_id == user_id)
        .order_by(InterviewResult.created_at.desc())
        .all()
    )

    history = []
    for r in results:
        history.append({
            "id": r.interview_id,
            "company": r.company,
            "target_role": r.target_role,
            "experience_level": r.experience_level,
            "interview_type": r.interview_type,
            "difficulty": r.difficulty,
            "domain": r.domain,
            "average_score": r.average_score,
            "performance_level": r.performance_level,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })
    return history


def get_user_recommendations(db: Session, user_id: int) -> Dict[str, Any]:
    """Aggregate user-wide weak areas, recommended topics, and roadmap across past interviews."""
    results = (
        db.query(InterviewResult)
        .filter(InterviewResult.user_id == user_id)
        .order_by(InterviewResult.created_at.desc())
        .limit(5)
        .all()
    )

    all_gaps, all_topics, roadmap_items = [], [], []
    for r in results:
        if r.technical_gaps_json:
            all_gaps.extend(json.loads(r.technical_gaps_json))
        if r.recommended_topics_json:
            all_topics.extend(json.loads(r.recommended_topics_json))
        if r.preparation_roadmap_json:
            roadmap_items.extend(json.loads(r.preparation_roadmap_json))

    return {
        "user_id": user_id,
        "identified_technical_gaps": list(dict.fromkeys(all_gaps))[:8],
        "recommended_topics": list(dict.fromkeys(all_topics))[:8],
        "actionable_roadmap": list(dict.fromkeys(roadmap_items))[:6],
    }