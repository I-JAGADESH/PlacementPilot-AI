from typing import Optional, List
import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.interview.schemas import InterviewEvaluation


class AIInterviewEvaluator:
    """
    AI-powered interview answer evaluator supporting objective scoring,
    technical gap identification, communication feedback, missed concepts,
    and fallback rule-based evaluation.
    """

    def __init__(self):
        self.client = None

        if (
            settings.GEMINI_API_KEY
            and settings.GEMINI_API_KEY != "placeholder"
            and not settings.GEMINI_API_KEY.startswith("your-")
        ):
            try:
                self.client = genai.Client(
                    api_key=settings.GEMINI_API_KEY,
                )
            except Exception as e:
                print("Gemini client initialization failed:", repr(e))


    def evaluate(
        self,
        question: str,
        answer: str,
        category: str,
        company: Optional[str] = None,
        difficulty: str = "Medium",
        question_type: str = "short_answer",
        rubric: Optional[str] = None,
    ) -> InterviewEvaluation:

        if not answer.strip():
            return InterviewEvaluation(
                score=0.0,
                technical_score=0.0,
                communication_score=0.0,
                strengths=[],
                weaknesses=["No answer was provided."],
                technical_gaps=["Candidate skipped the question."],
                communication_feedback=["No verbal or written response was submitted."],
                missed_concepts=["All required concepts were omitted."],
                feedback="Please provide an answer to the interview question.",
                ideal_answer="A strong answer should directly address the question, provide technical depth, and cite practical examples.",
            )

        if self.client is not None:
            try:
                return self._evaluate_with_gemini(
                    question=question,
                    answer=answer,
                    category=category,
                    company=company,
                    difficulty=difficulty,
                    question_type=question_type,
                    rubric=rubric,
                )
            except Exception as e:
                print("Gemini evaluation failed. Using rule-based fallback evaluator. Reason:", repr(e))

        return self._fallback_evaluation(
            question=question,
            answer=answer,
            category=category,
            difficulty=difficulty,
            question_type=question_type,
            rubric=rubric,
        )

    def _evaluate_with_gemini(
        self,
        question: str,
        answer: str,
        category: str,
        company: Optional[str],
        difficulty: str,
        question_type: str,
        rubric: Optional[str],
    ) -> InterviewEvaluation:

        company_name = company or "Generic"
        rubric_text = rubric or "Evaluate based on technical correctness, clarity, and depth."

        prompt = f"""
You are an expert technical interviewer conducting a placement interview for {company_name}.

Evaluate the candidate's answer strictly and objectively against the rubric.

INTERVIEW DETAILS:
Company: {company_name}
Category: {category}
Difficulty: {difficulty}
Question Type: {question_type}
Evaluation Rubric: {rubric_text}

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

RETURN A JSON OBJECT WITH EXACTLY THESE KEYS:
- score: float (0-100)
- technical_score: float (0-100)
- communication_score: float (0-100)
- strengths: list of strings
- weaknesses: list of strings
- technical_gaps: list of strings
- communication_feedback: list of strings
- missed_concepts: list of strings
- feedback: string explanation
- ideal_answer: string with ideal response
"""

        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        text = response.text.strip()
        if not text:
            raise ValueError("Gemini returned an empty response.")

        data = json.loads(text)

        score = max(0.0, min(100.0, float(data.get("score", 50.0))))
        tech_score = max(0.0, min(100.0, float(data.get("technical_score", score))))
        comm_score = max(0.0, min(100.0, float(data.get("communication_score", score))))

        return InterviewEvaluation(
            score=round(score, 2),
            technical_score=round(tech_score, 2),
            communication_score=round(comm_score, 2),
            strengths=[str(s) for s in data.get("strengths", [])],
            weaknesses=[str(w) for w in data.get("weaknesses", [])],
            technical_gaps=[str(t) for t in data.get("technical_gaps", [])],
            communication_feedback=[str(c) for c in data.get("communication_feedback", [])],
            missed_concepts=[str(m) for m in data.get("missed_concepts", [])],
            feedback=str(data.get("feedback", "Evaluation complete.")),
            ideal_answer=str(data.get("ideal_answer", "Standard comprehensive response.")),
        )

    def _fallback_evaluation(
        self,
        question: str,
        answer: str,
        category: str,
        difficulty: str = "Medium",
        question_type: str = "short_answer",
        rubric: Optional[str] = None,
    ) -> InterviewEvaluation:
        answer_clean = answer.strip()
        word_count = len(answer_clean.split())

        base_score = 45.0
        strengths: List[str] = []
        weaknesses: List[str] = []
        technical_gaps: List[str] = []
        communication_feedback: List[str] = []
        missed_concepts: List[str] = []

        if word_count >= 10:
            base_score += 15.0
            communication_feedback.append("Good response length and initial clarity.")
        else:
            communication_feedback.append("Answer is too brief. Elaborate further with STAR method or structured technical points.")
            weaknesses.append("Conciseness needs more substance.")

        if word_count >= 35:
            base_score += 15.0
            strengths.append("Provides detailed explanation and context.")

        # Keywords check for technical relevance
        keywords = ["because", "example", "complexity", "implementation", "class", "function", "database", "algorithm", "trade-off", "architecture"]
        found = [k for k in keywords if k in answer_clean.lower()]

        if found:
            base_score += 15.0
            strengths.append(f"Used technical terms: {', '.join(found[:3])}.")
        else:
            technical_gaps.append("Missing specific technical terminology and domain depth.")
            missed_concepts.append("Core algorithmic or architectural details.")

        score = min(100.0, round(base_score, 2))
        tech_score = score
        comm_score = min(100.0, round(score + (10.0 if word_count >= 20 else -10.0), 2))

        if score >= 75:
            feedback = "Strong attempt! You demonstrated solid understanding and clear communication."
        elif score >= 55:
            feedback = "Satisfactory answer, but you can strengthen it by citing exact trade-offs and concrete examples."
        else:
            feedback = "Needs improvement. Focus on technical accuracy, edge cases, and structured delivery."

        ideal_answer = (
            "A strong interview response should clearly state the core concept, explain how it works under the hood, "
            "highlight key trade-offs (time/space complexity or system bottlenecks), and cite a real-world project example."
        )

        return InterviewEvaluation(
            score=score,
            technical_score=tech_score,
            communication_score=comm_score,
            strengths=strengths or ["Addressed the question directly."],
            weaknesses=weaknesses or ["Could provide deeper architectural details."],
            technical_gaps=technical_gaps or ["Minor technical specifics missing."],
            communication_feedback=communication_feedback,
            missed_concepts=missed_concepts or ["Advanced edge case considerations."],
            feedback=feedback,
            ideal_answer=ideal_answer,
        )


evaluator = AIInterviewEvaluator()