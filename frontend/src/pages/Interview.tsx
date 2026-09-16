import { useEffect, useState } from "react";
import {
  Brain,
  ChevronRight,
  Clock,
  Loader2,
  RotateCcw,
  Sparkles,
  Trophy,
  BookOpen,
  History,
  Compass,
} from "lucide-react";
import api from "../services/api";
import BackButton from "../components/BackButton";

interface InterviewQuestion {
  question_id: number;
  question: string;
  category: string;
  difficulty: string;
  company?: string;
  round?: string;
  role?: string;
  experience_level?: string;
  domain?: string;
  question_type?: string;
  options?: string[];
  expected_answer_type?: string;
  rubric?: string;
  concepts_tested?: string[];
  estimated_time?: string;
  disclaimer?: string;
}

interface Evaluation {
  question_id: number;
  score: number;
  technical_score?: number;
  communication_score?: number;
  feedback: string;
  ideal_answer: string;
  strengths?: string[];
  weaknesses?: string[];
  technical_gaps?: string[];
  communication_feedback?: string[];
  missed_concepts?: string[];
  adaptation_reason?: string;
}

interface ConfigResponse {
  roles: string[];
  experience_levels: string[];
  interview_rounds: string[];
  difficulties: string[];
  domains: string[];
  user_profile_summary?: {
    target_company?: string;
    target_role?: string;
    projects_count?: number;
    skills_count?: number;
    weak_topics?: string[];
  };
}

interface StartResponse {
  interview_id: number;
  company: string;
  target_role: string;
  experience_level: string;
  interview_type: string;
  difficulty: string;
  domain?: string;
  total_questions: number;
  first_question: InterviewQuestion;
}

interface AnswerResponse {
  interview_id: number;
  question_id: number;
  evaluation: Evaluation;
  next_question: InterviewQuestion | null;
  completed: boolean;
  adaptation_notice?: string;
}

interface SummaryResponse {
  interview_id: number;
  company: string;
  target_role: string;
  experience_level: string;
  interview_type: string;
  difficulty: string;
  domain?: string;
  completed_questions: number;
  total_questions: number;
  average_score: number;
  communication_score: number;
  performance_level: string;
  completed: boolean;
  strengths: string[];
  weaknesses: string[];
  technical_gaps: string[];
  communication_feedback: string[];
  missed_concepts: string[];
  recommended_topics: string[];
  next_recommended_difficulty: string;
  preparation_roadmap: string[];
}

interface HistoryItem {
  id: number;
  company: string;
  target_role: string;
  experience_level: string;
  interview_type: string;
  difficulty: string;
  domain?: string;
  average_score: number;
  performance_level: string;
  created_at: string;
}

export default function Interview() {
  const [activeTab, setActiveTab] = useState<"practice" | "history">("practice");
  const [config, setConfig] = useState<ConfigResponse | null>(null);

  // Form State
  const [company, setCompany] = useState("Generic");
  const [customCompany, setCustomCompany] = useState("");
  const [role, setRole] = useState("Software Engineer");
  const [experienceLevel, setExperienceLevel] = useState("Entry Level");
  const [interviewRound, setInterviewRound] = useState("Technical MCQ");
  const [difficulty, setDifficulty] = useState("Medium");
  const [domain, setDomain] = useState("DSA");

  // Interview Execution State
  const [interviewId, setInterviewId] = useState<number | null>(null);
  const [question, setQuestion] = useState<InterviewQuestion | null>(null);
  const [nextQuestion, setNextQuestion] = useState<InterviewQuestion | null>(null);
  const [answer, setAnswer] = useState("");
  const [selectedMcq, setSelectedMcq] = useState("");

  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const [totalQuestions, setTotalQuestions] = useState(0);
  const [timer, setTimer] = useState(0);

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [started, setStarted] = useState(false);
  const [finished, setFinished] = useState(false);

  // Fetch Configuration and History
  useEffect(() => {
    loadConfig();
    loadHistory();
  }, []);

  // Question Timer
  useEffect(() => {
    let interval: any = null;
    if (started && !finished && question) {
      interval = setInterval(() => setTimer((t) => t + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [started, finished, question]);

  const loadConfig = async () => {
    try {
      const res = await api.get<ConfigResponse>("/api/v1/interview/config");
      setConfig(res.data);
      if (res.data.user_profile_summary?.target_company) {
        setCompany(res.data.user_profile_summary.target_company);
      }
      if (res.data.user_profile_summary?.target_role) {
        setRole(res.data.user_profile_summary.target_role);
      }
    } catch (err) {
      console.error("Failed to load interview config:", err);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await api.get<HistoryItem[]>("/api/v1/interview/history");
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const startInterview = async () => {
    try {
      setLoading(true);
      setError("");
      setEvaluation(null);
      setSummary(null);
      setNextQuestion(null);
      setAnswer("");
      setSelectedMcq("");
      setFinished(false);
      setTimer(0);

      const targetComp = company === "Custom" ? customCompany || "Generic" : company;

      const response = await api.post<StartResponse>("/api/v1/interview/start", {
        company: targetComp,
        role,
        experience_level: experienceLevel,
        interview_round: interviewRound,
        difficulty,
        domain,
      });

      setInterviewId(response.data.interview_id);
      setQuestion(response.data.first_question);
      setTotalQuestions(response.data.total_questions);
      setStarted(true);
    } catch (err: any) {
      console.error("Failed to start interview:", err);
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Unable to start the interview session.");
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!interviewId || !question) return;

    const finalAns = question.options ? selectedMcq : answer.trim();
    if (!finalAns) {
      setError("Please select or enter an answer before submitting.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const response = await api.post<AnswerResponse>("/api/v1/interview/answer", {
        interview_id: interviewId,
        question_id: question.question_id,
        answer: finalAns,
      });

      setEvaluation(response.data.evaluation);
      setAnswer("");
      setSelectedMcq("");

      if (response.data.completed) {
        setFinished(true);
        setNextQuestion(null);
        await loadSummary(interviewId);
        await loadHistory();
      } else {
        setNextQuestion(response.data.next_question);
      }
    } catch (err: any) {
      console.error("Failed to submit answer:", err);
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Unable to evaluate answer.");
    } finally {
      setSubmitting(false);
    }
  };

  const proceedToNext = () => {
    if (nextQuestion) {
      setQuestion(nextQuestion);
      setNextQuestion(null);
      setEvaluation(null);
      setAnswer("");
      setSelectedMcq("");
      setTimer(0);
    }
  };

  const loadSummary = async (id: number) => {
    try {
      const response = await api.get<SummaryResponse>(`/api/v1/interview/${id}/summary`);
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
    setSelectedMcq("");
    setEvaluation(null);
    setSummary(null);
    setTotalQuestions(0);
    setStarted(false);
    setFinished(false);
    setError("");
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
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

        .tab-switcher {
          display: flex;
          gap: 12px;
          margin-bottom: 24px;
        }

        .tab-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 18px;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 700;
          cursor: pointer;
          border: 1px solid #e2e8f0;
          background: white;
          color: #64748b;
          transition: 0.2s;
        }

        .tab-btn.active {
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          color: white;
          border-color: transparent;
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }

        .interview-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          margin-bottom: 24px;
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

        .setup-card, .question-card, .evaluation-card, .summary-card, .history-card {
          background: white;
          border: 1px solid #e6e9f0;
          border-radius: 20px;
          padding: 28px;
          box-shadow: 0 8px 28px rgba(16, 24, 40, 0.06);
          margin-bottom: 24px;
        }

        .setup-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 18px;
          margin-bottom: 22px;
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

        .field select, .field input {
          height: 46px;
          padding: 0 13px;
          border: 1px solid #d9dee8;
          border-radius: 11px;
          background: white;
          color: #172033;
          font-size: 14px;
          outline: none;
        }

        .profile-signals-card {
          background: #f8fafc;
          border: 1px dashed #cbd5e1;
          border-radius: 14px;
          padding: 16px;
          margin-bottom: 22px;
        }

        .disclaimer-banner {
          background: #eff6ff;
          border: 1px solid #bfdbfe;
          color: #1e40af;
          border-radius: 10px;
          padding: 10px 14px;
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 20px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .start-button, .submit-button, .next-button, .reset-button {
          border: none;
          cursor: pointer;
          border-radius: 11px;
          font-weight: 700;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: 0.2s;
        }

        .start-button {
          width: 100%;
          height: 48px;
          color: white;
          background: linear-gradient(135deg, #6366f1, #7c3aed);
        }

        .question-meta-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          margin-bottom: 16px;
        }

        .question-text {
          font-size: 22px;
          line-height: 1.45;
          font-weight: 800;
          color: #0f172a;
          margin-bottom: 20px;
        }

        .mcq-options {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 20px;
        }

        .mcq-option {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          cursor: pointer;
          transition: 0.2s;
        }

        .mcq-option:hover {
          border-color: #6366f1;
          background: #f8fafc;
        }

        .mcq-option.selected {
          border-color: #6366f1;
          background: #eef2ff;
        }

        .answer-box {
          width: 100%;
          min-height: 160px;
          border: 1px solid #cbd5e1;
          border-radius: 14px;
          padding: 14px;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.6;
          outline: none;
        }

        .scores-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
          margin-bottom: 20px;
        }

        .score-pill {
          padding: 14px;
          border-radius: 12px;
          text-align: center;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
        }

        .score-pill strong {
          display: block;
          font-size: 24px;
          font-weight: 900;
          margin-bottom: 4px;
        }

        .eval-details-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
          margin-top: 16px;
        }

        .eval-box {
          padding: 16px;
          border-radius: 12px;
          border: 1px solid #e2e8f0;
          background: #ffffff;
        }

        .eval-box h4 {
          margin: 0 0 8px;
          font-size: 13px;
          font-weight: 700;
        }

        .eval-box ul {
          margin: 0;
          padding-left: 18px;
          font-size: 13px;
          color: #475569;
        }

        .roadmap-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-top: 12px;
          text-align: left;
        }

        .roadmap-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 16px;
          background: #f1f5f9;
          border-radius: 10px;
          font-size: 14px;
          font-weight: 600;
        }
      `}</style>

      <div className="interview-container">
        <BackButton />

        <div className="interview-header">
          <div style={{ display: "flex", gap: "14px", alignItems: "center" }}>
            <div className="interview-icon">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h1 style={{ margin: 0, fontSize: "26px", fontWeight: 800 }}>Company-Style AI Interview Engine</h1>
              <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: "14px" }}>
                Role-specific, profile-aware interview preparation across 11 rounds & 16 technical domains.
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-switcher">
          <button
            className={`tab-btn ${activeTab === "practice" ? "active" : ""}`}
            onClick={() => setActiveTab("practice")}
          >
            <Compass className="w-4 h-4" /> Practice Interview
          </button>
          <button
            className={`tab-btn ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            <History className="w-4 h-4" /> Session History ({history.length})
          </button>
        </div>

        {/* Framing Disclaimer */}
        <div className="disclaimer-banner">
          <Sparkles className="w-4 h-4" />
          <span>Notice: All questions are realistic company-style interview questions based on role expectations and standard interview patterns.</span>
        </div>

        {activeTab === "practice" ? (
          <>
            {!started ? (
              <div className="setup-card">
                <h2 style={{ margin: "0 0 18px", fontSize: "18px", fontWeight: 800 }}>Configure Your Interview Session</h2>

                {/* Profile Context Banner if available */}
                {config?.user_profile_summary && (
                  <div className="profile-signals-card">
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#334155", marginBottom: "6px" }}>
                      Detected Profile Signals:
                    </div>
                    <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", fontSize: "12px", color: "#64748b" }}>
                      <span>Target: <strong>{config.user_profile_summary.target_company || "Generic"}</strong></span>
                      <span>Role: <strong>{config.user_profile_summary.target_role || "Software Engineer"}</strong></span>
                      <span>Projects: <strong>{config.user_profile_summary.projects_count}</strong></span>
                      <span>Skills: <strong>{config.user_profile_summary.skills_count}</strong></span>
                      {config.user_profile_summary.weak_topics?.length ? (
                        <span style={{ color: "#e11d48" }}>Identified Weak Areas: <strong>{config.user_profile_summary.weak_topics.join(", ")}</strong></span>
                      ) : null}
                    </div>
                  </div>
                )}

                <div className="setup-grid">
                  <div className="field">
                    <label>Target Company</label>
                    <select value={company} onChange={(e) => setCompany(e.target.value)}>
                      <option value="Generic">Generic / General</option>
                      <option value="Microsoft">Microsoft</option>
                      <option value="Amazon">Amazon</option>
                      <option value="Zoho">Zoho</option>
                      <option value="TCS">TCS</option>
                      <option value="Infosys">Infosys</option>
                      <option value="Custom">Custom Entry...</option>
                    </select>
                  </div>

                  {company === "Custom" && (
                    <div className="field">
                      <label>Enter Company Name</label>
                      <input
                        type="text"
                        placeholder="e.g. Google, Stripe"
                        value={customCompany}
                        onChange={(e) => setCustomCompany(e.target.value)}
                      />
                    </div>
                  )}

                  <div className="field">
                    <label>Target Role</label>
                    <select value={role} onChange={(e) => setRole(e.target.value)}>
                      {config?.roles.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      )) || <option value="Software Engineer">Software Engineer</option>}
                    </select>
                  </div>

                  <div className="field">
                    <label>Experience Level</label>
                    <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)}>
                      {config?.experience_levels.map((el) => (
                        <option key={el} value={el}>{el}</option>
                      )) || <option value="Entry Level">Entry Level</option>}
                    </select>
                  </div>

                  <div className="field">
                    <label>Interview Round</label>
                    <select value={interviewRound} onChange={(e) => setInterviewRound(e.target.value)}>
                      {config?.interview_rounds.map((ir) => (
                        <option key={ir} value={ir}>{ir}</option>
                      )) || <option value="Technical MCQ">Technical MCQ</option>}
                    </select>
                  </div>

                  <div className="field">
                    <label>Difficulty</label>
                    <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                      {config?.difficulties.map((d) => (
                        <option key={d} value={d}>{d}</option>
                      )) || <option value="Medium">Medium</option>}
                    </select>
                  </div>

                  <div className="field">
                    <label>Technical Domain</label>
                    <select value={domain} onChange={(e) => setDomain(e.target.value)}>
                      {config?.domains.map((dom) => (
                        <option key={dom} value={dom}>{dom}</option>
                      )) || <option value="DSA">DSA</option>}
                    </select>
                  </div>
                </div>

                {error && <div style={{ color: "#ef4444", fontSize: "13px", marginBottom: "14px" }}>{error}</div>}

                <button className="start-button" onClick={startInterview} disabled={loading}>
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Start Interview Session"}
                </button>
              </div>
            ) : finished && summary ? (
              /* POST-INTERVIEW SUMMARY REPORT */
              <div className="summary-card" style={{ textAlign: "center" }}>
                <div style={{ width: "64px", height: "64px", margin: "0 auto 16px", borderRadius: "50%", background: "#ecfdf5", color: "#10b981", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Trophy className="w-8 h-8" />
                </div>
                <h2 style={{ margin: 0, fontSize: "24px", fontWeight: 800 }}>Interview Evaluation Report</h2>
                <p style={{ color: "#64748b", margin: "6px 0 20px" }}>
                  Completed {summary.completed_questions} of {summary.total_questions} questions for {summary.target_role} ({summary.company}).
                </p>

                <div className="scores-grid">
                  <div className="score-pill">
                    <strong>{summary.average_score}%</strong>
                    <span style={{ fontSize: "12px", color: "#64748b" }}>Overall Score</span>
                  </div>
                  <div className="score-pill">
                    <strong>{summary.communication_score}%</strong>
                    <span style={{ fontSize: "12px", color: "#64748b" }}>Communication Score</span>
                  </div>
                  <div className="score-pill">
                    <strong style={{ fontSize: "18px", color: "#6366f1" }}>{summary.next_recommended_difficulty}</strong>
                    <span style={{ fontSize: "12px", color: "#64748b" }}>Next Recommended Difficulty</span>
                  </div>
                </div>

                <div className="eval-details-grid" style={{ textAlign: "left" }}>
                  <div className="eval-box">
                    <h4 style={{ color: "#10b981" }}>Strengths</h4>
                    <ul>
                      {summary.strengths.map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="eval-box">
                    <h4 style={{ color: "#ef4444" }}>Technical Gaps</h4>
                    <ul>
                      {summary.technical_gaps.map((g, idx) => (
                        <li key={idx}>{g}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="eval-box">
                    <h4 style={{ color: "#6366f1" }}>Communication Feedback</h4>
                    <ul>
                      {summary.communication_feedback.map((cf, idx) => (
                        <li key={idx}>{cf}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="eval-box">
                    <h4 style={{ color: "#f59e0b" }}>Recommended Topics</h4>
                    <ul>
                      {summary.recommended_topics.map((rt, idx) => (
                        <li key={idx}>{rt}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Personal Roadmap */}
                <div style={{ marginTop: "24px", textAlign: "left" }}>
                  <h3 style={{ fontSize: "16px", fontWeight: 800, margin: "0 0 12px" }}>Personal Preparation Roadmap</h3>
                  <div className="roadmap-list">
                    {summary.preparation_roadmap.map((step, idx) => (
                      <div className="roadmap-item" key={idx}>
                        <BookOpen className="w-4 h-4 text-indigo-600" />
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <button className="start-button" style={{ marginTop: "28px" }} onClick={resetInterview}>
                  <RotateCcw className="w-4 h-4" /> Start New Interview
                </button>
              </div>
            ) : question ? (
              /* INTERVIEW QUESTION & ANSWER CANVAS */
              <div className="question-card">
                <div className="question-meta-row">
                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    <span style={{ background: "#eef2ff", color: "#6366f1", padding: "4px 10px", borderRadius: "999px", fontSize: "12px", fontWeight: 700 }}>
                      Q{question.question_id} of {totalQuestions}
                    </span>
                    <span style={{ background: "#f1f5f9", color: "#475569", padding: "4px 10px", borderRadius: "999px", fontSize: "12px", fontWeight: 700 }}>
                      {question.category}
                    </span>
                    <span style={{ background: "#fef3c7", color: "#b45309", padding: "4px 10px", borderRadius: "999px", fontSize: "12px", fontWeight: 700 }}>
                      {question.difficulty}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", fontWeight: 700, color: "#64748b" }}>
                    <Clock className="w-4 h-4" />
                    <span>{formatTimer(timer)}</span>
                  </div>
                </div>

                <div className="question-text">{question.question}</div>

                {/* Concepts Tested */}
                {question.concepts_tested && question.concepts_tested.length > 0 && (
                  <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "16px" }}>
                    {question.concepts_tested.map((c, idx) => (
                      <span key={idx} style={{ fontSize: "11px", background: "#f8fafc", border: "1px solid #e2e8f0", padding: "3px 8px", borderRadius: "6px", color: "#64748b" }}>
                        #{c}
                      </span>
                    ))}
                  </div>
                )}

                {/* Question Input: MCQ or Open Text */}
                {question.options && question.options.length > 0 ? (
                  <div className="mcq-options">
                    {question.options.map((opt, idx) => (
                      <div
                        key={idx}
                        className={`mcq-option ${selectedMcq === opt ? "selected" : ""}`}
                        onClick={() => setSelectedMcq(opt)}
                      >
                        <input
                          type="radio"
                          name="mcq"
                          checked={selectedMcq === opt}
                          onChange={() => setSelectedMcq(opt)}
                        />
                        <span style={{ fontSize: "14px", fontWeight: 600 }}>{opt}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div>
                    <textarea
                      className="answer-box"
                      placeholder="Type your interview response clearly here..."
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                      disabled={!!evaluation}
                    />
                  </div>
                )}

                {error && <div style={{ color: "#ef4444", fontSize: "13px", marginTop: "10px" }}>{error}</div>}

                {/* Evaluation Card for current answer */}
                {evaluation ? (
                  <div className="evaluation-card">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                      <h3 style={{ margin: 0, fontSize: "16px", fontWeight: 800 }}>Answer Evaluation</h3>
                      <div style={{ fontSize: "18px", fontWeight: 900, color: evaluation.score >= 70 ? "#10b981" : "#f59e0b" }}>
                        Score: {evaluation.score}/100
                      </div>
                    </div>

                    {evaluation.adaptation_reason && (
                      <div style={{ background: "#fef3c7", color: "#92400e", padding: "8px 12px", borderRadius: "8px", fontSize: "12px", marginBottom: "12px" }}>
                        {evaluation.adaptation_reason}
                      </div>
                    )}

                    <p style={{ fontSize: "13px", color: "#475569", lineHeight: 1.5 }}>{evaluation.feedback}</p>

                    <div style={{ background: "#f8fafc", padding: "12px", borderRadius: "10px", marginTop: "10px", fontSize: "13px" }}>
                      <strong>Ideal Answer:</strong>
                      <p style={{ margin: "4px 0 0", color: "#334155" }}>{evaluation.ideal_answer}</p>
                    </div>

                    <div style={{ marginTop: "16px", display: "flex", justifyContent: "flex-end" }}>
                      <button className="next-button" onClick={proceedToNext}>
                        Continue to Next Question <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div style={{ marginTop: "18px", display: "flex", justifyContent: "flex-end" }}>
                    <button className="submit-button" onClick={submitAnswer} disabled={submitting}>
                      {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Submit Answer"}
                    </button>
                  </div>
                )}
              </div>
            ) : null}
          </>
        ) : (
          /* SESSION HISTORY TAB */
          <div className="history-card">
            <h2 style={{ margin: "0 0 16px", fontSize: "18px", fontWeight: 800 }}>Your Interview History</h2>
            {history.length === 0 ? (
              <p style={{ color: "#64748b", fontSize: "14px" }}>No past interview sessions found. Complete your first practice session!</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {history.map((h) => (
                  <div key={h.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 18px", border: "1px solid #e2e8f0", borderRadius: "12px" }}>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: "15px" }}>{h.interview_type} — {h.company}</div>
                      <div style={{ fontSize: "12px", color: "#64748b" }}>Role: {h.target_role} | Difficulty: {h.difficulty} | {new Date(h.created_at).toLocaleDateString()}</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "18px", fontWeight: 900, color: h.average_score >= 70 ? "#10b981" : "#f59e0b" }}>
                        {h.average_score}%
                      </div>
                      <span style={{ fontSize: "11px", textTransform: "capitalize", color: "#64748b" }}>{h.performance_level}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}