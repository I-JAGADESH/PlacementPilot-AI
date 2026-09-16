import { useEffect, useState } from "react";
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  Lightbulb,
  Loader2,
  RotateCcw,
  Target,
  TrendingDown,
  TrendingUp,
  Trophy,
  Zap,
} from "lucide-react";

import api from "../services/api";
import BackButton from "../components/BackButton";
import "../App.css";

// --- Aptitude Engine Types ---
interface TaxonomySubtopic {
  name: string;
  slug: string;
}

interface TaxonomyTopic {
  name: string;
  slug: string;
  subtopics: TaxonomySubtopic[];
}

interface TaxonomyDomain {
  name: string;
  slug: string;
  topics: TaxonomyTopic[];
}

interface CompanyPattern {
  id: number;
  name: string;
  slug: string;
  description?: string;
  total_questions: number;
  duration_minutes: number;
  negative_marking: number;
}

interface QuestionOption {
  key: string;
  text: string;
}

interface DIDatasetContent {
  columns: string[];
  rows: (string | number)[][];
}

interface AptitudeQuestion {
  question_id: number;
  question_order: number;
  difficulty: string;
  question_type: string;
  question_text: string;
  options: QuestionOption[];
  estimated_time_seconds: number;
  negative_marking: number;
  subtopic_name?: string;
  subtopic_slug?: string;
  di_dataset?: {
    title: string;
    description: string;
    content: DIDatasetContent;
  };
}

interface AptitudeStartResponse {
  assessment_id: number;
  mode: string;
  title: string;
  duration_seconds: number;
  total_questions: number;
  start_time: string;
  questions: AptitudeQuestion[];
}

interface AptitudeSubmitResult {
  assessment_id: number;
  mode: string;
  title: string;
  status: string;
  total_questions: number;
  attempted_questions: number;
  correct_answers: number;
  incorrect_answers: number;
  skipped_answers: number;
  raw_score: number;
  score_percentage: number;
  accuracy_percentage: number;
  speed_qpm: number;
  time_spent_seconds: number;
  domain_performance: Record<string, { total: number; correct: number }>;
  subtopic_performance: Record<string, { total: number; correct: number; subtopic_name: string }>;
  strong_topics: string[];
  weak_topics: string[];
  recommendations: string[];
}

interface FormulaReference {
  title: string;
  formula: string;
  concept_summary: string;
  when_to_use: string;
  important_notes: string;
  common_traps: string;
}

interface AnalyticsData {
  has_data: boolean;
  message?: string;
  overall_score: number;
  overall_accuracy: number;
  total_attempts: number;
  strongest_subtopics: { subtopic_name: string; subtopic_slug: string; accuracy: number; total_attempted: number }[];
  weakest_subtopics: { subtopic_name: string; subtopic_slug: string; accuracy: number; total_attempted: number }[];
  recent_attempts: { assessment_id: number; title: string; mode: string; score_percentage: number; accuracy_percentage: number; completed_at: string }[];
  recommendations: string[];
}

// --- Legacy Technical Skill Types ---
interface LegacyQuestion {
  id: number;
  skill: string;
  topic: string;
  question: string;
  options: string[];
}

interface LegacyStartResponse {
  assessment_id: number;
  skill: string;
  total_questions: number;
  questions: LegacyQuestion[];
}

interface LegacyTopicPerformance {
  topic: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
}

interface LegacyResult {
  assessment_id: number;
  skill: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  performance_level: string;
  topic_performance: LegacyTopicPerformance[];
  strong_topics: string[];
  weak_topics: string[];
  recommendations: string[];
}

const ASSESSMENT_MODES = [
  "Practice Mode",
  "Topic Practice",
  "Weak Topic Practice",
  "Retry Mode",
  "Full Mock Test",
  "Placement Test",
  "Company-pattern Test",
];

const FALLBACK_SKILLS = [
  "Algorithms",
  "Data Structures",
  "Python",
  "Java",
  "C++",
  "SQL",
  "React",
  "Git",
  "GitHub",
  "REST API",
];

export default function Assessment() {
  // Active Main Tab: 'aptitude' or 'legacy_skills'
  const [activeTab, setActiveTab] = useState<"aptitude" | "legacy_skills">("aptitude");

  // --- Aptitude Engine State ---
  const [mode, setMode] = useState<string>("Practice Mode");
  const [taxonomy, setTaxonomy] = useState<TaxonomyDomain[]>([]);
  const [selectedSubtopic, setSelectedSubtopic] = useState<string>("percentage");
  const [companyPatterns, setCompanyPatterns] = useState<CompanyPattern[]>([]);
  const [selectedPattern, setSelectedPattern] = useState<string>("company-pattern-a");
  const [numQuestions, setNumQuestions] = useState<number>(10);

  const [aptitudeSession, setAptitudeSession] = useState<AptitudeStartResponse | null>(null);
  const [currentQIndex, setCurrentQIndex] = useState<number>(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, { val: string; time: number }>>({});
  const [aptitudeResult, setAptitudeResult] = useState<AptitudeSubmitResult | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);

  // Formula Modal State
  const [activeFormula, setActiveFormula] = useState<FormulaReference | null>(null);

  // Timer State
  const [timeLeft, setTimeLeft] = useState<number>(1800);
  const [isTimerRunning, setIsTimerRunning] = useState<boolean>(false);

  // Status & Loaders
  const [loading, setLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  // --- Legacy Technical Skill State ---
  const [legacySkills, setLegacySkills] = useState<string[]>(FALLBACK_SKILLS);
  const [selectedLegacySkill, setSelectedLegacySkill] = useState<string>("Algorithms");
  const [legacyAssessment, setLegacyAssessment] = useState<LegacyStartResponse | null>(null);
  const [legacyResult, setLegacyResult] = useState<LegacyResult | null>(null);
  const [legacyQIndex, setLegacyQIndex] = useState<number>(0);
  const [legacyAnswers, setLegacyAnswers] = useState<Record<number, string>>({});
  const [loadingLegacySkills, setLoadingLegacySkills] = useState<boolean>(false);
  const [startingLegacy, setStartingLegacy] = useState<boolean>(false);
  const [submittingLegacy, setSubmittingLegacy] = useState<boolean>(false);

  useEffect(() => {
    loadTaxonomy();
    loadPatterns();
    loadAnalytics();
    loadLegacySkills();
  }, []);

  // Timer Countdown Effect for Aptitude Engine
  useEffect(() => {
    let timerId: any = null;
    if (isTimerRunning && timeLeft > 0) {
      timerId = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timerId);
            handleAutoSubmitOnTimeout();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timerId);
  }, [isTimerRunning, timeLeft]);

  // --- Aptitude API Loaders ---
  const loadTaxonomy = async () => {
    try {
      const res = await api.get("/aptitude/taxonomy");
      setTaxonomy(res.data || []);
    } catch (err: any) {
      console.error("Failed to load taxonomy", err);
    }
  };

  const loadPatterns = async () => {
    try {
      const res = await api.get("/aptitude/patterns");
      setCompanyPatterns(res.data || []);
    } catch (err: any) {
      console.error("Failed to load company patterns", err);
    }
  };

  const loadAnalytics = async () => {
    try {
      const res = await api.get("/aptitude/analytics");
      setAnalytics(res.data);
    } catch (err: any) {
      console.error("Failed to load analytics", err);
    }
  };

  const openFormulaModal = async (slug: string) => {
    try {
      const res = await api.get(`/aptitude/formulas/${slug}`);
      setActiveFormula(res.data);
    } catch (err: any) {
      console.error("Failed to fetch formula", err);
    }
  };

  const startAptitudeAssessment = async () => {
    setLoading(true);
    setError("");
    setAptitudeResult(null);
    setUserAnswers({});
    setCurrentQIndex(0);

    try {
      const payload = {
        mode,
        subtopic_slug: mode === "Topic Practice" ? selectedSubtopic : undefined,
        company_pattern_slug: mode === "Company-pattern Test" ? selectedPattern : undefined,
        num_questions: numQuestions,
      };

      const res = await api.post("/aptitude/assessments/start", payload);
      setAptitudeSession(res.data);
      setTimeLeft(res.data.duration_seconds || 1800);
      setIsTimerRunning(true);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to start aptitude assessment.");
    } finally {
      setLoading(false);
    }
  };

  const handleAutoSubmitOnTimeout = async () => {
    setIsTimerRunning(false);
    await submitAptitudeAssessment();
  };

  const submitAptitudeAssessment = async () => {
    if (!aptitudeSession) return;
    setSubmitting(true);
    setIsTimerRunning(false);

    try {
      const formattedAnswers = Object.entries(userAnswers).map(([qId, ans]) => ({
        question_id: Number(qId),
        selected_option_or_text: ans.val,
        time_spent_seconds: ans.time,
      }));

      const res = await api.post(`/aptitude/assessments/${aptitudeSession.assessment_id}/submit`, {
        answers: formattedAnswers,
      });

      setAptitudeResult(res.data);
      setAptitudeSession(null);
      loadAnalytics();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to submit assessment.");
    } finally {
      setSubmitting(false);
    }
  };

  const selectAnswer = (qId: number, answerVal: string) => {
    setUserAnswers((prev) => ({
      ...prev,
      [qId]: { val: answerVal, time: (prev[qId]?.time || 0) + 5 },
    }));
  };

  const formatTimer = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  // --- Legacy Skill Assessment Handlers ---
  const loadLegacySkills = async () => {
    try {
      setLoadingLegacySkills(true);
      const res = await api.get<{ skills: string[] }>("/api/v1/assessment/skills");
      if (res.data.skills?.length) {
        setLegacySkills(res.data.skills);
        if (!res.data.skills.includes(selectedLegacySkill)) {
          setSelectedLegacySkill(res.data.skills[0]);
        }
      }
    } catch (err: any) {
      console.error("Unable to load assessment skills:", err);
    } finally {
      setLoadingLegacySkills(false);
    }
  };

  const startLegacyAssessment = async (skillToStart?: string) => {
    const targetSkill = skillToStart || selectedLegacySkill;
    setSelectedLegacySkill(targetSkill);
    try {
      setStartingLegacy(true);
      setError("");
      setLegacyResult(null);
      setLegacyAssessment(null);
      setLegacyAnswers({});
      setLegacyQIndex(0);

      const res = await api.post<LegacyStartResponse>("/api/v1/assessment/start", {
        skill: targetSkill,
      });

      setLegacyAssessment(res.data);
    } catch (err: any) {
      console.error("Assessment start error:", err);
      setError(err?.response?.data?.detail || "Unable to start skill assessment. Please try again.");
    } finally {
      setStartingLegacy(false);
    }
  };

  const handleSelectLegacyOption = (option: string) => {
    if (!currentLegacyQ || submittingLegacy) return;
    setLegacyAnswers((prev) => ({
      ...prev,
      [currentLegacyQ.id]: option,
    }));
  };

  const submitLegacyAssessment = async () => {
    if (!legacyAssessment || submittingLegacy) return;

    try {
      setSubmittingLegacy(true);
      setError("");

      const submittedAnswers = legacyAssessment.questions.map((q) => ({
        question_id: q.id,
        selected_option: legacyAnswers[q.id] || "",
      }));

      const res = await api.post<LegacyResult>("/api/v1/assessment/submit", {
        assessment_id: legacyAssessment.assessment_id,
        answers: submittedAnswers,
      });

      setLegacyResult(res.data);
      setLegacyAssessment(null);
    } catch (err: any) {
      console.error("Assessment submission error:", err);
      setError(err?.response?.data?.detail || "Unable to submit assessment. Please try again.");
    } finally {
      setSubmittingLegacy(false);
    }
  };

  const restartLegacyAssessment = () => {
    setLegacyAssessment(null);
    setLegacyResult(null);
    setLegacyAnswers({});
    setLegacyQIndex(0);
    setError("");
  };

  const currentQ = aptitudeSession?.questions[currentQIndex];
  const currentLegacyQ = legacyAssessment?.questions[legacyQIndex];

  return (
    <div className="page-container">
      <div className="page-header flex justify-between items-center mb-6">
        <div>
          <BackButton />
          <h1 className="page-title text-2xl font-bold flex items-center gap-2 mt-2">
            <Trophy className="w-7 h-7 text-amber-500" /> Placement & Skill Assessment Engine
          </h1>
          <p className="page-subtitle text-gray-400">
            Comprehensive quantitative aptitude preparation & domain technical skill assessments.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-gray-800 p-1 rounded-lg border border-gray-700">
          <button
            onClick={() => setActiveTab("aptitude")}
            className={`px-4 py-2 text-sm font-semibold rounded-md transition ${
              activeTab === "aptitude" ? "bg-amber-500 text-gray-900 shadow" : "text-gray-400 hover:text-white"
            }`}
          >
            Aptitude Engine
          </button>
          <button
            onClick={() => setActiveTab("legacy_skills")}
            className={`px-4 py-2 text-sm font-semibold rounded-md transition ${
              activeTab === "legacy_skills" ? "bg-amber-500 text-gray-900 shadow" : "text-gray-400 hover:text-white"
            }`}
          >
            Technical Skill Tests
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-900/40 border border-rose-500/50 text-rose-200 p-4 rounded-xl mb-6 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* ============================================================ */}
      {/* 1. APTITUDE PREPARATION ENGINE VIEW */}
      {/* ============================================================ */}
      {activeTab === "aptitude" && (
        <div>
          {/* SETUP / MODE SELECTOR (When no active session & no result) */}
          {!aptitudeSession && !aptitudeResult && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Setup Box */}
              <div className="lg:col-span-2 bg-gray-900/90 border border-gray-800 p-6 rounded-2xl shadow-xl">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-amber-400" /> Configure Assessment Mode
                </h2>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
                  {ASSESSMENT_MODES.map((m) => (
                    <button
                      key={m}
                      onClick={() => setMode(m)}
                      className={`p-4 rounded-xl text-left border transition ${
                        mode === m
                          ? "bg-amber-500/10 border-amber-500 text-amber-300 font-semibold"
                          : "bg-gray-800/60 border-gray-700/60 text-gray-300 hover:bg-gray-800"
                      }`}
                    >
                      <div className="font-bold text-sm mb-1">{m}</div>
                      <div className="text-xs text-gray-400">
                        {m === "Practice Mode" && "Randomized quantitative & reasoning practice."}
                        {m === "Topic Practice" && "Deep-dive focus into a specific normalized subtopic."}
                        {m === "Weak Topic Practice" && "Target topics with lowest historical accuracy."}
                        {m === "Retry Mode" && "Re-attempt questions previously answered incorrectly."}
                        {m === "Full Mock Test" && "Timed comprehensive 30-question placement simulation."}
                        {m === "Placement Test" && "High-intensity diagnostic aptitude benchmark."}
                        {m === "Company-pattern Test" && "Structured placement-style company pattern."}
                      </div>
                    </button>
                  ))}
                </div>

                {/* Subtopic Selector if Topic Practice */}
                {mode === "Topic Practice" && (
                  <div className="mb-6 bg-gray-800/40 p-4 rounded-xl border border-gray-700">
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Select Subtopic:</label>
                    <select
                      value={selectedSubtopic}
                      onChange={(e) => setSelectedSubtopic(e.target.value)}
                      className="w-full bg-gray-800 text-white border border-gray-700 p-3 rounded-lg focus:outline-none focus:border-amber-500"
                    >
                      {taxonomy.map((domain) => (
                        <optgroup key={domain.slug} label={domain.name}>
                          {domain.topics.flatMap((topic) =>
                            topic.subtopics.map((st) => (
                              <option key={st.slug} value={st.slug}>
                                {st.name}
                              </option>
                            ))
                          )}
                        </optgroup>
                      ))}
                    </select>
                  </div>
                )}

                {/* Company Pattern Selector if Pattern Test */}
                {mode === "Company-pattern Test" && (
                  <div className="mb-6 bg-gray-800/40 p-4 rounded-xl border border-gray-700">
                    <label className="block text-sm font-semibold text-gray-300 mb-2">Select Company Pattern:</label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {companyPatterns.map((cp) => (
                        <div
                          key={cp.slug}
                          onClick={() => setSelectedPattern(cp.slug)}
                          className={`p-3 rounded-lg border cursor-pointer ${
                            selectedPattern === cp.slug
                              ? "bg-amber-500/20 border-amber-500 text-white"
                              : "bg-gray-800 border-gray-700 text-gray-400"
                          }`}
                        >
                          <div className="font-semibold text-sm">{cp.name}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            {cp.total_questions} Questions • {cp.duration_minutes} Mins • -{cp.negative_marking} Neg
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between mt-6">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-400">Questions:</span>
                    <select
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(Number(e.target.value))}
                      className="bg-gray-800 text-white border border-gray-700 p-2 rounded-lg text-sm"
                    >
                      <option value={5}>5 Questions</option>
                      <option value={10}>10 Questions</option>
                      <option value={15}>15 Questions</option>
                      <option value={20}>20 Questions</option>
                    </select>
                  </div>

                  <button
                    onClick={startAptitudeAssessment}
                    disabled={loading}
                    className="bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold px-6 py-3 rounded-xl shadow-lg flex items-center gap-2 transition disabled:opacity-50"
                  >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                    Start Assessment
                  </button>
                </div>
              </div>

              {/* Analytics Sidebar */}
              <div className="bg-gray-900/90 border border-gray-800 p-6 rounded-2xl shadow-xl">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-amber-400" /> Aptitude Performance Snapshot
                </h2>

                {analytics?.has_data ? (
                  <div>
                    <div className="grid grid-cols-2 gap-3 mb-4">
                      <div className="bg-gray-800/60 p-3 rounded-xl text-center border border-gray-700">
                        <div className="text-xs text-gray-400">Overall Accuracy</div>
                        <div className="text-xl font-black text-amber-400">{analytics.overall_accuracy}%</div>
                      </div>
                      <div className="bg-gray-800/60 p-3 rounded-xl text-center border border-gray-700">
                        <div className="text-xs text-gray-400">Total Attempts</div>
                        <div className="text-xl font-black text-white">{analytics.total_attempts}</div>
                      </div>
                    </div>

                    {analytics.weakest_subtopics.length > 0 && (
                      <div className="mb-4">
                        <div className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">Weakest Subtopics:</div>
                        <div className="space-y-1">
                          {analytics.weakest_subtopics.map((item) => (
                            <div key={item.subtopic_slug} className="flex justify-between text-xs bg-rose-950/30 p-2 rounded border border-rose-900/40">
                              <span className="text-gray-300">{item.subtopic_name}</span>
                              <span className="font-bold text-rose-400">{item.accuracy}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-gray-400 py-6 text-center">
                    No completed aptitude attempts yet. Complete your first assessment to unlock diagnostic analytics!
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ACTIVE ASSESSMENT TEST INTERFACE */}
          {aptitudeSession && currentQ && (
            <div className="bg-gray-900/95 border border-gray-800 p-6 rounded-2xl shadow-2xl">
              {/* Header Info & Timer */}
              <div className="flex flex-wrap justify-between items-center pb-4 mb-6 border-b border-gray-800 gap-4">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    {aptitudeSession.title}
                  </h2>
                  <span className="text-xs text-amber-400 bg-amber-950/50 px-2 py-0.5 rounded border border-amber-800/50">
                    Question {currentQIndex + 1} of {aptitudeSession.total_questions}
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm font-mono font-bold ${
                    timeLeft < 300 ? "bg-rose-950/60 border-rose-600 text-rose-300 animate-pulse" : "bg-gray-800 border-gray-700 text-amber-400"
                  }`}>
                    <Clock className="w-4 h-4" />
                    <span>{formatTimer(timeLeft)}</span>
                  </div>

                  <button
                    onClick={submitAptitudeAssessment}
                    disabled={submitting}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded-xl text-sm transition"
                  >
                    {submitting ? "Submitting..." : "Finish Test"}
                  </button>
                </div>
              </div>

              {/* Data Interpretation Shared Dataset Block if present */}
              {currentQ.di_dataset && (
                <div className="mb-6 bg-gray-800/60 border border-gray-700 p-4 rounded-xl">
                  <h3 className="text-md font-bold text-amber-300 mb-1">{currentQ.di_dataset.title}</h3>
                  <p className="text-xs text-gray-400 mb-3">{currentQ.di_dataset.description}</p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left text-gray-300 border-collapse">
                      <thead>
                        <tr className="bg-gray-700 text-amber-400">
                          {currentQ.di_dataset.content.columns.map((col, idx) => (
                            <th key={idx} className="p-2 border border-gray-600">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {currentQ.di_dataset.content.rows.map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-gray-750">
                            {row.map((cell, cIdx) => (
                              <td key={cIdx} className="p-2 border border-gray-700">{cell}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Question Text */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">
                    {currentQ.subtopic_name || "Aptitude Problem"} • {currentQ.difficulty}
                  </span>
                  {currentQ.subtopic_slug && (
                    <button
                      onClick={() => openFormulaModal(currentQ.subtopic_slug!)}
                      className="text-xs text-amber-400 hover:underline flex items-center gap-1"
                    >
                      <Lightbulb className="w-3.5 h-3.5" /> Formula Cheat Sheet
                    </button>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-white leading-relaxed">{currentQ.question_text}</h3>
              </div>

              {/* Answer Options / Numerical Input */}
              {currentQ.question_type === "Numerical" ? (
                <div className="mb-8">
                  <label className="block text-sm text-gray-300 mb-2 font-semibold">Enter Numerical Answer:</label>
                  <input
                    type="number"
                    step="any"
                    value={userAnswers[currentQ.question_id]?.val || ""}
                    onChange={(e) => selectAnswer(currentQ.question_id, e.target.value)}
                    placeholder="Type number..."
                    className="w-full sm:w-64 bg-gray-800 border border-gray-700 text-white p-3 rounded-xl focus:outline-none focus:border-amber-500 text-lg font-mono"
                  />
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
                  {currentQ.options.map((opt) => {
                    const isSelected = userAnswers[currentQ.question_id]?.val === opt.key;
                    return (
                      <button
                        key={opt.key}
                        onClick={() => selectAnswer(currentQ.question_id, opt.key)}
                        className={`p-4 rounded-xl text-left border flex items-center gap-3 transition ${
                          isSelected
                            ? "bg-amber-500/20 border-amber-500 text-amber-200 font-semibold"
                            : "bg-gray-800/60 border-gray-700/70 text-gray-300 hover:bg-gray-800"
                        }`}
                      >
                        <span className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs ${
                          isSelected ? "bg-amber-500 text-gray-950" : "bg-gray-700 text-gray-300"
                        }`}>
                          {opt.key}
                        </span>
                        <span className="text-sm">{opt.text}</span>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Question Navigation Footer */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                <button
                  disabled={currentQIndex === 0}
                  onClick={() => setCurrentQIndex((prev) => prev - 1)}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-sm font-semibold flex items-center gap-1 disabled:opacity-40"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>

                {/* Question Palette Grid */}
                <div className="hidden md:flex gap-1">
                  {aptitudeSession.questions.map((q, idx) => {
                    const isAnswered = !!userAnswers[q.question_id]?.val;
                    const isCurrent = idx === currentQIndex;
                    return (
                      <button
                        key={q.question_id}
                        onClick={() => setCurrentQIndex(idx)}
                        className={`w-7 h-7 rounded-md text-xs font-bold transition ${
                          isCurrent
                            ? "ring-2 ring-amber-400 bg-amber-500 text-gray-950"
                            : isAnswered
                            ? "bg-emerald-900/60 text-emerald-300 border border-emerald-700"
                            : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                        }`}
                      >
                        {idx + 1}
                      </button>
                    );
                  })}
                </div>

                <button
                  disabled={currentQIndex === aptitudeSession.total_questions - 1}
                  onClick={() => setCurrentQIndex((prev) => prev + 1)}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-sm font-semibold flex items-center gap-1 disabled:opacity-40"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* DIAGNOSTIC RESULT DASHBOARD */}
          {aptitudeResult && (
            <div className="bg-gray-900/95 border border-gray-800 p-6 rounded-2xl shadow-2xl">
              <div className="text-center pb-6 border-b border-gray-800 mb-6">
                <Trophy className="w-12 h-12 text-amber-400 mx-auto mb-2" />
                <h2 className="text-2xl font-bold text-white">{aptitudeResult.title} Results</h2>
                <p className="text-sm text-gray-400 mt-1">Diagnostic Score & Subtopic Analysis</p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-800/60 p-4 rounded-xl border border-gray-700 text-center">
                  <div className="text-xs text-gray-400 mb-1">Score Percentage</div>
                  <div className="text-2xl font-black text-amber-400">{aptitudeResult.score_percentage}%</div>
                </div>
                <div className="bg-gray-800/60 p-4 rounded-xl border border-gray-700 text-center">
                  <div className="text-xs text-gray-400 mb-1">Accuracy</div>
                  <div className="text-2xl font-black text-emerald-400">{aptitudeResult.accuracy_percentage}%</div>
                </div>
                <div className="bg-gray-800/60 p-4 rounded-xl border border-gray-700 text-center">
                  <div className="text-xs text-gray-400 mb-1">Correct / Total</div>
                  <div className="text-2xl font-black text-white">{aptitudeResult.correct_answers} / {aptitudeResult.total_questions}</div>
                </div>
                <div className="bg-gray-800/60 p-4 rounded-xl border border-gray-700 text-center">
                  <div className="text-xs text-gray-400 mb-1">Raw Score</div>
                  <div className="text-2xl font-black text-indigo-400">{aptitudeResult.raw_score}</div>
                </div>
              </div>

              {/* Recommendations Box */}
              {aptitudeResult.recommendations.length > 0 && (
                <div className="bg-amber-950/30 border border-amber-800/50 p-4 rounded-xl mb-6">
                  <h4 className="text-sm font-bold text-amber-300 mb-2 flex items-center gap-1.5">
                    <Lightbulb className="w-4 h-4" /> Actionable Recommendations:
                  </h4>
                  <ul className="list-disc list-inside text-xs text-gray-300 space-y-1">
                    {aptitudeResult.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex justify-center gap-4 mt-6">
                <button
                  onClick={() => setAptitudeResult(null)}
                  className="bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold px-6 py-3 rounded-xl shadow transition"
                >
                  Start Another Session
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Formula Modal Overlay */}
      {activeFormula && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-gray-700 p-6 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-amber-400 mb-2">{activeFormula.title}</h3>
            <div className="bg-gray-800 p-3 rounded-xl font-mono text-sm text-emerald-300 mb-4 border border-gray-700">
              {activeFormula.formula}
            </div>
            <div className="space-y-3 text-xs text-gray-300 mb-6">
              <div><strong className="text-amber-300">Concept:</strong> {activeFormula.concept_summary}</div>
              <div><strong className="text-amber-300">When To Use:</strong> {activeFormula.when_to_use}</div>
              <div><strong className="text-amber-300">Important Notes:</strong> {activeFormula.important_notes}</div>
              <div><strong className="text-rose-400">Common Traps:</strong> {activeFormula.common_traps}</div>
            </div>
            <button
              onClick={() => setActiveFormula(null)}
              className="w-full py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-xl text-sm font-semibold"
            >
              Close Cheat Sheet
            </button>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* 2. LEGACY TECHNICAL SKILLS VIEW */}
      {/* ============================================================ */}
      {activeTab === "legacy_skills" && (
        <div>
          {/* SETUP VIEW: Skill Selector */}
          {!legacyAssessment && !legacyResult && (
            <div className="bg-gray-900/90 border border-gray-800 p-6 rounded-2xl">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-5 h-5 text-indigo-400" />
                <h2 className="text-xl font-bold text-white">Technical Skill Assessment</h2>
              </div>
              <p className="text-sm text-gray-400 mb-6">
                Evaluate your core domain programming knowledge with placement-focused MCQs and topic analysis.
              </p>

              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-300 mb-3">Select Technical Skill:</label>
                <div className="flex justify-start gap-2 flex-wrap mb-4">
                  {legacySkills.map((sk) => (
                    <button
                      key={sk}
                      onClick={() => setSelectedLegacySkill(sk)}
                      className={`px-4 py-2.5 rounded-xl text-xs font-semibold border transition ${
                        selectedLegacySkill === sk
                          ? "bg-indigo-600 text-white border-indigo-500 shadow-md"
                          : "bg-gray-800/80 border-gray-700 text-gray-300 hover:bg-gray-800"
                      }`}
                    >
                      {sk}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => startLegacyAssessment()}
                  disabled={startingLegacy || loadingLegacySkills}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-6 py-3 rounded-xl shadow-lg flex items-center gap-2 transition disabled:opacity-50"
                >
                  {startingLegacy ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Trophy className="w-5 h-5" />
                  )}
                  {startingLegacy ? "Starting..." : `Start ${selectedLegacySkill} Assessment`}
                </button>
              </div>
            </div>
          )}

          {/* ACTIVE LEGACY ASSESSMENT QUESTION VIEW */}
          {legacyAssessment && currentLegacyQ && (
            <div className="bg-gray-900/95 border border-gray-800 p-6 rounded-2xl shadow-2xl">
              <div className="flex flex-wrap justify-between items-center pb-4 mb-6 border-b border-gray-800 gap-4">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    {legacyAssessment.skill} Skill Assessment
                  </h2>
                  <span className="text-xs text-indigo-400 bg-indigo-950/50 px-2 py-0.5 rounded border border-indigo-800/50">
                    Question {legacyQIndex + 1} of {legacyAssessment.total_questions}
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-xs text-gray-400">
                    Answered: {Object.keys(legacyAnswers).length} / {legacyAssessment.total_questions}
                  </span>
                  <button
                    onClick={submitLegacyAssessment}
                    disabled={submittingLegacy}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded-xl text-sm transition"
                  >
                    {submittingLegacy ? "Submitting..." : "Submit Test"}
                  </button>
                </div>
              </div>

              {/* Question Text & Topic */}
              <div className="mb-6">
                <div className="text-xs text-indigo-400 uppercase tracking-wider font-semibold mb-2">
                  Topic: {currentLegacyQ.topic}
                </div>
                <h3 className="text-lg font-semibold text-white leading-relaxed">{currentLegacyQ.question}</h3>
              </div>

              {/* Question Options */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
                {currentLegacyQ.options.map((opt, idx) => {
                  const isSelected = legacyAnswers[currentLegacyQ.id] === opt;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelectLegacyOption(opt)}
                      className={`p-4 rounded-xl text-left border flex items-center gap-3 transition ${
                        isSelected
                          ? "bg-indigo-600/20 border-indigo-500 text-indigo-200 font-semibold"
                          : "bg-gray-800/60 border-gray-700/70 text-gray-300 hover:bg-gray-800"
                      }`}
                    >
                      <span className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs ${
                        isSelected ? "bg-indigo-600 text-white" : "bg-gray-700 text-gray-300"
                      }`}>
                        {chr(65 + idx)}
                      </span>
                      <span className="text-sm">{opt}</span>
                    </button>
                  );
                })}
              </div>

              {/* Navigation Footer */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                <button
                  disabled={legacyQIndex === 0}
                  onClick={() => setLegacyQIndex((prev) => Math.max(prev - 1, 0))}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-sm font-semibold flex items-center gap-1 disabled:opacity-40"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>

                <span className="text-xs text-gray-400 font-semibold">
                  {legacyQIndex + 1} / {legacyAssessment.total_questions}
                </span>

                <button
                  disabled={legacyQIndex === legacyAssessment.total_questions - 1}
                  onClick={() => setLegacyQIndex((prev) => Math.min(prev + 1, legacyAssessment.questions.length - 1))}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-sm font-semibold flex items-center gap-1 disabled:opacity-40"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* LEGACY RESULT DISPLAY */}
          {legacyResult && (
            <div className="bg-gray-900/95 border border-gray-800 p-6 rounded-2xl shadow-2xl">
              <div className="text-center pb-6 border-b border-gray-800 mb-6">
                <Trophy className="w-12 h-12 text-indigo-400 mx-auto mb-2" />
                <h2 className="text-2xl font-bold text-white">{legacyResult.skill} Assessment Result</h2>
                <span className="inline-block mt-2 px-3 py-1 bg-indigo-950 text-indigo-300 border border-indigo-800 rounded-full text-xs font-bold">
                  Level: {legacyResult.performance_level}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-800/60 p-4 rounded-xl border border-gray-700 text-center">
                  <div className="text-xs text-gray-400 mb-1">Score Percentage</div>
                  <div className="text-2xl font-black text-indigo-400">{legacyResult.score_percentage}%</div>
                </div>
                <div className="bg-gray-800/60 p-4 rounded-xl border border-gray-700 text-center">
                  <div className="text-xs text-gray-400 mb-1">Correct Answers</div>
                  <div className="text-2xl font-black text-emerald-400">{legacyResult.correct_answers} / {legacyResult.total_questions}</div>
                </div>
                <div className="bg-gray-800/60 p-4 rounded-xl border border-gray-700 text-center col-span-2 sm:col-span-1">
                  <div className="text-xs text-gray-400 mb-1">Skill Evaluated</div>
                  <div className="text-lg font-bold text-white">{legacyResult.skill}</div>
                </div>
              </div>

              {/* Topic Performance Breakdown Table */}
              {legacyResult.topic_performance?.length > 0 && (
                <div className="mb-6 bg-gray-800/40 p-4 rounded-xl border border-gray-700">
                  <h4 className="text-sm font-bold text-gray-200 mb-3 flex items-center gap-1.5">
                    <BookOpen className="w-4 h-4 text-indigo-400" /> Topic Performance Breakdown
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left text-gray-300">
                      <thead>
                        <tr className="bg-gray-800 text-indigo-300">
                          <th className="p-2.5 rounded-l-lg">Topic</th>
                          <th className="p-2.5">Questions</th>
                          <th className="p-2.5">Correct</th>
                          <th className="p-2.5 rounded-r-lg">Accuracy %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {legacyResult.topic_performance.map((tp, idx) => (
                          <tr key={idx} className="border-b border-gray-800/60">
                            <td className="p-2.5 font-medium">{tp.topic}</td>
                            <td className="p-2.5">{tp.total_questions}</td>
                            <td className="p-2.5 text-emerald-400 font-semibold">{tp.correct_answers}</td>
                            <td className="p-2.5 font-bold text-indigo-400">{tp.score_percentage}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Recommendations & Strengths */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                {legacyResult.strong_topics?.length > 0 && (
                  <div className="bg-emerald-950/20 border border-emerald-900/50 p-4 rounded-xl">
                    <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Strong Topics:
                    </h5>
                    <ul className="text-xs text-gray-300 space-y-1">
                      {legacyResult.strong_topics.map((st, i) => (
                        <li key={i}>• {st}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {legacyResult.weak_topics?.length > 0 && (
                  <div className="bg-rose-950/20 border border-rose-900/50 p-4 rounded-xl">
                    <h5 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <TrendingDown className="w-3.5 h-3.5" /> Weak Topics:
                    </h5>
                    <ul className="text-xs text-gray-300 space-y-1">
                      {legacyResult.weak_topics.map((wt, i) => (
                        <li key={i}>• {wt}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {legacyResult.recommendations?.length > 0 && (
                <div className="bg-indigo-950/30 border border-indigo-800/50 p-4 rounded-xl mb-6">
                  <h4 className="text-sm font-bold text-indigo-300 mb-2 flex items-center gap-1.5">
                    <Lightbulb className="w-4 h-4" /> Recommended Next Steps:
                  </h4>
                  <ul className="list-disc list-inside text-xs text-gray-300 space-y-1">
                    {legacyResult.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex justify-center mt-6">
                <button
                  onClick={restartLegacyAssessment}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-6 py-3 rounded-xl shadow transition flex items-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" /> Attempt Another Skill Assessment
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function chr(code: number): string {
  return String.fromCharCode(code);
}
