import { useEffect, useState } from "react";
import {
  Brain,
  CheckCircle2,
  ChevronRight,
  Clock,
  Loader2,
  MessageSquare,
  RotateCcw,
  Send,
  Sparkles,
  Target,
  Trophy,
} from "lucide-react";
import api from "../services/api";
import BackButton from "../components/BackButton";

interface InterviewQuestion {
  question_id: number;
  question: string;
  category: string;
}

interface Evaluation {
  question_id: number;
  score: number;
  feedback: string;
  strengths?: string[];
  weaknesses?: string[];
  suggestions?: string[];
}

interface StartResponse {
  interview_id: number;
  company: string;
  target_role: string;
  interview_type: string;
  difficulty: string;
  total_questions: number;
  first_question: InterviewQuestion;
}

interface AnswerResponse {
  interview_id: number;
  question_id: number;
  evaluation: Evaluation;
  next_question: InterviewQuestion | null;
  completed: boolean;
}

interface SummaryResponse {
  interview_id: number;
  company: string;
  target_role: string;
  interview_type: string;
  difficulty: string;
  completed_questions: number;
  total_questions: number;
  average_score: number;
  completed: boolean;
}

const companies = [
  "Microsoft",
  "Amazon",
  "Zoho",
  "TCS",
  "Infosys",
  "Generic",
];

const interviewTypes = [
  "technical",
  "behavioral",
];

const difficulties = [
  "easy",
  "medium",
  "hard",
];

export default function Interview() {
  const [company, setCompany] = useState("Microsoft");
  const [interviewType, setInterviewType] = useState("technical");
  const [difficulty, setDifficulty] = useState("medium");

  const [interviewId, setInterviewId] = useState<number | null>(null);
  const [question, setQuestion] =
    useState<InterviewQuestion | null>(null);

  // Hold the next question until the user clicks Continue.
  // This keeps the evaluation aligned with the question just answered.
  const [nextQuestion, setNextQuestion] =
    useState<InterviewQuestion | null>(null);

  const [answer, setAnswer] = useState("");

  const [evaluation, setEvaluation] =
    useState<Evaluation | null>(null);

  const [summary, setSummary] =
    useState<SummaryResponse | null>(null);

  const [totalQuestions, setTotalQuestions] = useState(0);
  const [completedQuestions, setCompletedQuestions] = useState(0);

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [started, setStarted] = useState(false);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    setError("");
  }, [company, interviewType, difficulty]);

  const startInterview = async () => {
    try {
      setLoading(true);
      setError("");
      setEvaluation(null);
      setSummary(null);
      setNextQuestion(null);
      setAnswer("");
      setCompletedQuestions(0);
      setFinished(false);

      const response = await api.post<StartResponse>(
        "/api/v1/interview/start",
        {
          company,
          job_description:
            "Software Engineer responsible for designing, developing, testing, debugging, and maintaining software applications. Strong programming, data structures, algorithms, problem-solving, database, software engineering, and communication skills are expected.",
          interview_type: interviewType,
          difficulty,
        }
      );

      setInterviewId(response.data.interview_id);
      setQuestion(response.data.first_question);
      setTotalQuestions(response.data.total_questions);
      setStarted(true);
    } catch (err: any) {
      console.error("Failed to start interview:", err);

      const detail = err?.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(
          detail
            .map(
              (item: any) =>
                item?.msg || "Invalid interview configuration."
            )
            .join(", ")
        );
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError(
          "Unable to start the interview. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!interviewId || !question) return;

    if (!answer.trim()) {
      setError("Please enter an answer before submitting.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const response = await api.post<AnswerResponse>(
        "/api/v1/interview/answer",
        {
          interview_id: interviewId,
          question_id: question.question_id,
          answer: answer.trim(),
        }
      );

      setEvaluation(response.data.evaluation);
      setCompletedQuestions((previous) => previous + 1);
      setAnswer("");

      if (response.data.completed) {
        setFinished(true);
        setNextQuestion(null);
        await loadSummary(interviewId);
      } else {
        // Keep the current question visible while its evaluation is shown.
        // The next question is displayed only after Continue is clicked.
        setNextQuestion(response.data.next_question);
      }
    } catch (err: any) {
      console.error("Failed to submit answer:", err);

      const detail = err?.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(
          detail
            .map(
              (item: any) =>
                item?.msg || "Unable to evaluate your answer."
            )
            .join(", ")
        );
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError(
          "Unable to evaluate your answer. Please try again."
        );
      }
    } finally {
      setSubmitting(false);
    }
  };

  const loadSummary = async (id: number) => {
    try {
      const response = await api.get<SummaryResponse>(
        `/api/v1/interview/${id}/summary`
      );

      setSummary(response.data);
    } catch (err) {
      console.error("Failed to load interview summary:", err);
    }
  };

  const resetInterview = () => {
    setInterviewId(null);
    setQuestion(null);
    setNextQuestion(null);
    setAnswer("");
    setEvaluation(null);
    setSummary(null);
    setCompletedQuestions(0);
    setTotalQuestions(0);
    setStarted(false);
    setFinished(false);
    setError("");
  };

  const score = evaluation?.score ?? 0;

  const getScoreClass = (value: number) => {
    if (value >= 80) return "score-good";
    if (value >= 60) return "score-medium";
    return "score-low";
  };

  const getSummaryMessage = (value: number) => {
    if (value >= 85) {
      return "Excellent interview performance";
    }

    if (value >= 70) {
      return "Strong performance with room to improve";
    }

    if (value >= 50) {
      return "Good foundation — targeted practice will help";
    }

    return "More practice is recommended before interviews";
  };

  return (
    <div className="interview-page">
      <style>{`
        .interview-page {
          min-height: 100%;
          padding: 28px;
          color: #172033;
        }

        .interview-container {
          max-width: 1180px;
          margin: 0 auto;
        }

        .interview-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          margin-bottom: 28px;
        }

        .interview-title-row {
          display: flex;
          align-items: center;
          gap: 14px;
        }

        .interview-icon {
          width: 48px;
          height: 48px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          color: white;
          box-shadow: 0 8px 20px rgba(99, 102, 241, 0.22);
        }

        .interview-header h1 {
          margin: 0;
          font-size: 28px;
          font-weight: 800;
        }

        .interview-header p {
          margin: 6px 0 0;
          color: #667085;
          font-size: 14px;
        }

        .interview-badge {
          display: flex;
          align-items: center;
          gap: 7px;
          padding: 8px 12px;
          border-radius: 999px;
          background: #f3f0ff;
          color: #6841d8;
          font-size: 12px;
          font-weight: 700;
        }

        .setup-card,
        .question-card,
        .evaluation-card,
        .summary-card {
          background: white;
          border: 1px solid #e6e9f0;
          border-radius: 20px;
          box-shadow: 0 8px 28px rgba(16, 24, 40, 0.06);
        }

        .setup-card {
          padding: 28px;
        }

        .section-heading {
          margin-bottom: 22px;
        }

        .section-heading h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 800;
        }

        .section-heading p {
          margin: 6px 0 0;
          color: #667085;
          font-size: 14px;
        }

        .setup-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 18px;
        }

        .field {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .field label {
          font-size: 13px;
          font-weight: 700;
          color: #344054;
        }

        .field select {
          height: 46px;
          padding: 0 13px;
          border: 1px solid #d9dee8;
          border-radius: 11px;
          background: white;
          color: #172033;
          font-size: 14px;
          outline: none;
          cursor: pointer;
        }

        .field select:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .start-button,
        .submit-button,
        .reset-button,
        .next-button {
          border: none;
          cursor: pointer;
          border-radius: 11px;
          font-weight: 700;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: 0.2s ease;
        }

        .start-button {
          margin-top: 22px;
          width: 100%;
          height: 48px;
          color: white;
          background: linear-gradient(135deg, #6366f1, #7c3aed);
        }

        .start-button:hover,
        .submit-button:hover,
        .next-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 8px 18px rgba(99, 102, 241, 0.2);
        }

        .start-button:disabled,
        .submit-button:disabled {
          opacity: 0.65;
          cursor: not-allowed;
          transform: none;
        }

        .error-box {
          margin-top: 18px;
          padding: 12px 14px;
          border-radius: 10px;
          background: #fff1f2;
          border: 1px solid #fecdd3;
          color: #be123c;
          font-size: 13px;
        }

        .interview-topbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          margin-bottom: 18px;
        }

        .interview-meta {
          display: flex;
          gap: 9px;
          flex-wrap: wrap;
        }

        .meta-pill {
          padding: 7px 11px;
          border-radius: 999px;
          background: #f5f6fa;
          color: #475467;
          font-size: 12px;
          font-weight: 700;
        }

        .progress-info {
          min-width: 220px;
        }

        .progress-label {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #667085;
          margin-bottom: 7px;
        }

        .progress-track {
          height: 7px;
          border-radius: 99px;
          background: #eaecf0;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          border-radius: 99px;
          background: linear-gradient(90deg, #6366f1, #8b5cf6);
          transition: width 0.3s ease;
        }

        .question-card {
          padding: 30px;
        }

        .question-category {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          padding: 7px 10px;
          border-radius: 999px;
          background: #eef2ff;
          color: #4f46e5;
          font-size: 12px;
          font-weight: 800;
          text-transform: capitalize;
          margin-bottom: 18px;
        }

        .question-number {
          color: #98a2b3;
          font-size: 13px;
          font-weight: 700;
          margin-bottom: 9px;
        }

        .question-text {
          font-size: 24px;
          line-height: 1.45;
          font-weight: 750;
          color: #172033;
          margin: 0 0 24px;
        }

        .answer-box {
          width: 100%;
          min-height: 180px;
          resize: vertical;
          box-sizing: border-box;
          border: 1px solid #d9dee8;
          border-radius: 14px;
          padding: 15px;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.6;
          outline: none;
        }

        .answer-box:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .answer-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 15px;
          margin-top: 14px;
        }

        .answer-hint {
          color: #98a2b3;
          font-size: 12px;
        }

        .submit-button,
        .next-button {
          min-width: 150px;
          height: 44px;
          color: white;
          background: linear-gradient(135deg, #6366f1, #7c3aed);
        }

        .evaluation-card {
          margin-top: 18px;
          padding: 24px;
        }

        .evaluation-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 15px;
          margin-bottom: 20px;
        }

        .evaluation-title {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .evaluation-title h3 {
          margin: 0;
          font-size: 17px;
        }

        .score-badge {
          min-width: 64px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          font-weight: 900;
        }

        .score-good {
          background: #ecfdf3;
          color: #027a48;
        }

        .score-medium {
          background: #fffaeb;
          color: #b54708;
        }

        .score-low {
          background: #fff1f2;
          color: #be123c;
        }

        .feedback {
          padding: 16px;
          border-radius: 12px;
          background: #f8f9fc;
          color: #475467;
          font-size: 14px;
          line-height: 1.65;
          margin-bottom: 18px;
        }

        .evaluation-columns {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
        }

        .eval-section {
          padding: 15px;
          border: 1px solid #eaecf0;
          border-radius: 12px;
        }

        .eval-section h4 {
          margin: 0 0 10px;
          font-size: 13px;
        }

        .eval-section ul {
          margin: 0;
          padding-left: 18px;
          color: #667085;
          font-size: 13px;
          line-height: 1.6;
        }

        .eval-section li {
          margin-bottom: 5px;
        }

        .next-row {
          display: flex;
          justify-content: flex-end;
          margin-top: 20px;
        }

        .summary-card {
          padding: 34px;
          text-align: center;
        }

        .summary-icon {
          width: 68px;
          height: 68px;
          margin: 0 auto 16px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #ecfdf3;
          color: #039855;
        }

        .summary-card h2 {
          margin: 0;
          font-size: 25px;
        }

        .summary-card > p {
          margin: 8px 0 24px;
          color: #667085;
        }

        .summary-score {
          font-size: 56px;
          font-weight: 900;
          line-height: 1;
          margin-bottom: 8px;
        }

        .summary-message {
          color: #475467;
          font-size: 14px;
          margin-bottom: 26px;
        }

        .summary-stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
          margin-bottom: 25px;
        }

        .summary-stat {
          padding: 18px;
          background: #f8f9fc;
          border-radius: 13px;
        }

        .summary-stat strong {
          display: block;
          font-size: 22px;
          margin-bottom: 4px;
        }

        .summary-stat span {
          color: #667085;
          font-size: 12px;
        }

        .reset-button {
          height: 44px;
          padding: 0 18px;
          color: #344054;
          background: white;
          border: 1px solid #d0d5dd;
        }

        .reset-button:hover {
          background: #f9fafb;
        }

        .loading-center {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 9px;
          padding: 25px;
          color: #667085;
          font-size: 13px;
        }

        @media (max-width: 800px) {
          .interview-page {
            padding: 18px;
          }

          .interview-header {
            flex-direction: column;
          }

          .setup-grid,
          .evaluation-columns,
          .summary-stats {
            grid-template-columns: 1fr;
          }

          .interview-topbar,
          .answer-footer {
            flex-direction: column;
            align-items: stretch;
          }

          .progress-info {
            width: 100%;
          }

          .question-text {
            font-size: 20px;
          }

          .submit-button,
          .next-button {
            width: 100%;
          }
        }
      `}</style>

      <div className="interview-container">
        <BackButton />

        <div className="interview-header">
          <div>
            <div className="interview-title-row">
              <div className="interview-icon">
                <Brain size={25} />
              </div>

              <div>
                <h1>AI Interview</h1>
                <p>
                  Practice realistic interviews and get AI-powered feedback.
                </p>
              </div>
            </div>
          </div>

          <div className="interview-badge">
            <Sparkles size={14} />
            AI Evaluated
          </div>
        </div>

        {!started && (
          <div className="setup-card">
            <div className="section-heading">
              <h2>Configure your interview</h2>
              <p>
                Choose your target company, interview style and difficulty.
              </p>
            </div>

            <div className="setup-grid">
              <div className="field">
                <label>Target Company</label>

                <select
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                >
                  {companies.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label>Interview Type</label>

                <select
                  value={interviewType}
                  onChange={(e) =>
                    setInterviewType(e.target.value)
                  }
                >
                  {interviewTypes.map((item) => (
                    <option key={item} value={item}>
                      {item.charAt(0).toUpperCase() + item.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label>Difficulty</label>

                <select
                  value={difficulty}
                  onChange={(e) =>
                    setDifficulty(e.target.value)
                  }
                >
                  {difficulties.map((item) => (
                    <option key={item} value={item}>
                      {item.charAt(0).toUpperCase() + item.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              className="start-button"
              onClick={startInterview}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 size={17} />
                  Starting Interview...
                </>
              ) : (
                <>
                  <Sparkles size={17} />
                  Start AI Interview
                </>
              )}
            </button>

            {error && <div className="error-box">{error}</div>}
          </div>
        )}

        {started && !finished && question && (
          <>
            <div className="interview-topbar">
              <div className="interview-meta">
                <span className="meta-pill">
                  <Target size={12} /> {company}
                </span>

                <span className="meta-pill">
                  {interviewType}
                </span>

                <span className="meta-pill">
                  <Clock size={12} /> {difficulty}
                </span>
              </div>

              <div className="progress-info">
                <div className="progress-label">
                  <span>Interview progress</span>
                  <span>
                    {completedQuestions}/{totalQuestions}
                  </span>
                </div>

                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${
                        totalQuestions
                          ? (completedQuestions / totalQuestions) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="question-card">
              <div className="question-category">
                <MessageSquare size={13} />
                {question.category}
              </div>

              <div className="question-number">
                Question {completedQuestions + 1} of {totalQuestions}
              </div>

              <h2 className="question-text">
                {question.question}
              </h2>

              <textarea
                className="answer-box"
                placeholder="Type your answer here..."
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                disabled={submitting}
              />

              <div className="answer-footer">
                <span className="answer-hint">
                  Give a clear answer with examples where possible.
                </span>

                <button
                  className="submit-button"
                  onClick={submitAnswer}
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <Loader2 size={16} />
                      Evaluating...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Submit Answer
                    </>
                  )}
                </button>
              </div>

              {error && <div className="error-box">{error}</div>}
            </div>

            {evaluation && (
              <div className="evaluation-card">
                <div className="evaluation-header">
                  <div className="evaluation-title">
                    <CheckCircle2 size={20} color="#039855" />
                    <h3>AI Evaluation</h3>
                  </div>

                  <div
                    className={`score-badge ${getScoreClass(
                      score
                    )}`}
                  >
                    {Math.round(score)}/100
                  </div>
                </div>

                <div className="feedback">
                  {evaluation.feedback}
                </div>

                <div className="evaluation-columns">
                  {evaluation.strengths &&
                    evaluation.strengths.length > 0 && (
                      <div className="eval-section">
                        <h4>Strengths</h4>

                        <ul>
                          {evaluation.strengths.map(
                            (item, index) => (
                              <li key={index}>{item}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}

                  {evaluation.weaknesses &&
                    evaluation.weaknesses.length > 0 && (
                      <div className="eval-section">
                        <h4>Areas to Improve</h4>

                        <ul>
                          {evaluation.weaknesses.map(
                            (item, index) => (
                              <li key={index}>{item}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}

                  {evaluation.suggestions &&
                    evaluation.suggestions.length > 0 && (
                      <div className="eval-section">
                        <h4>Suggestions</h4>

                        <ul>
                          {evaluation.suggestions.map(
                            (item, index) => (
                              <li key={index}>{item}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                </div>

                {!finished && question && (
                  <div className="next-row">
                    <button
                      className="next-button"
                      onClick={() => {
                        setEvaluation(null);
                        setAnswer("");

                        if (nextQuestion) {
                          setQuestion(nextQuestion);
                          setNextQuestion(null);
                        }
                      }}
                    >
                      Continue
                      <ChevronRight size={16} />
                    </button>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {finished && (
          <div className="summary-card">
            <div className="summary-icon">
              {summary && summary.average_score >= 70 ? (
                <Trophy size={32} />
              ) : (
                <CheckCircle2 size={32} />
              )}
            </div>

            <h2>Interview Completed</h2>

            <p>
              {summary
                ? getSummaryMessage(summary.average_score)
                : "Your interview has been evaluated."}
            </p>

            {summary ? (
              <>
                <div
                  className={`summary-score ${getScoreClass(
                    summary.average_score
                  )}`}
                >
                  {Math.round(summary.average_score)}/100
                </div>

                <div className="summary-message">
                  Average interview score
                </div>

                <div className="summary-stats">
                  <div className="summary-stat">
                    <strong>
                      {summary.completed_questions}
                    </strong>
                    <span>Questions Completed</span>
                  </div>

                  <div className="summary-stat">
                    <strong>
                      {summary.total_questions}
                    </strong>
                    <span>Total Questions</span>
                  </div>

                  <div className="summary-stat">
                    <strong>{summary.company}</strong>
                    <span>Target Company</span>
                  </div>
                </div>

                <button
                  className="reset-button"
                  onClick={resetInterview}
                >
                  <RotateCcw size={16} />
                  Start Another Interview
                </button>
              </>
            ) : (
              <div className="loading-center">
                <Loader2 size={17} />
                Loading your interview summary...
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}