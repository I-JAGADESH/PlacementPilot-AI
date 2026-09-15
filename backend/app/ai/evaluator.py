from typing import Optional
import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.interview.schemas import InterviewEvaluation


# ============================================================
# AI INTERVIEW EVALUATOR
# ============================================================

class AIInterviewEvaluator:
    """
    AI-powered interview answer evaluator.

    Gemini is used when configured.
    If Gemini fails or times out, the application
    automatically falls back to the rule-based evaluator.
    """

    def __init__(self):
        self.client = None

        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(
                    api_key=settings.GEMINI_API_KEY,
                )

            except Exception as e:
                print(
                    "Gemini client initialization failed:",
                    repr(e),
                )

    # ========================================================
    # PUBLIC EVALUATION
    # ========================================================

    def evaluate(
        self,
        question: str,
        answer: str,
        category: str,
        company: Optional[str] = None,
        difficulty: str = "medium",
    ) -> InterviewEvaluation:

        # ----------------------------------------------------
        # Empty answer
        # ----------------------------------------------------

        if not answer.strip():
            return InterviewEvaluation(
                score=0,
                strengths=[],
                weaknesses=[
                    "No answer was provided."
                ],
                feedback=(
                    "Please provide an answer "
                    "to the interview question."
                ),
                ideal_answer=(
                    "A strong answer should directly "
                    "address the question and explain "
                    "the concept clearly."
                ),
            )

        # ----------------------------------------------------
        # Gemini
        # ----------------------------------------------------

        if self.client is not None:

            try:
                return self._evaluate_with_gemini(
                    question=question,
                    answer=answer,
                    category=category,
                    company=company,
                    difficulty=difficulty,
                )

            except Exception as e:

                # Keep the interview alive even if
                # Gemini is temporarily unavailable.
                print(
                    "Gemini evaluation failed. "
                    "Using fallback evaluator."
                )
                print(
                    "Reason:",
                    repr(e),
                )

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        return self._fallback_evaluation(
            question=question,
            answer=answer,
            category=category,
        )

    # ========================================================
    # GEMINI EVALUATION
    # ========================================================

    def _evaluate_with_gemini(
        self,
        question: str,
        answer: str,
        category: str,
        company: Optional[str],
        difficulty: str,
    ) -> InterviewEvaluation:

        company_name = company or "Generic"

        prompt = f"""
You are an expert technical interviewer conducting
a placement interview.

Evaluate the candidate's answer objectively.

INTERVIEW DETAILS

Company:
{company_name}

Category:
{category}

Difficulty:
{difficulty}

QUESTION

{question}

CANDIDATE ANSWER

{answer}

EVALUATION CRITERIA

Evaluate based on:

1. Technical correctness
2. Relevance
3. Completeness
4. Clarity
5. Reasoning
6. Practical examples
7. Depth appropriate for the difficulty

SCORING

0-20   = Completely incorrect or irrelevant
21-40  = Major gaps
41-60  = Basic understanding
61-75  = Good answer with some gaps
76-90  = Strong answer
91-100 = Excellent interview-level answer

Return a JSON object containing:

score
strengths
weaknesses
feedback
ideal_answer

Rules:

- score must be between 0 and 100.
- strengths must be a JSON array of strings.
- weaknesses must be a JSON array of strings.
- feedback must be a concise explanation.
- ideal_answer must be technically correct.
- Do not reward unnecessary length.
- Focus on technical correctness.
- Include a practical example in ideal_answer when appropriate.
"""

        # ----------------------------------------------------
        # Gemini request
        # ----------------------------------------------------

        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        # ----------------------------------------------------
        # Read response
        # ----------------------------------------------------

        text = response.text.strip()

        if not text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        data = json.loads(text)

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score = float(
            data.get("score", 0)
        )

        score = max(
            0,
            min(
                100,
                score,
            ),
        )

        # ----------------------------------------------------
        # Strengths
        # ----------------------------------------------------

        strengths = data.get(
            "strengths",
            [],
        )

        if not isinstance(strengths, list):
            strengths = [
                str(strengths)
            ]

        strengths = [
            str(item)
            for item in strengths
        ]

        # ----------------------------------------------------
        # Weaknesses
        # ----------------------------------------------------

        weaknesses = data.get(
            "weaknesses",
            [],
        )

        if not isinstance(weaknesses, list):
            weaknesses = [
                str(weaknesses)
            ]

        weaknesses = [
            str(item)
            for item in weaknesses
        ]

        # ----------------------------------------------------
        # Feedback
        # ----------------------------------------------------

        feedback = str(
            data.get(
                "feedback",
                "The answer was evaluated.",
            )
        )

        # ----------------------------------------------------
        # Ideal answer
        # ----------------------------------------------------

        ideal_answer = str(
            data.get(
                "ideal_answer",
                (
                    "A strong answer should directly "
                    "address the question, explain the "
                    "concept clearly, provide reasoning, "
                    "and include an example when appropriate."
                ),
            )
        )

        # ----------------------------------------------------
        # Return evaluation
        # ----------------------------------------------------

        return InterviewEvaluation(
            score=round(score, 2),
            strengths=strengths,
            weaknesses=weaknesses,
            feedback=feedback,
            ideal_answer=ideal_answer,
        )

    # ========================================================
    # FALLBACK EVALUATOR
    # ========================================================

    def _fallback_evaluation(
        self,
        question: str,
        answer: str,
        category: str,
    ) -> InterviewEvaluation:

        answer = answer.strip()

        word_count = len(
            answer.split()
        )

        score = 40.0

        strengths = []
        weaknesses = []

        # ----------------------------------------------------
        # Answer length
        # ----------------------------------------------------

        if word_count >= 10:
            score += 10

        if word_count >= 25:
            score += 10

        if word_count >= 50:
            score += 10

        # ----------------------------------------------------
        # Technical indicators
        # ----------------------------------------------------

        technical_keywords = [
            "because",
            "example",
            "algorithm",
            "complexity",
            "implementation",
            "advantage",
            "disadvantage",
            "process",
            "method",
            "class",
            "object",
            "database",
            "function",
            "memory",
            "time",
        ]

        answer_lower = answer.lower()

        found_keywords = [
            keyword
            for keyword in technical_keywords
            if keyword in answer_lower
        ]

        if found_keywords:
            score += 8

            strengths.append(
                "The answer includes relevant "
                "technical explanation."
            )

        if word_count >= 15:
            strengths.append(
                "The answer provides reasonable detail."
            )

        if word_count >= 30:
            strengths.append(
                "The answer shows logical structure "
                "or explanation."
            )

        if not strengths:
            strengths.append(
                "The answer addresses the question."
            )

        # ----------------------------------------------------
        # Weaknesses
        # ----------------------------------------------------

        if word_count < 15:
            weaknesses.append(
                "Provide more technical details."
            )

        if word_count < 30:
            weaknesses.append(
                "Include a practical example "
                "or explanation."
            )

        if not weaknesses:
            weaknesses.append(
                "The answer can be improved with "
                "deeper technical reasoning."
            )

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score = min(
            round(score, 2),
            100,
        )

        # ----------------------------------------------------
        # Feedback
        # ----------------------------------------------------

        if score >= 80:

            feedback = (
                "Excellent answer. You demonstrated "
                "good understanding and provided "
                "useful explanation."
            )

        elif score >= 65:

            feedback = (
                "Good attempt. The answer addresses "
                "the question, but you can improve it "
                "with more technical detail or examples."
            )

        else:

            feedback = (
                "The answer needs improvement. "
                "Focus on explaining the concept clearly "
                "and provide a practical example."
            )

        # ----------------------------------------------------
        # Ideal answer
        # ----------------------------------------------------

        ideal_answer = (
            "A strong answer should directly address "
            "the question, explain the key concept clearly, "
            "provide relevant reasoning, and include "
            "a practical example when appropriate."
        )

        return InterviewEvaluation(
            score=score,
            strengths=strengths,
            weaknesses=weaknesses,
            feedback=feedback,
            ideal_answer=ideal_answer,
        )


# ============================================================
# SHARED EVALUATOR INSTANCE
# ============================================================

evaluator = AIInterviewEvaluator()