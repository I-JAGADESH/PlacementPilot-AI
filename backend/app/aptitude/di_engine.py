"""
Data Interpretation Engine for PlacementPilot AI Aptitude Engine.
Supports shared DI datasets (tables, growth, ratios, percentages) across multiple questions.
"""

import json
from typing import Any, Dict, List


SAMPLE_DI_DATASETS: List[Dict[str, Any]] = [
    {
        "title": "Quarterly Revenue & Profitability Analysis (2024)",
        "description": "Financial summary of TechCorp Inc. across four quarters in USD Millions.",
        "dataset_type": "table",
        "content_json": json.dumps({
            "columns": ["Quarter", "Revenue ($M)", "Operating Cost ($M)", "Tax Rate (%)"],
            "rows": [
                ["Q1", 120, 80, 20],
                ["Q2", 150, 90, 20],
                ["Q3", 180, 110, 25],
                ["Q4", 200, 120, 25],
            ],
        }),
        "questions": [
            {
                "subtopic_slug": "data-interpretation",
                "difficulty": "Medium",
                "question_type": "Data Interpretation",
                "question_text": "Based on the table, what was the gross profit (Revenue - Operating Cost) for Q2 in USD Millions?",
                "options": ["50", "60", "70", "80"],
                "correct_answer": "60",
                "explanation": "Q2 Gross Profit = Revenue ($150M) - Operating Cost ($90M) = $60M.",
                "formula_concept": "Profit = Revenue - Operating Cost",
                "estimated_time_seconds": 45,
                "negative_marking": 0.25,
                "tags": ["data-interpretation", "table", "profit"],
                "source_type": "static",
            },
            {
                "subtopic_slug": "percentage-and-population",
                "difficulty": "Hard",
                "question_type": "Data Interpretation",
                "question_text": "What was the percentage growth in Revenue from Q1 to Q4?",
                "options": ["50.00%", "60.00%", "66.67%", "75.00%"],
                "correct_answer": "66.67%",
                "explanation": "Percentage Growth = ((Q4 Revenue - Q1 Revenue) / Q1 Revenue) × 100 = ((200 - 120) / 120) × 100 = 66.67%.",
                "formula_concept": "Growth % = ((Final - Initial) / Initial) × 100",
                "estimated_time_seconds": 60,
                "negative_marking": 0.25,
                "tags": ["data-interpretation", "growth", "percentage"],
                "source_type": "static",
            },
        ],
    },
    {
        "title": "Placement Campus Recruitment Demographics (2025)",
        "description": "Student placement statistics across different engineering streams.",
        "dataset_type": "table",
        "content_json": json.dumps({
            "columns": ["Stream", "Total Students", "Placed Students", "Avg Package (LPA)"],
            "rows": [
                ["CSE", 300, 270, 12.5],
                ["ECE", 200, 160, 9.0],
                ["MECH", 150, 105, 7.5],
                ["EEE", 150, 120, 8.0],
            ],
        }),
        "questions": [
            {
                "subtopic_slug": "data-interpretation",
                "difficulty": "Medium",
                "question_type": "Data Interpretation",
                "question_text": "Which stream recorded the highest placement percentage?",
                "options": ["CSE", "ECE", "MECH", "EEE"],
                "correct_answer": "CSE",
                "explanation": "CSE: (270/300)*100 = 90%; ECE: (160/200)*100 = 80%; MECH: (105/150)*100 = 70%; EEE: (120/150)*100 = 80%. CSE is highest at 90%.",
                "formula_concept": "Placement % = (Placed / Total) × 100",
                "estimated_time_seconds": 45,
                "negative_marking": 0.25,
                "tags": ["data-interpretation", "placement", "ratios"],
                "source_type": "static",
            }
        ],
    },
]
