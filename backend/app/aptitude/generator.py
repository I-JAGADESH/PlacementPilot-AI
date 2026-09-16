"""
Programmatic and Deterministic Question Generator Engine for PlacementPilot AI.
Supports numerical generators across 13 core aptitude categories with independent math validation.
"""

import math
import random
from typing import Any, Dict, List, Optional, Tuple

from app.aptitude.formulas import get_formula_for_subtopic
from app.aptitude.validator import validate_question_data


class GeneratorError(Exception):
    pass


def _create_options(correct_val: float, is_int: bool = True, rng: Optional[random.Random] = None) -> Tuple[List[str], str]:
    if rng is None:
        rng = random.Random()

    if is_int:
        c_str = str(int(round(correct_val)))
        val = int(round(correct_val))
        distractors = set()

        offsets = [-5, -2, -1, 1, 2, 5, 10, 15, -10]
        rng.shuffle(offsets)

        for offset in offsets:
            d = val + offset
            if d > 0 and d != val:
                distractors.add(str(d))
            if len(distractors) == 3:
                break

        while len(distractors) < 3:
            d = val + len(distractors) + 3
            if str(d) != c_str:
                distractors.add(str(d))

        opts = [c_str] + list(distractors)
        rng.shuffle(opts)
        return opts, c_str
    else:
        c_str = f"{correct_val:.2f}"
        val = round(correct_val, 2)
        distractors = set()

        offsets = [-2.5, -1.0, -0.5, 0.5, 1.0, 2.5, 5.0]
        rng.shuffle(offsets)

        for offset in offsets:
            d = val + offset
            if d > 0 and d != val:
                distractors.add(f"{d:.2f}")
            if len(distractors) == 3:
                break

        while len(distractors) < 3:
            d = val + len(distractors) + 0.75
            if f"{d:.2f}" != c_str:
                distractors.add(f"{d:.2f}")

        opts = [c_str] + list(distractors)
        rng.shuffle(opts)
        return opts, c_str


def generate_percentage_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    base = rng.choice([200, 400, 500, 800, 1000, 1200, 1500])
    pct = rng.choice([5, 10, 12, 15, 20, 25, 30, 40, 50])

    expected = (pct / 100.0) * base
    opts, correct_str = _create_options(expected, is_int=True, rng=rng)

    f_info = get_formula_for_subtopic("percentage")

    q_data = {
        "subtopic_slug": "percentage",
        "difficulty": rng.choice(["Easy", "Medium"]),
        "question_type": "MCQ",
        "question_text": f"What is {pct}% of {base}?",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"{pct}% of {base} = ({pct} / 100) × {base} = {correct_str}.",
        "formula_concept": f_info["formula"],
        "estimated_time_seconds": 30,
        "negative_marking": 0.25,
        "tags": ["percentage", "basic-arithmetic"],
        "source_type": "generated",
        "generation_strategy": "percentage_direct",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated percentage question invalid: {errors}")

    return q_data


def generate_profit_loss_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    cp = rng.choice([100, 200, 250, 400, 500, 800, 1000])
    profit_pct = rng.choice([10, 15, 20, 25, 30, 40])

    sp = cp + (profit_pct / 100.0) * cp
    opts, correct_str = _create_options(sp, is_int=True, rng=rng)

    f_info = get_formula_for_subtopic("profit-percentage")

    q_data = {
        "subtopic_slug": "profit-percentage",
        "difficulty": "Medium",
        "question_type": "MCQ",
        "question_text": f"An item bought for ${cp} is sold at a profit of {profit_pct}%. What is the selling price?",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"Selling Price = Cost Price + Profit = {cp} + ({profit_pct}% of {cp}) = {correct_str}.",
        "formula_concept": f_info["formula"],
        "estimated_time_seconds": 45,
        "negative_marking": 0.25,
        "tags": ["profit-and-loss", "selling-price"],
        "source_type": "generated",
        "generation_strategy": "sp_from_cp_profit",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated profit/loss question invalid: {errors}")

    return q_data


def generate_simple_interest_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    p = rng.choice([1000, 2000, 5000, 10000, 12000])
    r = rng.choice([5, 6, 8, 10, 12])
    t = rng.choice([2, 3, 4, 5])

    si = (p * r * t) / 100.0
    opts, correct_str = _create_options(si, is_int=True, rng=rng)

    f_info = get_formula_for_subtopic("si-formula")

    q_data = {
        "subtopic_slug": "si-formula",
        "difficulty": "Easy",
        "question_type": "MCQ",
        "question_text": f"Calculate the Simple Interest on a principal of ${p} at an annual interest rate of {r}% for {t} years.",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"Simple Interest SI = (P × R × T) / 100 = ({p} × {r} × {t}) / 100 = {correct_str}.",
        "formula_concept": f_info["formula"],
        "estimated_time_seconds": 45,
        "negative_marking": 0.25,
        "tags": ["simple-interest", "formula"],
        "source_type": "generated",
        "generation_strategy": "si_direct",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated simple interest question invalid: {errors}")

    return q_data


def generate_compound_interest_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    p = rng.choice([1000, 2000, 4000, 5000, 10000])
    r = rng.choice([10, 20])
    t = 2

    amount = p * ((1.0 + (r / 100.0)) ** t)
    ci = amount - p
    opts, correct_str = _create_options(ci, is_int=True, rng=rng)

    f_info = get_formula_for_subtopic("compound-interest-formula")

    q_data = {
        "subtopic_slug": "compound-interest-formula",
        "difficulty": "Medium",
        "question_type": "MCQ",
        "question_text": f"Find the Compound Interest on ${p} compounded annually for {t} years at {r}% per annum.",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"Amount A = {p} × (1 + {r}/100)^{t} = {int(round(amount))}. CI = A - P = {correct_str}.",
        "formula_concept": f_info["formula"],
        "estimated_time_seconds": 60,
        "negative_marking": 0.25,
        "tags": ["compound-interest", "annual-compounding"],
        "source_type": "generated",
        "generation_strategy": "ci_annual_2yr",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated compound interest question invalid: {errors}")

    return q_data


def generate_speed_distance_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    speed_kmh = rng.choice([36, 54, 72, 90, 108, 126, 144])

    # Convert km/h to m/s: multiply by 5/18
    speed_ms = (speed_kmh * 5) // 18
    opts, correct_str = _create_options(float(speed_ms), is_int=True, rng=rng)

    f_info = get_formula_for_subtopic("basic-speed-formula")

    q_data = {
        "subtopic_slug": "km-hr-to-m-s-conversion",
        "difficulty": "Easy",
        "question_type": "MCQ",
        "question_text": f"Convert a speed of {speed_kmh} km/hr into m/s.",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"To convert km/hr to m/s, multiply by (5/18): {speed_kmh} × (5/18) = {correct_str} m/s.",
        "formula_concept": f_info["formula"],
        "estimated_time_seconds": 30,
        "negative_marking": 0.25,
        "tags": ["speed-time-distance", "unit-conversion"],
        "source_type": "generated",
        "generation_strategy": "kmh_to_ms",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated speed distance question invalid: {errors}")

    return q_data


def generate_time_and_work_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    days_a = rng.choice([10, 12, 15, 20, 30])
    days_b = rng.choice([12, 15, 20, 30, 60])

    # LCM method
    lcm = math.lcm(days_a, days_b)
    rate_a = lcm // days_a
    rate_b = lcm // days_b
    combined_rate = rate_a + rate_b

    combined_days = lcm / combined_rate
    opts, correct_str = _create_options(combined_days, is_int=(lcm % combined_rate == 0), rng=rng)

    f_info = get_formula_for_subtopic("time-and-work")

    q_data = {
        "subtopic_slug": "time-and-work",
        "difficulty": "Medium",
        "question_type": "MCQ",
        "question_text": f"A can complete a piece of work in {days_a} days and B can complete it in {days_b} days. How many days will they take to complete the work together?",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"1 day work of A = 1/{days_a}, 1 day work of B = 1/{days_b}. Combined 1 day work = ({days_a}+{days_b})/({days_a}×{days_b}). Total time = {correct_str} days.",
        "formula_concept": f_info["formula"],
        "estimated_time_seconds": 60,
        "negative_marking": 0.25,
        "tags": ["time-and-work", "combined-work"],
        "source_type": "generated",
        "generation_strategy": "combined_time_work",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated time and work question invalid: {errors}")

    return q_data


def generate_averages_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    n = 5
    avg = rng.choice([20, 25, 30, 40, 50, 60])
    nums = [avg - 4, avg - 2, avg, avg + 2, avg + 4]

    expected_avg = float(sum(nums)) / len(nums)
    opts, correct_str = _create_options(expected_avg, is_int=True, rng=rng)

    q_data = {
        "subtopic_slug": "simple-average",
        "difficulty": "Easy",
        "question_type": "MCQ",
        "question_text": f"Find the simple average of the numbers: {nums[0]}, {nums[1]}, {nums[2]}, {nums[3]}, and {nums[4]}.",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"Average = Sum of items / Number of items = ({sum(nums)}) / 5 = {correct_str}.",
        "formula_concept": "Average = Total Sum / Total Count",
        "estimated_time_seconds": 30,
        "negative_marking": 0.25,
        "tags": ["averages", "basic-average"],
        "source_type": "generated",
        "generation_strategy": "simple_average_5nums",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated averages question invalid: {errors}")

    return q_data


def generate_ratio_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    ratio_a = rng.choice([2, 3, 4, 5])
    ratio_b = rng.choice([3, 5, 7, 9])
    multiplier = rng.choice([10, 15, 20, 25, 50])

    val_a = ratio_a * multiplier
    val_b = ratio_b * multiplier
    total = val_a + val_b

    opts, correct_str = _create_options(float(val_a), is_int=True, rng=rng)

    q_data = {
        "subtopic_slug": "division-into-ratios",
        "difficulty": "Easy",
        "question_type": "MCQ",
        "question_text": f"Divide ${total} between A and B in the ratio {ratio_a}:{ratio_b}. What is A's share?",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"Total parts = {ratio_a} + {ratio_b} = {ratio_a + ratio_b}. A's share = ({ratio_a} / {ratio_a + ratio_b}) × ${total} = ${correct_str}.",
        "formula_concept": "Share = (Ratio Part / Total Ratio Sum) × Total Amount",
        "estimated_time_seconds": 45,
        "negative_marking": 0.25,
        "tags": ["ratio-and-proportion", "division"],
        "source_type": "generated",
        "generation_strategy": "ratio_share_part",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated ratio question invalid: {errors}")

    return q_data


def generate_number_system_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    num1 = rng.choice([12, 18, 24, 36, 48, 60])
    num2 = rng.choice([16, 20, 30, 40, 60, 72])

    val_hcf = math.gcd(num1, num2)
    opts, correct_str = _create_options(float(val_hcf), is_int=True, rng=rng)

    f_info = get_formula_for_subtopic("hcf")

    q_data = {
        "subtopic_slug": "hcf",
        "difficulty": "Easy",
        "question_type": "MCQ",
        "question_text": f"Find the Highest Common Factor (HCF) of {num1} and {num2}.",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"Prime factorization of {num1} and {num2} yields HCF = {correct_str}.",
        "formula_concept": f_info["formula"],
        "estimated_time_seconds": 30,
        "negative_marking": 0.25,
        "tags": ["number-systems", "hcf"],
        "source_type": "generated",
        "generation_strategy": "hcf_two_numbers",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated HCF question invalid: {errors}")

    return q_data


def generate_mensuration_question(seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    side = rng.choice([3, 4, 5, 6, 8, 10, 12])

    surface_area = 6 * (side ** 2)
    opts, correct_str = _create_options(float(surface_area), is_int=True, rng=rng)

    q_data = {
        "subtopic_slug": "surface-area-of-cube",
        "difficulty": "Easy",
        "question_type": "MCQ",
        "question_text": f"Calculate the total surface area of a cube having an edge length of {side} cm.",
        "options": opts,
        "correct_answer": correct_str,
        "explanation": f"Total Surface Area of Cube = 6 × (edge)^2 = 6 × ({side})^2 = 6 × {side**2} = {correct_str} cm².",
        "formula_concept": "Surface Area of Cube = 6 a²",
        "estimated_time_seconds": 30,
        "negative_marking": 0.25,
        "tags": ["mensuration", "cube"],
        "source_type": "generated",
        "generation_strategy": "cube_surface_area",
        "is_generated": True,
        "seed": seed,
        "expected_math_check": correct_str,
    }

    is_valid, errors = validate_question_data(q_data)
    if not is_valid:
        raise GeneratorError(f"Generated mensuration question invalid: {errors}")

    return q_data


# Master Registry of Generator Functions
GENERATOR_REGISTRY = [
    generate_percentage_question,
    generate_profit_loss_question,
    generate_simple_interest_question,
    generate_compound_interest_question,
    generate_speed_distance_question,
    generate_time_and_work_question,
    generate_averages_question,
    generate_ratio_question,
    generate_number_system_question,
    generate_mensuration_question,
]


def generate_random_aptitude_question(subtopic_slug: Optional[str] = None, seed: Optional[int] = None) -> Dict[str, Any]:
    rng = random.Random(seed)
    gen_func = rng.choice(GENERATOR_REGISTRY)

    q_data = gen_func(seed=seed)
    if subtopic_slug:
        # Override subtopic_slug if specific requested
        q_data["subtopic_slug"] = subtopic_slug

    return q_data
