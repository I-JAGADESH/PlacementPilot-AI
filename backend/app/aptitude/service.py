"""
Core Aptitude Assessment Service Engine for PlacementPilot AI Phase 2.
Handles 7 Assessment Modes, backend timing, option shuffling, scoring, analytics, and user performance snapshots.
"""

import json
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.aptitude.di_engine import SAMPLE_DI_DATASETS
from app.aptitude.formulas import get_formula_for_subtopic
from app.aptitude.generator import GENERATOR_REGISTRY, generate_random_aptitude_question
from app.aptitude.models import (
    AptitudeAssessment,
    AptitudeDomain,
    AptitudeQuestion,
    AptitudeSubtopic,
    AptitudeTopic,
    AssessmentAnswer,
    AssessmentQuestionMap,
    AssessmentSection,
    CompanyPattern,
    DIDataset,
    PerformanceSnapshot,
    QuestionOption,
)
from app.aptitude.taxonomy import TAXONOMY_DATA, get_subtopic_map


def seed_aptitude_taxonomy(db: Session) -> None:
    """
    Seeds normalized 14-domain taxonomy hierarchy into database if empty.
    """
    if db.query(AptitudeDomain).first() is not None:
        return

    for domain_data in TAXONOMY_DATA:
        domain = AptitudeDomain(name=domain_data["name"], slug=domain_data["slug"])
        db.add(domain)
        db.flush()

        for topic_data in domain_data["topics"]:
            topic = AptitudeTopic(
                domain_id=domain.id,
                name=topic_data["name"],
                slug=topic_data["slug"],
            )
            db.add(topic)
            db.flush()

            for subtopic_data in topic_data["subtopics"]:
                subtopic = AptitudeSubtopic(
                    topic_id=topic.id,
                    name=subtopic_data["name"],
                    slug=subtopic_data["slug"],
                )
                db.add(subtopic)
                db.flush()

    # Seed Company Patterns if empty
    if db.query(CompanyPattern).first() is None:
        cp_a = CompanyPattern(
            name="Placement-Style Configuration A",
            slug="company-pattern-a",
            description="Balanced Quantitative & Analytical Aptitude Test Pattern.",
            total_questions=20,
            duration_minutes=25,
            negative_marking=0.25,
            sections_config_json=json.dumps([
                {"name": "Quantitative Aptitude", "duration_seconds": 900},
                {"name": "Logical & Analytical Reasoning", "duration_seconds": 600},
            ]),
            topic_distribution_json=json.dumps({
                "divisibility-rules": 5,
                "percentage": 5,
                "profit-percentage": 5,
                "basic-speed-formula": 5,
            }),
        )
        cp_b = CompanyPattern(
            name="Placement-Style Configuration B",
            slug="company-pattern-b",
            description="Advanced Numerical & Data Interpretation Assessment Pattern.",
            total_questions=30,
            duration_minutes=35,
            negative_marking=0.5,
            sections_config_json=json.dumps([
                {"name": "Numerical Ability", "duration_seconds": 1200},
                {"name": "Data Interpretation", "duration_seconds": 900},
            ]),
            topic_distribution_json=json.dumps({
                "division-into-ratios": 8,
                "time-and-work": 8,
                "compound-interest-formula": 7,
                "data-interpretation": 7,
            }),
        )
        db.add(cp_a)
        db.add(cp_b)

    # Seed sample DI Datasets & static questions if empty
    if db.query(DIDataset).first() is None:
        subtopic_map = {st.slug: st for st in db.query(AptitudeSubtopic).all()}
        for ds_item in SAMPLE_DI_DATASETS:
            dataset = DIDataset(
                title=ds_item["title"],
                description=ds_item["description"],
                dataset_type=ds_item["dataset_type"],
                content_json=ds_item["content_json"],
            )
            db.add(dataset)
            db.flush()

            for q_spec in ds_item["questions"]:
                st_slug = q_spec["subtopic_slug"]
                if st_slug in subtopic_map:
                    st_obj = subtopic_map[st_slug]
                    question = AptitudeQuestion(
                        subtopic_id=st_obj.id,
                        di_dataset_id=dataset.id,
                        difficulty=q_spec["difficulty"],
                        question_type=q_spec["question_type"],
                        question_text=q_spec["question_text"],
                        correct_answer=q_spec["correct_answer"],
                        explanation=q_spec["explanation"],
                        formula_concept=q_spec["formula_concept"],
                        estimated_time_seconds=q_spec["estimated_time_seconds"],
                        negative_marking=q_spec["negative_marking"],
                        tags_json=json.dumps(q_spec["tags"]),
                        source_type="static",
                        is_generated=False,
                        validation_status="VALIDATED",
                    )
                    db.add(question)
                    db.flush()

                    for idx, opt_text in enumerate(q_spec["options"]):
                        opt_key = chr(65 + idx)
                        is_corr = (opt_text == q_spec["correct_answer"])
                        db.add(QuestionOption(
                            question_id=question.id,
                            option_key=opt_key,
                            option_text=opt_text,
                            is_correct=is_corr,
                        ))

    db.commit()


def get_or_create_subtopic_by_slug(db: Session, slug: str) -> AptitudeSubtopic:
    st = db.query(AptitudeSubtopic).filter(AptitudeSubtopic.slug == slug).first()
    if st:
        return st

    # If missing, retrieve details from subtopic map and insert domain/topic/subtopic
    s_map = get_subtopic_map()
    if slug not in s_map:
        raise ValueError(f"Unknown subtopic slug: '{slug}'")

    meta = s_map[slug]
    domain = db.query(AptitudeDomain).filter(AptitudeDomain.slug == meta["domain_slug"]).first()
    if not domain:
        domain = AptitudeDomain(name=meta["domain_name"], slug=meta["domain_slug"])
        db.add(domain)
        db.flush()

    topic = db.query(AptitudeTopic).filter(AptitudeTopic.slug == meta["topic_slug"]).first()
    if not topic:
        topic = AptitudeTopic(domain_id=domain.id, name=meta["topic_name"], slug=meta["topic_slug"])
        db.add(topic)
        db.flush()

    subtopic = AptitudeSubtopic(topic_id=topic.id, name=meta["subtopic_name"], slug=meta["subtopic_slug"])
    db.add(subtopic)
    db.flush()
    db.commit()
    return subtopic


def generate_and_persist_question(db: Session, subtopic_slug: str, seed: Optional[int] = None) -> AptitudeQuestion:
    """
    Generates a numerical question, validates it, and persists it to database.
    """
    st_obj = get_or_create_subtopic_by_slug(db, subtopic_slug)
    q_data = generate_random_aptitude_question(subtopic_slug=subtopic_slug, seed=seed)

    question = AptitudeQuestion(
        subtopic_id=st_obj.id,
        difficulty=q_data["difficulty"],
        question_type=q_data["question_type"],
        question_text=q_data["question_text"],
        correct_answer=q_data["correct_answer"],
        explanation=q_data["explanation"],
        formula_concept=q_data.get("formula_concept"),
        estimated_time_seconds=q_data.get("estimated_time_seconds", 60),
        negative_marking=q_data.get("negative_marking", 0.25),
        tags_json=json.dumps(q_data.get("tags", [])),
        source_type="generated",
        generation_strategy=q_data.get("generation_strategy"),
        is_generated=True,
        seed=seed,
        validation_status="VALIDATED",
    )
    db.add(question)
    db.flush()

    if q_data["question_type"] == "MCQ" and "options" in q_data:
        for idx, opt_text in enumerate(q_data["options"]):
            opt_key = chr(65 + idx)
            is_corr = (opt_text == q_data["correct_answer"])
            db.add(QuestionOption(
                question_id=question.id,
                option_key=opt_key,
                option_text=opt_text,
                is_correct=is_corr,
            ))

    db.commit()
    return question


def calculate_user_difficulty_progression(db: Session, user_id: int, subtopic_slug: str) -> str:
    """
    Explainable difficulty progression algorithm based on user's recent accuracy.
    """
    st_obj = db.query(AptitudeSubtopic).filter(AptitudeSubtopic.slug == subtopic_slug).first()
    if not st_obj:
        return "Medium"

    recent_answers = (
        db.query(AssessmentAnswer)
        .join(AptitudeAssessment)
        .join(AptitudeQuestion)
        .filter(
            AptitudeAssessment.user_id == user_id,
            AptitudeQuestion.subtopic_id == st_obj.id,
        )
        .order_by(AssessmentAnswer.id.desc())
        .limit(10)
        .all()
    )

    if len(recent_answers) < 3:
        return "Medium"

    correct_count = sum(1 for a in recent_answers if a.is_correct)
    acc = (correct_count / float(len(recent_answers))) * 100.0

    if acc >= 80.0:
        return "Hard"
    elif acc < 50.0:
        return "Easy"

    return "Medium"


def create_assessment_session(
    db: Session,
    user_id: int,
    mode: str,
    subtopic_slug: Optional[str] = None,
    domain_slug: Optional[str] = None,
    company_pattern_slug: Optional[str] = None,
    num_questions: int = 10,
    seed: Optional[int] = None,
) -> AptitudeAssessment:
    """
    Factory creating an assessment for any of the 7 supported modes.
    """
    seed_aptitude_taxonomy(db)
    rng = random.Random(seed)

    title_mode = mode.replace("-", " ").title()
    title = f"{title_mode} Assessment"
    duration_seconds = 1800  # Default 30 mins
    neg_marking = 0.25

    selected_questions: List[AptitudeQuestion] = []

    if mode == "Topic Practice" and subtopic_slug:
        st_obj = get_or_create_subtopic_by_slug(db, subtopic_slug)
        title = f"Practice: {st_obj.name}"

        # Fetch static questions or generate new ones
        existing_q = db.query(AptitudeQuestion).filter(AptitudeQuestion.subtopic_id == st_obj.id).all()
        selected_questions.extend(existing_q[:num_questions])

        while len(selected_questions) < num_questions:
            q_gen = generate_and_persist_question(db, subtopic_slug=subtopic_slug, seed=rng.randint(1, 100000))
            selected_questions.append(q_gen)

    elif mode == "Weak Topic Practice":
        # Identify weak subtopics from user's history
        snapshots = (
            db.query(PerformanceSnapshot)
            .filter(PerformanceSnapshot.user_id == user_id, PerformanceSnapshot.accuracy < 60.0)
            .all()
        )
        weak_slugs = []
        for sn in snapshots:
            if sn.subtopic_id:
                st = db.query(AptitudeSubtopic).get(sn.subtopic_id)
                if st:
                    weak_slugs.append(st.slug)

        if not weak_slugs:
            weak_slugs = ["percentage", "profit-percentage", "si-formula", "time-and-work"]

        title = "Weak Topic Practice Session"
        for i in range(num_questions):
            target_slug = weak_slugs[i % len(weak_slugs)]
            q_gen = generate_and_persist_question(db, subtopic_slug=target_slug, seed=rng.randint(1, 100000))
            selected_questions.append(q_gen)

    elif mode == "Retry Mode":
        # Fetch user's incorrect answers
        incorrect_answers = (
            db.query(AssessmentAnswer)
            .join(AptitudeAssessment)
            .filter(
                AptitudeAssessment.user_id == user_id,
                AssessmentAnswer.is_correct == False,
            )
            .limit(num_questions)
            .all()
        )
        if incorrect_answers:
            selected_questions = [ans.question for ans in incorrect_answers]

        # Fill remaining if needed
        while len(selected_questions) < num_questions:
            target_slug = rng.choice(["percentage", "profit-percentage", "basic-speed-formula"])
            q_gen = generate_and_persist_question(db, subtopic_slug=target_slug, seed=rng.randint(1, 100000))
            selected_questions.append(q_gen)

    elif mode == "Company-pattern Test" and company_pattern_slug:
        pattern = db.query(CompanyPattern).filter(CompanyPattern.slug == company_pattern_slug).first()
        if pattern:
            title = f"{pattern.name} Test"
            duration_seconds = pattern.duration_minutes * 60
            neg_marking = pattern.negative_marking
            num_questions = pattern.total_questions

            topic_dist = json.loads(pattern.topic_distribution_json)
            for t_slug, q_count in topic_dist.items():
                for _ in range(q_count):
                    q_gen = generate_and_persist_question(db, subtopic_slug=t_slug, seed=rng.randint(1, 100000))
                    selected_questions.append(q_gen)

    # General / Full Mock fallback
    if len(selected_questions) < num_questions:
        default_slugs = ["percentage", "profit-percentage", "si-formula", "compound-interest-formula", "basic-speed-formula", "time-and-work", "simple-average", "division-into-ratios", "hcf", "surface-area-of-cube"]
        for i in range(num_questions - len(selected_questions)):
            target_slug = default_slugs[i % len(default_slugs)]
            q_gen = generate_and_persist_question(db, subtopic_slug=target_slug, seed=rng.randint(1, 100000))
            selected_questions.append(q_gen)

    assessment = AptitudeAssessment(
        user_id=user_id,
        mode=mode,
        title=title,
        status="IN_PROGRESS",
        company_pattern_slug=company_pattern_slug,
        duration_seconds=duration_seconds,
        total_questions=len(selected_questions),
    )
    db.add(assessment)
    db.flush()

    # Map & randomize questions and options
    for idx, q in enumerate(selected_questions):
        options = db.query(QuestionOption).filter(QuestionOption.question_id == q.id).all()
        opt_list = []

        if options:
            opts_copy = list(options)
            rng.shuffle(opts_copy)
            opt_list = [
                {"key": chr(65 + o_idx), "text": opt.option_text, "original_key": opt.option_key}
                for o_idx, opt in enumerate(opts_copy)
            ]

        q_map = AssessmentQuestionMap(
            assessment_id=assessment.id,
            question_id=q.id,
            question_order=idx + 1,
            options_order_json=json.dumps(opt_list),
            seed=seed,
        )
        db.add(q_map)

    db.commit()
    db.refresh(assessment)
    return assessment


def evaluate_and_submit_assessment(db: Session, user_id: int, assessment_id: int, raw_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Authoritative backend evaluation, timing check, scoring, and performance snapshot update.
    """
    assessment = (
        db.query(AptitudeAssessment)
        .filter(AptitudeAssessment.id == assessment_id, AptitudeAssessment.user_id == user_id)
        .first()
    )
    if not assessment:
        raise ValueError("Assessment attempt not found or unauthorized.")

    if assessment.status != "IN_PROGRESS":
        raise ValueError("This assessment attempt is already completed or expired.")

    now = datetime.now(timezone.utc)
    start = assessment.start_time
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    elapsed_seconds = int((now - start).total_seconds())

    # Backend Authoritative Expiry Check
    if elapsed_seconds > assessment.duration_seconds + 30:  # 30s grace buffer for network latency
        assessment.status = "EXPIRED"

    q_maps = db.query(AssessmentQuestionMap).filter(AssessmentQuestionMap.assessment_id == assessment_id).all()
    answer_dict = {ans.get("question_id"): ans for ans in raw_answers}

    total_q = len(q_maps)
    attempted = 0
    correct = 0
    incorrect = 0
    skipped = 0
    raw_score = 0.0

    domain_stats = {}
    subtopic_stats = {}

    for qm in q_maps:
        question = qm.question
        st_slug = question.subtopic.slug if question.subtopic else "general"
        domain_name = question.subtopic.topic.domain.name if question.subtopic and question.subtopic.topic else "General"

        if domain_name not in domain_stats:
            domain_stats[domain_name] = {"total": 0, "correct": 0}
        domain_stats[domain_name]["total"] += 1

        if st_slug not in subtopic_stats:
            subtopic_stats[st_slug] = {"total": 0, "correct": 0, "subtopic_name": question.subtopic.name if question.subtopic else st_slug}
        subtopic_stats[st_slug]["total"] += 1

        ans_entry = answer_dict.get(question.id)
        selected_val = ans_entry.get("selected_option_or_text") if ans_entry else None
        time_spent = ans_entry.get("time_spent_seconds", 0) if ans_entry else 0

        is_corr = False
        score_delta = 0.0

        if not selected_val or str(selected_val).strip() == "":
            skipped += 1
        else:
            attempted += 1
            # Check correctness
            if question.question_type == "MCQ":
                # Decode randomized option mapping if available
                opt_order = json.loads(qm.options_order_json) if qm.options_order_json else []
                original_correct_text = question.correct_answer

                # Match option text or key
                matched_text = selected_val
                for opt in opt_order:
                    if opt["key"] == selected_val:
                        matched_text = opt["text"]
                        break

                if matched_text == original_correct_text:
                    is_corr = True
            elif question.question_type == "Numerical":
                try:
                    if abs(float(selected_val) - float(question.correct_answer)) < 1e-4:
                        is_corr = True
                except ValueError:
                    is_corr = False
            else:
                if str(selected_val).strip().lower() == str(question.correct_answer).strip().lower():
                    is_corr = True

            if is_corr:
                correct += 1
                score_delta = 1.0
                domain_stats[domain_name]["correct"] += 1
                subtopic_stats[st_slug]["correct"] += 1
            else:
                incorrect += 1
                score_delta = -abs(question.negative_marking)

        raw_score += score_delta

        db.add(AssessmentAnswer(
            assessment_id=assessment.id,
            question_id=question.id,
            selected_option_or_text=selected_val,
            is_correct=is_corr,
            time_spent_seconds=time_spent,
            score_delta=score_delta,
        ))

        # Update or create PerformanceSnapshot
        if question.subtopic:
            domain_id = question.subtopic.topic.domain_id
            subtopic_id = question.subtopic.id

            snapshot = (
                db.query(PerformanceSnapshot)
                .filter(
                    PerformanceSnapshot.user_id == user_id,
                    PerformanceSnapshot.subtopic_id == subtopic_id,
                )
                .first()
            )
            if not snapshot:
                snapshot = PerformanceSnapshot(
                    user_id=user_id,
                    domain_id=domain_id,
                    subtopic_id=subtopic_id,
                    total_attempted=0,
                    total_correct=0,
                )
                db.add(snapshot)

            snapshot.total_attempted += 1 if selected_val else 0
            if is_corr:
                snapshot.total_correct += 1
            if snapshot.total_attempted > 0:
                snapshot.accuracy = round((snapshot.total_correct / float(snapshot.total_attempted)) * 100.0, 2)

    score_pct = round((correct / float(total_q)) * 100.0, 2) if total_q > 0 else 0.0
    accuracy = round((correct / float(attempted)) * 100.0, 2) if attempted > 0 else 0.0

    actual_time = min(elapsed_seconds, assessment.duration_seconds)
    qpm = round((attempted / (actual_time / 60.0)), 2) if actual_time > 0 else 0.0

    if assessment.status != "EXPIRED":
        assessment.status = "COMPLETED"

    assessment.end_time = now
    assessment.attempted_questions = attempted
    assessment.correct_answers = correct
    assessment.incorrect_answers = incorrect
    assessment.skipped_answers = skipped
    assessment.raw_score = raw_score
    assessment.score_percentage = score_pct
    assessment.time_spent_seconds = actual_time
    assessment.avg_time_per_question = round(actual_time / float(total_q), 2) if total_q > 0 else 0.0
    assessment.accuracy_percentage = accuracy
    assessment.speed_qpm = qpm

    assessment.domain_performance_json = json.dumps(domain_stats)
    assessment.subtopic_performance_json = json.dumps(subtopic_stats)

    db.commit()
    db.refresh(assessment)

    # Derive weak and strong topics based on current assessment performance
    strong_topics = [s_info["subtopic_name"] for s_slug, s_info in subtopic_stats.items() if (s_info["correct"] / float(s_info["total"])) >= 0.7]
    weak_topics = [s_info["subtopic_name"] for s_slug, s_info in subtopic_stats.items() if (s_info["correct"] / float(s_info["total"])) < 0.7]

    recommendations = []
    if score_pct < 60:
        recommendations.append("Accuracy is below target. Focus on foundational formulas and practice easy-level numerical problems.")
    if weak_topics:
        recommendations.append(f"Target your focus practice sessions on: {', '.join(weak_topics[:3])}.")
    if score_pct >= 80:
        recommendations.append("Excellent speed and accuracy! Advance to Hard & Expert difficulty mock tests.")
    else:
        recommendations.append("Review detailed solution step-by-step breakdowns for skipped or incorrect questions.")

    return {
        "assessment_id": assessment.id,
        "mode": assessment.mode,
        "title": assessment.title,
        "status": assessment.status,
        "total_questions": total_q,
        "attempted_questions": attempted,
        "correct_answers": correct,
        "incorrect_answers": incorrect,
        "skipped_answers": skipped,
        "raw_score": raw_score,
        "score_percentage": score_pct,
        "accuracy_percentage": accuracy,
        "speed_qpm": qpm,
        "time_spent_seconds": actual_time,
        "domain_performance": domain_stats,
        "subtopic_performance": subtopic_stats,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "recommendations": recommendations,
    }


def get_user_aptitude_analytics(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Computes truthful analytics strictly from persisted user attempts in database.
    Returns empty/unattempted state if no attempts exist.
    """
    attempts = (
        db.query(AptitudeAssessment)
        .filter(AptitudeAssessment.user_id == user_id, AptitudeAssessment.status.in_(["COMPLETED", "EXPIRED"]))
        .order_by(AptitudeAssessment.end_time.desc())
        .all()
    )

    if not attempts:
        return {
            "has_data": False,
            "message": "No aptitude assessments completed yet. Take a test to unlock personalized analytics.",
            "overall_score": 0.0,
            "overall_accuracy": 0.0,
            "total_attempts": 0,
            "strongest_subtopics": [],
            "weakest_subtopics": [],
            "recent_attempts": [],
            "recommendations": ["Start with Practice Mode or Topic Practice to begin performance tracking."],
        }

    total_attempts = len(attempts)
    avg_score = round(sum(a.score_percentage for a in attempts) / float(total_attempts), 2)
    avg_accuracy = round(sum(a.accuracy_percentage for a in attempts) / float(total_attempts), 2)

    # Subtopic analysis across snapshots
    snapshots = (
        db.query(PerformanceSnapshot)
        .filter(PerformanceSnapshot.user_id == user_id)
        .all()
    )

    strongest = []
    weakest = []

    for sn in snapshots:
        if sn.subtopic:
            item = {
                "subtopic_name": sn.subtopic.name,
                "subtopic_slug": sn.subtopic.slug,
                "accuracy": sn.accuracy,
                "total_attempted": sn.total_attempted,
            }
            if sn.accuracy >= 70.0 and sn.total_attempted >= 2:
                strongest.append(item)
            elif sn.accuracy < 60.0 and sn.total_attempted >= 1:
                weakest.append(item)

    strongest.sort(key=lambda x: x["accuracy"], reverse=True)
    weakest.sort(key=lambda x: x["accuracy"])

    rec_actions = []
    if weakest:
        rec_actions.append(f"Practice your weakest subtopic: '{weakest[0]['subtopic_name']}'.")
    if avg_accuracy < 70:
        rec_actions.append("Work on accuracy before attempting full timed company mock tests.")
    else:
        rec_actions.append("Attempt Full Placement Mock Tests to test endurance under pressure.")

    return {
        "has_data": True,
        "overall_score": avg_score,
        "overall_accuracy": avg_accuracy,
        "total_attempts": total_attempts,
        "strongest_subtopics": strongest[:5],
        "weakest_subtopics": weakest[:5],
        "recent_attempts": [
            {
                "assessment_id": a.id,
                "title": a.title,
                "mode": a.mode,
                "score_percentage": a.score_percentage,
                "accuracy_percentage": a.accuracy_percentage,
                "completed_at": a.end_time,
            }
            for a in attempts[:5]
        ],
        "recommendations": rec_actions,
    }
