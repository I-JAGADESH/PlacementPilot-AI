from typing import List

from app.assessment.question_bank import get_questions


def build_assessment_questions(skill: str) -> List[dict]:
    """
    Return assessment questions without exposing the correct answers
    to the frontend.
    """
    questions = get_questions(skill)

    return [
        {
            "id": question["id"],
            "skill": question["skill"],
            "topic": question["topic"],
            "question": question["question"],
            "options": question["options"],
        }
        for question in questions
    ]


def evaluate_assessment(skill: str, answers: List[dict]) -> dict:
    """
    Evaluate submitted answers and generate topic-wise performance.
    """

    questions = get_questions(skill)

    answer_map = {
        int(answer["question_id"]): answer["selected_option"]
        for answer in answers
    }

    total_questions = len(questions)
    correct_answers = 0

    topic_stats = {}

    for question in questions:
        question_id = question["id"]
        topic = question["topic"]

        if topic not in topic_stats:
            topic_stats[topic] = {
                "total_questions": 0,
                "correct_answers": 0,
            }

        topic_stats[topic]["total_questions"] += 1

        selected_option = answer_map.get(question_id)

        if selected_option == question["answer"]:
            correct_answers += 1
            topic_stats[topic]["correct_answers"] += 1

    score_percentage = (
        round((correct_answers / total_questions) * 100, 2)
        if total_questions
        else 0.0
    )

    topic_performance = []

    for topic, stats in topic_stats.items():
        topic_score = (
            round(
                (stats["correct_answers"] / stats["total_questions"]) * 100,
                2,
            )
            if stats["total_questions"]
            else 0.0
        )

        topic_performance.append(
            {
                "topic": topic,
                "total_questions": stats["total_questions"],
                "correct_answers": stats["correct_answers"],
                "score_percentage": topic_score,
            }
        )

    strong_topics = [
        item["topic"]
        for item in topic_performance
        if item["score_percentage"] >= 70
    ]

    weak_topics = [
        item["topic"]
        for item in topic_performance
        if item["score_percentage"] < 70
    ]

    if score_percentage >= 85:
        performance_level = "Excellent"
    elif score_percentage >= 70:
        performance_level = "Strong"
    elif score_percentage >= 50:
        performance_level = "Developing"
    else:
        performance_level = "Needs Improvement"

    recommendations = []

    if score_percentage < 70:
        recommendations.append(
            f"Review the core concepts of {skill} before attempting another assessment."
        )

    if weak_topics:
        recommendations.append(
            "Focus your training on: " + ", ".join(weak_topics) + "."
        )

    if strong_topics:
        recommendations.append(
            "Maintain your strength in: " + ", ".join(strong_topics) + "."
        )

    if score_percentage >= 85:
        recommendations.append(
            "You have demonstrated strong understanding. Move to harder "
            "practice questions and technical interviews."
        )
    elif score_percentage >= 70:
        recommendations.append(
            "Your foundation is good. Strengthen weak topics and continue "
            "with interview-level problems."
        )
    else:
        recommendations.append(
            "Complete the relevant Personalized Training topics and retry "
            "the assessment."
        )

    return {
        "skill": skill,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score_percentage": score_percentage,
        "performance_level": performance_level,
        "topic_performance": topic_performance,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "recommendations": recommendations,
    }