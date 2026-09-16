"""
Formula and Reference System for PlacementPilot AI Aptitude Engine.
Provides formula definitions, concept summaries, when-to-use tips, and common traps.
"""

from typing import Dict, TypedDict


class FormulaData(TypedDict):
    title: str
    formula: str
    concept_summary: str
    when_to_use: str
    important_notes: str
    common_traps: str


FORMULA_DATABASE: Dict[str, FormulaData] = {
    "divisibility-rules": {
        "title": "Divisibility Rules Reference",
        "formula": "Rule for 3 & 9: Sum of digits; Rule for 4 & 8: Last 2 & 3 digits; Rule for 11: Alternating sum of digits = 0 or multiple of 11.",
        "concept_summary": "Divisibility tests allow rapid verification without full division.",
        "when_to_use": "Use when simplifying large fractions or solving remainder problems.",
        "important_notes": "A number divisible by coprime factors a and b is divisible by a × b.",
        "common_traps": "Combining divisibility of non-coprime numbers (e.g. 6 is 2×3, but 12 needs 3×4 not 2×6).",
    },
    "lcm": {
        "title": "Lowest Common Multiple (LCM)",
        "formula": "LCM(a, b) = (a × b) / HCF(a, b); For fractions: LCM = LCM(numerators) / HCF(denominators).",
        "concept_summary": "The smallest positive integer divisible by all given numbers.",
        "when_to_use": "Use in alternating work, traffic light blinking, or adding fractions.",
        "important_notes": "Always simplify fraction terms before applying fraction LCM formulas.",
        "common_traps": "Confusing LCM formula for fractions with HCF formula for fractions.",
    },
    "hcf": {
        "title": "Highest Common Factor (HCF / GCD)",
        "formula": "HCF(a, b) × LCM(a, b) = a × b; For fractions: HCF = HCF(numerators) / LCM(denominators).",
        "concept_summary": "The greatest integer dividing all given numbers without a remainder.",
        "when_to_use": "Use when grouping items into equal maximum sizes.",
        "important_notes": "HCF of consecutive integers is always 1.",
        "common_traps": "Assuming product formula HCF×LCM=a×b works for three or more numbers (it applies directly only to two numbers).",
    },
    "percentage": {
        "title": "Basic Percentage Formula",
        "formula": "Percentage = (Part / Whole) × 100",
        "concept_summary": "Percentage represents a fraction out of 100.",
        "when_to_use": "Use when calculating ratio parts relative to total base.",
        "important_notes": "Always identify the correct base denominator.",
        "common_traps": "Changing base values across multi-step percentage changes.",
    },
    "profit-percentage": {
        "title": "Profit Percentage Formula",
        "formula": "Profit % = ((Selling Price - Cost Price) / Cost Price) × 100",
        "concept_summary": "Profit percentage measures financial gain relative to Cost Price unless specified.",
        "when_to_use": "Use to calculate percentage return on investment or product sales.",
        "important_notes": "Cost Price is standard base for profit percentage calculations.",
        "common_traps": "Dividing profit by Selling Price instead of Cost Price.",
    },
    "cp-of-m-sp-of-n": {
        "title": "CP of m Articles = SP of n Articles",
        "formula": "Profit % = ((m - n) / n) × 100 if m > n; Loss % = ((n - m) / n) × 100 if n > m.",
        "concept_summary": "Relates article count directly to percentage gain or loss.",
        "when_to_use": "Use when question equates cost of m items to revenue from n items.",
        "important_notes": "The denominator is always n (number of articles sold).",
        "common_traps": "Using m in the denominator instead of n.",
    },
    "si-formula": {
        "title": "Simple Interest Formula",
        "formula": "SI = (P × R × T) / 100; Total Amount A = P + SI = P (1 + RT/100)",
        "concept_summary": "Interest accumulated linearly on original principal over time.",
        "when_to_use": "Use when interest rate is calculated solely on original capital.",
        "important_notes": "Time T must be in years; Rate R must be annual percentage.",
        "common_traps": "Forgetting to convert months to fraction of years (e.g. 6 months = 0.5 years).",
    },
    "compound-interest-formula": {
        "title": "Compound Interest Formula",
        "formula": "A = P (1 + R / (100 × n))^(n × t); CI = A - P",
        "concept_summary": "Interest accrued on principal plus accumulated interest.",
        "when_to_use": "Use when compounding periodically (annual n=1, half-yearly n=2, quarterly n=4).",
        "important_notes": "Adjust rate R/n and periods n*t for half-yearly or quarterly compounding.",
        "common_traps": "Applying annual compounding rate directly to quarterly periods.",
    },
    "ci-and-si-difference-for-2-years": {
        "title": "CI and SI Difference for 2 Years",
        "formula": "Difference D = P × (R / 100)^2",
        "concept_summary": "Direct relation for 2-year difference between CI and SI at rate R.",
        "when_to_use": "Use to quickly calculate principal P or rate R when 2-year CI-SI difference is given.",
        "important_notes": "Valid strictly for 2 annual periods.",
        "common_traps": "Using this 2-year shortcut for 3-year difference problems.",
    },
    "basic-speed-formula": {
        "title": "Basic Speed, Distance and Time",
        "formula": "Speed = Distance / Time; Distance = Speed × Time; Time = Distance / Speed",
        "concept_summary": "Linear relationship governing uniform motion.",
        "when_to_use": "Use for basic rate-time-distance conversions and calculations.",
        "important_notes": "Conversion factor: 1 km/h = 5/18 m/s; 1 m/s = 18/5 km/h.",
        "common_traps": "Mixing m/s with km/h without converting units.",
    },
    "average-speed": {
        "title": "Average Speed Formula",
        "formula": "Average Speed = Total Distance / Total Time; For equal distances: 2xy / (x + y)",
        "concept_summary": "Harmonic mean of speeds when distances covered are equal.",
        "when_to_use": "Use when traveling equal distances at two different speeds x and y.",
        "important_notes": "Average speed is NOT simple arithmetic mean (x+y)/2 unless time intervals are equal.",
        "common_traps": "Averaging speeds directly ((x+y)/2) for equal distance journeys.",
    },
    "time-and-work": {
        "title": "Time and Work LCM Method",
        "formula": "Total Work = LCM(Individual Days); One Day Work = Total Work / Days",
        "concept_summary": "Converts rates into integer work units for straightforward addition.",
        "when_to_use": "Use when multiple workers join, leave, or work on alternate days.",
        "important_notes": "If A completes work in x days, A's 1 day work rate is 1/x.",
        "common_traps": "Adding completion days directly instead of adding work rates.",
    },
    "pipes-and-cisterns": {
        "title": "Pipes and Cisterns Inlet/Outlet",
        "formula": "Net Rate = Inlet Rate - Outlet Rate = (1 / t_in) - (1 / t_out)",
        "concept_summary": "Inlet pipes add volume (+); outlet/leak pipes subtract volume (-).",
        "when_to_use": "Use when filling a tank with simultaneous inflow and outflow.",
        "important_notes": "If outlet rate > inlet rate, the tank empties.",
        "common_traps": "Adding leak rate instead of subtracting it from inlet rate.",
    },
    "alligation-rule": {
        "title": "Alligation Cross Rule",
        "formula": "Quantity of Cheaper / Quantity of Dearer = (Dearer Price - Mean Price) / (Mean Price - Cheaper Price)",
        "concept_summary": "Weighted average rule for mixing two ingredients at different unit costs.",
        "when_to_use": "Use when two mixtures/prices are blended to achieve a desired target price/concentration.",
        "important_notes": "All values must be on the same base (e.g. all CP, or all percentage concentration).",
        "common_traps": "Mixing CP with SP in the same alligation cross.",
    },
    "removal-and-replacement-formula": {
        "title": "Repeated Liquid Replacement Formula",
        "formula": "Final Amount of Original Liquid = Initial Amount × (1 - x / V)^n",
        "concept_summary": "Calculates remaining concentration after removing x units and replacing with another liquid n times.",
        "when_to_use": "Use when withdrawing x litres from V litres and refilling with water n times.",
        "important_notes": "V is initial total capacity; x is amount replaced per cycle; n is repetition count.",
        "common_traps": "Applying formula when replaced with a third different liquid.",
    },
}


def get_formula_for_subtopic(subtopic_slug: str) -> FormulaData:
    if subtopic_slug in FORMULA_DATABASE:
        return FORMULA_DATABASE[subtopic_slug]

    return {
        "title": f"Formula & Concept Guide for {subtopic_slug.replace('-', ' ').title()}",
        "formula": "Standard mathematical formula applies based on subtopic definitions.",
        "concept_summary": f"Fundamental aptitude concept covering {subtopic_slug.replace('-', ' ')}.",
        "when_to_use": "Use standard step-by-step arithmetic or algebraic operations.",
        "important_notes": "Pay close attention to units, ratios, and initial conditions.",
        "common_traps": "Avoid arithmetic errors and read question conditions carefully.",
    }
