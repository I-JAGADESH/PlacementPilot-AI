import json
from typing import List, Optional
from sqlalchemy.orm import Session

from app.interview.schemas import (
    InterviewQuestion,
    InterviewEvaluation,
)
from app.ai.evaluator import evaluator
from app.interview.models import (
    InterviewResult,
    InterviewSession,
    InterviewQuestionAnswer,
)


# ============================================================
# COMPANY QUESTION BANK
# ============================================================

QUESTION_BANK = {

    # ========================================================
    # GENERIC
    # ========================================================

    "Generic": {

        "technical": [
            {
                "question": "What is object-oriented programming? Explain its main principles.",
                "category": "Programming",
            },
            {
                "question": "What is the difference between a process and a thread?",
                "category": "Operating Systems",
            },
            {
                "question": "What is a data structure? Explain common types.",
                "category": "Data Structures",
            },
            {
                "question": "What is the difference between an array and a linked list?",
                "category": "Data Structures",
            },
            {
                "question": "What is the difference between stack and queue?",
                "category": "Data Structures",
            },
            {
                "question": "What is a database management system?",
                "category": "DBMS",
            },
            {
                "question": "What is normalization in DBMS?",
                "category": "DBMS",
            },
            {
                "question": "What is an API? Explain REST APIs.",
                "category": "Web Development",
            },
            {
                "question": "What is the difference between HTTP GET and POST?",
                "category": "Web Development",
            },
        ],

        "hr": [
            {
                "question": "Tell me about yourself.",
                "category": "HR",
            },
            {
                "question": "Why do you want to join our company?",
                "category": "HR",
            },
            {
                "question": "What are your strengths and weaknesses?",
                "category": "HR",
            },
            {
                "question": "Where do you see yourself in five years?",
                "category": "HR",
            },
            {
                "question": "Why should we hire you?",
                "category": "HR",
            },
        ],

        "behavioral": [
            {
                "question": "Tell me about a challenging project you worked on.",
                "category": "Behavioral",
            },
            {
                "question": "Describe a situation where you solved a difficult problem.",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you worked as part of a team.",
                "category": "Behavioral",
            },
            {
                "question": "Describe a failure and what you learned from it.",
                "category": "Behavioral",
            },
            {
                "question": "How do you handle pressure and deadlines?",
                "category": "Behavioral",
            },
        ],
    },


    # ========================================================
    # ZOHO
    # ========================================================

    "Zoho": {

        "technical": [
            {
                "question": "Explain object-oriented programming and its four main principles.",
                "category": "Programming",
            },
            {
                "question": "What is the difference between C++ and Java?",
                "category": "Programming",
            },
            {
                "question": "Explain inheritance and polymorphism with an example.",
                "category": "OOP",
            },
            {
                "question": "How would you reverse a string without using a built-in reverse function?",
                "category": "Programming",
            },
            {
                "question": "Explain arrays, linked lists, stacks and queues.",
                "category": "Data Structures",
            },
            {
                "question": "How would you find duplicate elements in an array?",
                "category": "Data Structures",
            },
            {
                "question": "What is normalization in SQL?",
                "category": "SQL",
            },
            {
                "question": "Write a SQL query to find the second highest salary.",
                "category": "SQL",
            },
            {
                "question": "Explain the difference between primary key and foreign key.",
                "category": "DBMS",
            },
            {
                "question": "What is the difference between process and thread?",
                "category": "Operating Systems",
            },
        ],

        "hr": [
            {
                "question": "Tell me about yourself.",
                "category": "HR",
            },
            {
                "question": "Why do you want to join Zoho?",
                "category": "HR",
            },
            {
                "question": "Why should Zoho hire you?",
                "category": "HR",
            },
            {
                "question": "What are your strengths and weaknesses?",
                "category": "HR",
            },
            {
                "question": "Are you comfortable learning new technologies?",
                "category": "HR",
            },
        ],

        "behavioral": [
            {
                "question": "Tell me about a difficult technical problem you solved.",
                "category": "Behavioral",
            },
            {
                "question": "Describe a project where you had to learn something quickly.",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you disagreed with a teammate.",
                "category": "Behavioral",
            },
            {
                "question": "How do you approach debugging a program?",
                "category": "Behavioral",
            },
            {
                "question": "Describe a situation where you had to meet a strict deadline.",
                "category": "Behavioral",
            },
        ],
    },


    # ========================================================
    # TCS
    # ========================================================

    "TCS": {

        "technical": [
            {
                "question": "Explain the four pillars of OOP.",
                "category": "OOP",
            },
            {
                "question": "What is the difference between C and C++?",
                "category": "Programming",
            },
            {
                "question": "Explain the difference between stack and heap memory.",
                "category": "Programming",
            },
            {
                "question": "What is a linked list?",
                "category": "Data Structures",
            },
            {
                "question": "Explain time complexity and Big-O notation.",
                "category": "Algorithms",
            },
            {
                "question": "What is binary search and what is its time complexity?",
                "category": "Algorithms",
            },
            {
                "question": "What is normalization?",
                "category": "DBMS",
            },
            {
                "question": "Explain primary key, foreign key and candidate key.",
                "category": "DBMS",
            },
            {
                "question": "What is SQL JOIN? Explain its types.",
                "category": "SQL",
            },
            {
                "question": "What is an operating system?",
                "category": "Operating Systems",
            },
        ],

        "hr": [
            {
                "question": "Tell me about yourself.",
                "category": "HR",
            },
            {
                "question": "Why do you want to join TCS?",
                "category": "HR",
            },
            {
                "question": "Are you willing to relocate?",
                "category": "HR",
            },
            {
                "question": "What are your career goals?",
                "category": "HR",
            },
            {
                "question": "Why should we hire you?",
                "category": "HR",
            },
        ],

        "behavioral": [
            {
                "question": "Tell me about a challenging project.",
                "category": "Behavioral",
            },
            {
                "question": "How do you handle conflicts in a team?",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you showed leadership.",
                "category": "Behavioral",
            },
            {
                "question": "How do you prioritize multiple tasks?",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a mistake you made and what you learned.",
                "category": "Behavioral",
            },
        ],
    },


    # ========================================================
    # INFOSYS
    # ========================================================

    "Infosys": {

        "technical": [
            {
                "question": "What are the principles of object-oriented programming?",
                "category": "OOP",
            },
            {
                "question": "What is the difference between compile-time and run-time polymorphism?",
                "category": "OOP",
            },
            {
                "question": "Explain arrays and linked lists.",
                "category": "Data Structures",
            },
            {
                "question": "What is recursion?",
                "category": "Algorithms",
            },
            {
                "question": "What is the difference between BFS and DFS?",
                "category": "Algorithms",
            },
            {
                "question": "Explain SQL joins.",
                "category": "SQL",
            },
            {
                "question": "What is normalization in DBMS?",
                "category": "DBMS",
            },
            {
                "question": "Explain process scheduling.",
                "category": "Operating Systems",
            },
            {
                "question": "What is deadlock?",
                "category": "Operating Systems",
            },
        ],

        "hr": [
            {
                "question": "Tell me about yourself.",
                "category": "HR",
            },
            {
                "question": "Why do you want to join Infosys?",
                "category": "HR",
            },
            {
                "question": "What are your strengths?",
                "category": "HR",
            },
            {
                "question": "What are your weaknesses?",
                "category": "HR",
            },
            {
                "question": "Where do you see yourself in five years?",
                "category": "HR",
            },
        ],

        "behavioral": [
            {
                "question": "Describe a challenging situation and how you handled it.",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you worked in a team.",
                "category": "Behavioral",
            },
            {
                "question": "How do you handle failure?",
                "category": "Behavioral",
            },
            {
                "question": "How do you manage deadlines?",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you demonstrated leadership.",
                "category": "Behavioral",
            },
        ],
    },


    # ========================================================
    # AMAZON
    # ========================================================

    "Amazon": {

        "technical": [
            {
                "question": "Explain the difference between an array and a linked list.",
                "category": "Data Structures",
            },
            {
                "question": "How would you find the first non-repeating character in a string?",
                "category": "Algorithms",
            },
            {
                "question": "Explain hash tables and their average time complexity.",
                "category": "Data Structures",
            },
            {
                "question": "What is the difference between BFS and DFS?",
                "category": "Algorithms",
            },
            {
                "question": "Explain binary search.",
                "category": "Algorithms",
            },
            {
                "question": "What is a database index?",
                "category": "DBMS",
            },
            {
                "question": "Explain SQL joins.",
                "category": "SQL",
            },
            {
                "question": "What is REST API?",
                "category": "Web Development",
            },
            {
                "question": "What is the difference between process and thread?",
                "category": "Operating Systems",
            },
        ],

        "hr": [
            {
                "question": "Tell me about yourself.",
                "category": "HR",
            },
            {
                "question": "Why do you want to work at Amazon?",
                "category": "HR",
            },
            {
                "question": "Why should we hire you?",
                "category": "HR",
            },
            {
                "question": "What is your biggest strength?",
                "category": "HR",
            },
            {
                "question": "What is your biggest weakness?",
                "category": "HR",
            },
        ],

        "behavioral": [
            {
                "question": "Tell me about a time you demonstrated leadership.",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you disagreed with a teammate.",
                "category": "Behavioral",
            },
            {
                "question": "Describe a difficult problem you solved.",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a failure and what you learned.",
                "category": "Behavioral",
            },
            {
                "question": "Describe a situation where you took ownership.",
                "category": "Behavioral",
            },
        ],
    },


    # ========================================================
    # MICROSOFT
    # ========================================================

    "Microsoft": {

        "technical": [
            {
                "question": "Explain object-oriented programming.",
                "category": "OOP",
            },
            {
                "question": "What is the difference between stack and heap?",
                "category": "Programming",
            },
            {
                "question": "Explain binary trees.",
                "category": "Data Structures",
            },
            {
                "question": "What is a binary search tree?",
                "category": "Data Structures",
            },
            {
                "question": "Explain Big-O complexity.",
                "category": "Algorithms",
            },
            {
                "question": "What is dynamic programming?",
                "category": "Algorithms",
            },
            {
                "question": "Explain SQL indexing.",
                "category": "SQL",
            },
            {
                "question": "What is multithreading?",
                "category": "Operating Systems",
            },
            {
                "question": "What is cloud computing?",
                "category": "Cloud",
            },
        ],

        "hr": [
            {
                "question": "Tell me about yourself.",
                "category": "HR",
            },
            {
                "question": "Why Microsoft?",
                "category": "HR",
            },
            {
                "question": "Why should we hire you?",
                "category": "HR",
            },
            {
                "question": "What motivates you?",
                "category": "HR",
            },
            {
                "question": "Where do you see yourself in five years?",
                "category": "HR",
            },
        ],

        "behavioral": [
            {
                "question": "Tell me about a difficult technical problem you solved.",
                "category": "Behavioral",
            },
            {
                "question": "Describe a time when you had to learn a new technology.",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you received critical feedback.",
                "category": "Behavioral",
            },
            {
                "question": "Describe a situation where you had to make a difficult decision.",
                "category": "Behavioral",
            },
            {
                "question": "Tell me about a time you worked with a difficult teammate.",
                "category": "Behavioral",
            },
        ],
    },
}


# ============================================================
# COMPANY NAME NORMALIZATION
# ============================================================

def normalize_company(company: Optional[str]) -> str:
    """
    Normalize company name.

    Unknown companies fall back to Generic.
    """

    if not company:
        return "Generic"

    company = company.strip().lower()

    company_aliases = {
        "zoho": "Zoho",
        "tcs": "TCS",
        "infosys": "Infosys",
        "amazon": "Amazon",
        "microsoft": "Microsoft",
    }

    return company_aliases.get(
        company,
        "Generic",
    )


# ============================================================
# GET QUESTIONS
# ============================================================

def get_questions(
    interview_type: str = "technical",
    difficulty: str = "medium",
    company: Optional[str] = None,
) -> List[InterviewQuestion]:
    """
    Get company-specific interview questions.

    Unknown companies use the Generic question bank.
    """

    normalized_company = normalize_company(company)

    interview_type = interview_type.lower().strip()

    if interview_type not in {
        "technical",
        "hr",
        "behavioral",
    }:
        interview_type = "technical"

    company_questions = QUESTION_BANK.get(
        normalized_company,
        QUESTION_BANK["Generic"],
    )

    raw_questions = company_questions.get(
        interview_type,
        company_questions["technical"],
    )

    questions = []

    for index, question_data in enumerate(
        raw_questions,
        start=1,
    ):
        questions.append(
            InterviewQuestion(
                question_id=index,
                question=question_data["question"],
                category=question_data["category"],
                difficulty=difficulty,
                company=normalized_company,
            )
        )

    return questions


# ============================================================
# DATABASE-PERSISTED INTERVIEW SESSIONS
# ============================================================

def create_interview_session(
    db: Session,
    questions: List[InterviewQuestion],
    target_role: str,
    interview_type: str,
    difficulty: str,
    company: Optional[str] = None,
    user_id: Optional[int] = None,
) -> InterviewSession:
    """
    Create and persist a new interview session in SQLite database.
    """
    normalized_company = normalize_company(company)

    questions_data = [
        {
            "question_id": q.question_id,
            "question": q.question,
            "category": q.category,
            "difficulty": q.difficulty,
            "company": q.company,
        }
        for q in questions
    ]

    session = InterviewSession(
        user_id=user_id,
        company=normalized_company,
        target_role=target_role,
        interview_type=interview_type,
        difficulty=difficulty,
        current_index=0,
        total_questions=len(questions),
        questions_json=json.dumps(questions_data),
        status="in_progress",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_interview_session(
    db: Session,
    interview_id: int,
) -> Optional[InterviewSession]:
    """
    Retrieve an active or completed interview session from database.
    """
    return (
        db.query(InterviewSession)
        .filter(InterviewSession.id == interview_id)
        .first()
    )


def save_interview_evaluation(
    db: Session,
    interview_id: int,
    question_id: int,
    answer: str,
    evaluation: InterviewEvaluation,
):
    """
    Save an interview answer evaluation to database.
    """
    session = get_interview_session(db, interview_id)

    if session is None:
        return None

    questions = json.loads(session.questions_json)

    question_text = ""
    category = "general"

    for q in questions:
        if q.get("question_id") == question_id:
            question_text = q.get("question", "")
            category = q.get("category", "general")
            break

    eval_data = (
        evaluation.model_dump()
        if hasattr(evaluation, "model_dump")
        else evaluation.__dict__
    )

    qa = InterviewQuestionAnswer(
        session_id=session.id,
        question_id=question_id,
        question_text=question_text,
        category=category,
        user_answer=answer,
        score=float(evaluation.score),
        evaluation_json=json.dumps(eval_data),
    )

    db.add(qa)

    session.current_index += 1

    if session.current_index >= len(questions):
        session.status = "completed"
        db.commit()
        db.refresh(session)
        _persist_interview_result(db, session)
    else:
        db.commit()
        db.refresh(session)

    return session


def _get_performance_level(score: float) -> str:
    if score >= 80:
        return "excellent"
    if score >= 65:
        return "good"
    if score >= 50:
        return "developing"
    return "needs_improvement"


def _persist_interview_result(db: Session, session: InterviewSession) -> None:
    """Persist completed interview result for placement readiness calculations."""
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

    average_score = round(
        sum(a.score for a in answers) / len(answers),
        2,
    )

    result = (
        db.query(InterviewResult)
        .filter(
            InterviewResult.user_id == user_id,
            InterviewResult.interview_id == session.id,
        )
        .first()
    )

    if result is None:
        result = InterviewResult(
            user_id=user_id,
            interview_id=session.id,
        )
        db.add(result)

    questions = json.loads(session.questions_json)

    result.company = session.company
    result.target_role = session.target_role
    result.interview_type = session.interview_type
    result.difficulty = session.difficulty
    result.completed_questions = len(answers)
    result.total_questions = len(questions)
    result.average_score = average_score
    result.performance_level = _get_performance_level(average_score)

    db.commit()


def get_next_question(
    db: Session,
    interview_id: int,
) -> Optional[InterviewQuestion]:
    """
    Return the next unanswered question for an interview session.
    """
    session = get_interview_session(db, interview_id)

    if session is None:
        return None

    questions = json.loads(session.questions_json)

    if session.current_index >= len(questions):
        return None

    q_data = questions[session.current_index]

    return InterviewQuestion(
        question_id=q_data["question_id"],
        question=q_data["question"],
        category=q_data["category"],
        difficulty=q_data["difficulty"],
        company=q_data.get("company"),
    )


def evaluate_answer(
    question: str,
    answer: str,
    category: str,
    company: Optional[str] = None,
    difficulty: str = "medium",
) -> InterviewEvaluation:
    """
    Evaluate an interview answer using the AI evaluator.
    """
    return evaluator.evaluate(
        question=question,
        answer=answer,
        category=category,
        company=company,
        difficulty=difficulty,
    )


def get_interview_summary(
    db: Session,
    interview_id: int,
):
    """
    Calculate current/final interview summary from persistent session records.
    """
    session = get_interview_session(db, interview_id)

    if session is None:
        return None

    answers = (
        db.query(InterviewQuestionAnswer)
        .filter(InterviewQuestionAnswer.session_id == session.id)
        .all()
    )

    completed = len(answers)
    questions = json.loads(session.questions_json)
    total = len(questions)

    if answers:
        average_score = round(
            sum(a.score for a in answers) / completed,
            2,
        )
    else:
        average_score = 0.0

    if completed > 0 and completed >= total:
        _persist_interview_result(db, session)

    return {
        "interview_id": session.id,
        "company": session.company,
        "target_role": session.target_role,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "completed_questions": completed,
        "total_questions": total,
        "average_score": average_score,
        "completed": completed >= total,
    }