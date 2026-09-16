"""
Question Validation Layer for PlacementPilot AI Aptitude Engine.
Ensures no invalid, unverified, or mathematically flawed questions are served.
"""

from typing import Any, Dict, List, Tuple

from app.aptitude.taxonomy import get_all_subtopic_slugs

VALID_DIFFICULTIES = {"Easy", "Medium", "Hard", "Expert"}
VALID_TYPES = {"MCQ", "Numerical", "Data Interpretation", "Multi-step Reasoning"}


class QuestionValidationError(Exception):
    pass


def validate_question_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a question dict against schema, taxonomy, options, and math consistency rules.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    # Required fields check
    required_fields = [
        "subtopic_slug",
        "difficulty",
        "question_type",
        "question_text",
        "correct_answer",
        "explanation",
        "estimated_time_seconds",
    ]

    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            errors.append(f"Missing or empty required field: '{field}'")

    # Taxonomy reference check
    valid_subtopic_slugs = set(get_all_subtopic_slugs())
    if data.get("subtopic_slug") not in valid_subtopic_slugs:
        errors.append(
            f"Invalid subtopic_slug: '{data.get('subtopic_slug')}'. Must belong to normalized taxonomy."
        )

    # Difficulty check
    if data.get("difficulty") not in VALID_DIFFICULTIES:
        errors.append(
            f"Invalid difficulty: '{data.get('difficulty')}'. Must be one of {sorted(VALID_DIFFICULTIES)}."
        )

    # Question type check
    if data.get("question_type") not in VALID_TYPES:
        errors.append(
            f"Invalid question_type: '{data.get('question_type')}'. Must be one of {sorted(VALID_TYPES)}."
        )

    # Estimated time check
    if not isinstance(data.get("estimated_time_seconds"), (int, float)) or data.get("estimated_time_seconds", 0) <= 0:
        errors.append("estimated_time_seconds must be a positive number.")

    # Negative marking check
    neg_mark = data.get("negative_marking", 0.0)
    if not isinstance(neg_mark, (int, float)) or neg_mark < 0:
        errors.append("negative_marking cannot be negative.")

    # MCQ Option & Answer validation
    if data.get("question_type") == "MCQ":
        options = data.get("options")
        if not options or not isinstance(options, list) or len(options) < 2:
            errors.append("MCQ question must provide at least 2 options.")
        else:
            option_texts = [str(opt).strip() for opt in options]
            if len(set(option_texts)) != len(option_texts):
                errors.append("MCQ options must be unique.")

            correct_ans = str(data.get("correct_answer", "")).strip()
            if correct_ans not in option_texts:
                errors.append(
                    f"Correct answer '{correct_ans}' must be present in MCQ options list: {option_texts}"
                )

    # Numerical Answer validation
    elif data.get("question_type") == "Numerical":
        correct_ans = str(data.get("correct_answer", "")).strip()
        try:
            float(correct_ans)
        except ValueError:
            errors.append(f"Numerical answer '{correct_ans}' is not a valid number.")

    # Generated answer mathematical verification callback check
    if data.get("is_generated") and "expected_math_check" in data:
        expected = data["expected_math_check"]
        actual = data.get("correct_answer")
        if str(expected).strip() != str(actual).strip():
            errors.append(
                f"Generated question math mismatch: expected '{expected}', got '{actual}'."
            )

    return len(errors) == 0, errors
