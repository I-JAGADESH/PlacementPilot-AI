from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from sklearn.ensemble import RandomForestRegressor


FEATURE_NAMES = [
    "cgpa",
    "attendance",
    "backlogs",
    "aptitude_score",
    "communication_score",
    "skill_score",
    "project_score",
    "certification_score",
    "ats_score",
    "interview_score",
]


@dataclass
class ReadinessPrediction:
    score: float
    level: str
    probability: float
    factors: Dict[str, float]
    recommendations: List[str]


class PlacementReadinessModel:
    """
    Lightweight ML-based placement readiness predictor.

    The model is intentionally self-contained for the first version.
    It uses a synthetic baseline dataset to learn reasonable feature
    relationships. Real student outcomes can replace this training data
    later without changing the prediction interface.
    """

    def __init__(self) -> None:
        self.model = RandomForestRegressor(
            n_estimators=150,
            max_depth=8,
            random_state=42,
        )
        self._train()

    def _train(self) -> None:
        rng = np.random.default_rng(42)

        rows = []
        targets = []

        for _ in range(1000):
            cgpa = rng.uniform(5.0, 10.0)
            attendance = rng.uniform(50.0, 100.0)
            backlogs = rng.integers(0, 5)
            aptitude = rng.uniform(25.0, 100.0)
            communication = rng.uniform(25.0, 100.0)
            skill = rng.uniform(20.0, 100.0)
            projects = rng.uniform(20.0, 100.0)
            certifications = rng.uniform(0.0, 100.0)
            ats = rng.uniform(20.0, 100.0)
            interview = rng.uniform(20.0, 100.0)

            score = (
                cgpa / 10.0 * 15.0
                + attendance / 100.0 * 5.0
                + max(0.0, 1.0 - backlogs / 5.0) * 5.0
                + aptitude / 100.0 * 12.0
                + communication / 100.0 * 10.0
                + skill / 100.0 * 18.0
                + projects / 100.0 * 10.0
                + certifications / 100.0 * 5.0
                + ats / 100.0 * 8.0
                + interview / 100.0 * 12.0
            )

            noise = rng.normal(0.0, 3.0)
            score = float(np.clip(score + noise, 0.0, 100.0))

            rows.append(
                [
                    cgpa,
                    attendance,
                    backlogs,
                    aptitude,
                    communication,
                    skill,
                    projects,
                    certifications,
                    ats,
                    interview,
                ]
            )
            targets.append(score)

        self.model.fit(np.asarray(rows), np.asarray(targets))

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(float(value), maximum))

    def predict(
        self,
        cgpa: float = 0.0,
        attendance: float = 0.0,
        backlogs: int = 0,
        aptitude_score: float = 0.0,
        communication_score: float = 0.0,
        skill_score: float = 0.0,
        project_score: float = 0.0,
        certification_score: float = 0.0,
        ats_score: float = 0.0,
        interview_score: float = 0.0,
    ) -> ReadinessPrediction:
        values = {
            "cgpa": self._clamp(cgpa, 0.0, 10.0),
            "attendance": self._clamp(attendance, 0.0, 100.0),
            "backlogs": max(0, int(backlogs)),
            "aptitude_score": self._clamp(aptitude_score, 0.0, 100.0),
            "communication_score": self._clamp(
                communication_score, 0.0, 100.0
            ),
            "skill_score": self._clamp(skill_score, 0.0, 100.0),
            "project_score": self._clamp(project_score, 0.0, 100.0),
            "certification_score": self._clamp(
                certification_score, 0.0, 100.0
            ),
            "ats_score": self._clamp(ats_score, 0.0, 100.0),
            "interview_score": self._clamp(
                interview_score, 0.0, 100.0
            ),
        }

        features = np.asarray(
            [[values[name] for name in FEATURE_NAMES]],
            dtype=float,
        )

        prediction = float(
            np.clip(self.model.predict(features)[0], 0.0, 100.0)
        )

        if prediction >= 80:
            level = "placement_ready"
        elif prediction >= 65:
            level = "nearly_ready"
        elif prediction >= 45:
            level = "developing"
        else:
            level = "needs_improvement"

        probability = round(
            min(0.99, max(0.05, prediction / 100.0)),
            3,
        )

        factors = self._build_factors(values)
        recommendations = self._build_recommendations(values)

        return ReadinessPrediction(
            score=round(prediction, 2),
            level=level,
            probability=probability,
            factors=factors,
            recommendations=recommendations,
        )

    def _build_factors(self, values: Dict[str, float]) -> Dict[str, float]:
        normalized = {
            "cgpa": values["cgpa"] / 10.0 * 100.0,
            "attendance": values["attendance"],
            "backlogs": max(0.0, 100.0 - values["backlogs"] * 25.0),
            "aptitude": values["aptitude_score"],
            "communication": values["communication_score"],
            "skills": values["skill_score"],
            "projects": values["project_score"],
            "certifications": values["certification_score"],
            "ats": values["ats_score"],
            "interview": values["interview_score"],
        }

        return {
            key: round(float(value), 2)
            for key, value in normalized.items()
        }

    def _build_recommendations(
        self,
        values: Dict[str, float],
    ) -> List[str]:
        recommendations: List[str] = []

        checks = [
            (
                values["skill_score"],
                "Improve job-relevant technical skills.",
            ),
            (
                values["aptitude_score"],
                "Practice aptitude and logical reasoning regularly.",
            ),
            (
                values["communication_score"],
                "Improve communication through structured interview practice.",
            ),
            (
                values["project_score"],
                "Build stronger projects with measurable outcomes.",
            ),
            (
                values["ats_score"],
                "Optimize your resume for the target job description.",
            ),
            (
                values["interview_score"],
                "Complete more mock interviews and review your weak areas.",
            ),
            (
                values["certification_score"],
                "Add relevant certifications or demonstrate the skills through projects.",
            ),
        ]

        for value, recommendation in checks:
            if value < 60:
                recommendations.append(recommendation)

        if values["backlogs"] > 0:
            recommendations.append(
                "Clear pending backlogs because they can restrict placement eligibility."
            )

        if values["attendance"] < 75:
            recommendations.append(
                "Improve attendance to satisfy common placement eligibility requirements."
            )

        if not recommendations:
            recommendations.append(
                "Maintain your current preparation level and continue practicing with target-role assessments."
            )

        return recommendations[:6]


readiness_model = PlacementReadinessModel()
