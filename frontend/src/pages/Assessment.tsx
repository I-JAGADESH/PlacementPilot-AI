import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertCircle,
  Award,
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Lightbulb,
  Loader2,
  RotateCcw,
  Target,
  TrendingDown,
  TrendingUp,
  Trophy,
} from "lucide-react";

import api from "../services/api";
import BackButton from "../components/BackButton";
import "../App.css";

interface AssessmentQuestion {
  id: number;
  skill: string;
  topic: string;
  question: string;
  options: string[];
}

interface AssessmentStartResponse {
  assessment_id: number;
  skill: string;
  total_questions: number;
  questions: AssessmentQuestion[];
}

interface TopicPerformance {
  topic: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
}

interface AssessmentResult {
  assessment_id: number;
  skill: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  performance_level: string;
  topic_performance: TopicPerformance[];
  strong_topics: string[];
  weak_topics: string[];
  recommendations: string[];
}

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
  const navigate = useNavigate();

  const [skills, setSkills] = useState<string[]>(FALLBACK_SKILLS);
  const [selectedSkill, setSelectedSkill] = useState("Algorithms");

  const [assessment, setAssessment] =
    useState<AssessmentStartResponse | null>(null);

  const [result, setResult] = useState<AssessmentResult | null>(null);

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  const [answers, setAnswers] = useState<Record<number, string>>({});

  const [loadingSkills, setLoadingSkills] = useState(false);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState("");

  const currentQuestion = useMemo(() => {
    if (!assessment || assessment.questions.length === 0) {
      return null;
    }

    return assessment.questions[currentQuestionIndex];
  }, [assessment, currentQuestionIndex]);

  const answeredCount = useMemo(() => {
    return Object.keys(answers).length;
  }, [answers]);

  const progressPercentage = useMemo(() => {
    if (!assessment || assessment.total_questions === 0) {
      return 0;
    }

    return Math.round(
      ((currentQuestionIndex + 1) / assessment.total_questions) * 100
    );
  }, [assessment, currentQuestionIndex]);

  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    try {
      setLoadingSkills(true);

      const response = await api.get<{ skills: string[] }>(
        "/api/v1/assessment/skills"
      );

      if (response.data.skills?.length) {
        setSkills(response.data.skills);

        if (!response.data.skills.includes(selectedSkill)) {
          setSelectedSkill(response.data.skills[0]);
        }
      }
    } catch (err) {
      console.error("Unable to load assessment skills:", err);
    } finally {
      setLoadingSkills(false);
    }
  };

  const startAssessment = async () => {
    try {
      setStarting(true);
      setError("");
      setResult(null);
      setAssessment(null);
      setAnswers({});
      setCurrentQuestionIndex(0);

      const response = await api.post<AssessmentStartResponse>(
        "/api/v1/assessment/start",
        {
          skill: selectedSkill,
        }
      );

      setAssessment(response.data);
    } catch (err: any) {
      console.error("Assessment start error:", err);

      const message =
        err?.response?.data?.detail ||
        "Unable to start the assessment. Please try again.";

      setError(message);
    } finally {
      setStarting(false);
    }
  };

  const handleSelectOption = (option: string) => {
    if (!currentQuestion || submitting) {
      return;
    }

    setAnswers((previous) => ({
      ...previous,
      [currentQuestion.id]: option,
    }));
  };

  const handlePrevious = () => {
    setCurrentQuestionIndex((previous) => Math.max(previous - 1, 0));
  };

  const handleNext = () => {
    if (!assessment) {
      return;
    }

    setCurrentQuestionIndex((previous) =>
      Math.min(previous + 1, assessment.questions.length - 1)
    );
  };

  const submitAssessment = async () => {
    if (!assessment || submitting) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const submittedAnswers = assessment.questions.map((question) => ({
        question_id: question.id,
        selected_option: answers[question.id] || "",
      }));

      const response = await api.post<AssessmentResult>(
        "/api/v1/assessment/submit",
        {
          assessment_id: assessment.assessment_id,
          answers: submittedAnswers,
        }
      );

      setResult(response.data);
    } catch (err: any) {
      console.error("Assessment submission error:", err);

      const message =
        err?.response?.data?.detail ||
        "Unable to submit the assessment. Please try again.";

      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const restartAssessment = () => {
    setAssessment(null);
    setResult(null);
    setAnswers({});
    setCurrentQuestionIndex(0);
    setError("");
  };

  const getScoreLabel = (score: number) => {
    if (score >= 85) {
      return "Excellent";
    }

    if (score >= 70) {
      return "Strong";
    }

    if (score >= 50) {
      return "Developing";
    }

    return "Needs Improvement";
  };

  const getScoreDescription = (score: number) => {
    if (score >= 85) {
      return "Excellent understanding. You are ready for harder placement-level practice.";
    }

    if (score >= 70) {
      return "Good foundation. Strengthen your weaker topics and continue interview practice.";
    }

    if (score >= 50) {
      return "You have a developing foundation. Focus on your weak topics before progressing.";
    }

    return "Your fundamentals need improvement. Complete the relevant training topics and retry.";
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(180deg, #f8fafc 0%, #ffffff 45%, #f8fafc 100%)",
        color: "#101828",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "28px 28px 60px",
        }}
      >
        <BackButton />

        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: "24px",
            flexWrap: "wrap",
            marginBottom: "28px",
          }}
        >
          <div>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "7px 12px",
                borderRadius: "999px",
                background: "#eef4ff",
                color: "#175cd3",
                fontSize: "12px",
                fontWeight: 800,
                marginBottom: "12px",
              }}
            >
              <Target size={15} />
              PLACEMENT ASSESSMENT
            </div>

            <h1
              style={{
                margin: 0,
                fontSize: "32px",
                lineHeight: 1.2,
                fontWeight: 800,
                letterSpacing: "-0.7px",
              }}
            >
              Skill Assessment
            </h1>

            <p
              style={{
                margin: "10px 0 0",
                maxWidth: "720px",
                color: "#667085",
                fontSize: "15px",
                lineHeight: 1.6,
              }}
            >
              Test your understanding, identify weak topics and get a
              personalized recommendation for your next preparation step.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate("/training")}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "11px 16px",
              borderRadius: "10px",
              border: "1px solid #d0d5dd",
              background: "#ffffff",
              color: "#344054",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            <BookOpen size={17} />
            Continue Training
          </button>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              marginBottom: "18px",
              padding: "13px 15px",
              borderRadius: "10px",
              background: "#fef3f2",
              border: "1px solid #fecdca",
              color: "#b42318",
              display: "flex",
              alignItems: "center",
              gap: "9px",
              fontSize: "13px",
              fontWeight: 600,
            }}
          >
            <AlertCircle size={17} />
            {error}
          </div>
        )}

        {/* RESULT */}
        {result ? (
          <div>
            {/* Score Hero */}
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "18px",
                padding: "32px",
                boxShadow: "0 4px 14px rgba(16, 24, 40, 0.05)",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "28px",
                  flexWrap: "wrap",
                }}
              >
                <div
                  style={{
                    width: "150px",
                    height: "150px",
                    borderRadius: "50%",
                    border: "10px solid #dbeafe",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexDirection: "column",
                    flexShrink: 0,
                    background: "#f8fbff",
                  }}
                >
                  <strong
                    style={{
                      fontSize: "36px",
                      lineHeight: 1,
                      fontWeight: 800,
                      color: "#175cd3",
                    }}
                  >
                    {Math.round(result.score_percentage)}
                  </strong>

                  <span
                    style={{
                      marginTop: "5px",
                      fontSize: "12px",
                      color: "#667085",
                      fontWeight: 700,
                    }}
                  >
                    / 100
                  </span>
                </div>

                <div style={{ flex: 1, minWidth: "250px" }}>
                  <div
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "7px",
                      padding: "7px 11px",
                      borderRadius: "999px",
                      background: "#f0fdf4",
                      color: "#15803d",
                      fontSize: "12px",
                      fontWeight: 800,
                      marginBottom: "10px",
                    }}
                  >
                    <Trophy size={15} />
                    {getScoreLabel(result.score_percentage)}
                  </div>

                  <h2
                    style={{
                      margin: "0 0 7px",
                      fontSize: "26px",
                      fontWeight: 800,
                    }}
                  >
                    {result.skill} Assessment
                  </h2>

                  <p
                    style={{
                      margin: 0,
                      color: "#667085",
                      fontSize: "14px",
                      lineHeight: 1.6,
                      maxWidth: "700px",
                    }}
                  >
                    {getScoreDescription(result.score_percentage)}
                  </p>

                  <div
                    style={{
                      display: "flex",
                      gap: "12px",
                      marginTop: "18px",
                      flexWrap: "wrap",
                    }}
                  >
                    <div
                      style={{
                        padding: "10px 14px",
                        borderRadius: "10px",
                        background: "#f8fafc",
                        border: "1px solid #eaecf0",
                        fontSize: "13px",
                      }}
                    >
                      <strong>{result.correct_answers}</strong> correct
                    </div>

                    <div
                      style={{
                        padding: "10px 14px",
                        borderRadius: "10px",
                        background: "#f8fafc",
                        border: "1px solid #eaecf0",
                        fontSize: "13px",
                      }}
                    >
                      <strong>{result.total_questions}</strong> questions
                    </div>

                    <div
                      style={{
                        padding: "10px 14px",
                        borderRadius: "10px",
                        background: "#f8fafc",
                        border: "1px solid #eaecf0",
                        fontSize: "13px",
                      }}
                    >
                      <strong>{result.weak_topics.length}</strong> weak topics
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Topic Performance */}
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "16px",
                padding: "24px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "9px",
                  marginBottom: "18px",
                }}
              >
                <Target size={19} />
                <h2
                  style={{
                    margin: 0,
                    fontSize: "18px",
                    fontWeight: 800,
                  }}
                >
                  Topic Performance
                </h2>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(260px, 1fr))",
                  gap: "12px",
                }}
              >
                {result.topic_performance.map((topic) => {
                  const strong = topic.score_percentage >= 70;

                  return (
                    <div
                      key={topic.topic}
                      style={{
                        padding: "16px",
                        borderRadius: "12px",
                        border: "1px solid #eaecf0",
                        background: "#ffffff",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: "12px",
                          alignItems: "center",
                          marginBottom: "10px",
                        }}
                      >
                        <strong style={{ fontSize: "14px" }}>
                          {topic.topic}
                        </strong>

                        <span
                          style={{
                            fontSize: "13px",
                            fontWeight: 800,
                            color: strong ? "#15803d" : "#d92d20",
                          }}
                        >
                          {topic.score_percentage}%
                        </span>
                      </div>

                      <div
                        style={{
                          height: "8px",
                          borderRadius: "999px",
                          background: "#eaecf0",
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            width: `${Math.min(
                              Math.max(topic.score_percentage, 0),
                              100
                            )}%`,
                            height: "100%",
                            borderRadius: "999px",
                            background: strong
                              ? "#22c55e"
                              : "#f97316",
                            transition: "width 0.4s ease",
                          }}
                        />
                      </div>

                      <div
                        style={{
                          marginTop: "8px",
                          color: "#667085",
                          fontSize: "11px",
                        }}
                      >
                        {topic.correct_answers} of {topic.total_questions}{" "}
                        correct
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Strong + Weak */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "18px",
                marginBottom: "20px",
              }}
            >
              <section
                style={{
                  background: "#ffffff",
                  border: "1px solid #abefc6",
                  borderRadius: "16px",
                  padding: "22px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    color: "#15803d",
                    marginBottom: "14px",
                  }}
                >
                  <TrendingUp size={19} />
                  <h2
                    style={{
                      margin: 0,
                      fontSize: "17px",
                      fontWeight: 800,
                    }}
                  >
                    Strong Topics
                  </h2>
                </div>

                {result.strong_topics.length > 0 ? (
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "8px",
                    }}
                  >
                    {result.strong_topics.map((topic) => (
                      <span
                        key={topic}
                        style={{
                          padding: "8px 11px",
                          borderRadius: "999px",
                          background: "#f0fdf4",
                          color: "#15803d",
                          fontSize: "12px",
                          fontWeight: 700,
                        }}
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p
                    style={{
                      margin: 0,
                      color: "#667085",
                      fontSize: "13px",
                    }}
                  >
                    No topic has reached the strong threshold yet.
                  </p>
                )}
              </section>

              <section
                style={{
                  background: "#ffffff",
                  border: "1px solid #fecdca",
                  borderRadius: "16px",
                  padding: "22px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    color: "#d92d20",
                    marginBottom: "14px",
                  }}
                >
                  <TrendingDown size={19} />
                  <h2
                    style={{
                      margin: 0,
                      fontSize: "17px",
                      fontWeight: 800,
                    }}
                  >
                    Weak Topics
                  </h2>
                </div>

                {result.weak_topics.length > 0 ? (
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "8px",
                    }}
                  >
                    {result.weak_topics.map((topic) => (
                      <span
                        key={topic}
                        style={{
                          padding: "8px 11px",
                          borderRadius: "999px",
                          background: "#fef3f2",
                          color: "#b42318",
                          fontSize: "12px",
                          fontWeight: 700,
                        }}
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p
                    style={{
                      margin: 0,
                      color: "#667085",
                      fontSize: "13px",
                    }}
                  >
                    Excellent. No weak topics detected.
                  </p>
                )}
              </section>
            </div>

            {/* Recommendations */}
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "16px",
                padding: "22px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  marginBottom: "15px",
                }}
              >
                <Lightbulb size={19} />
                <h2
                  style={{
                    margin: 0,
                    fontSize: "18px",
                    fontWeight: 800,
                  }}
                >
                  Personalized Recommendations
                </h2>
              </div>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                }}
              >
                {result.recommendations.map((recommendation, index) => (
                  <div
                    key={`${recommendation}-${index}`}
                    style={{
                      display: "flex",
                      gap: "11px",
                      alignItems: "flex-start",
                      padding: "13px 14px",
                      borderRadius: "10px",
                      background: "#f8fafc",
                      border: "1px solid #eaecf0",
                    }}
                  >
                    <CheckCircle2
                      size={17}
                      style={{
                        marginTop: "1px",
                        flexShrink: 0,
                        color: "#175cd3",
                      }}
                    />

                    <span
                      style={{
                        color: "#344054",
                        fontSize: "13px",
                        lineHeight: 1.55,
                      }}
                    >
                      {recommendation}
                    </span>
                  </div>
                ))}
              </div>
            </section>

            {/* Result Actions */}
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: "11px",
                flexWrap: "wrap",
              }}
            >
              <button
                type="button"
                onClick={restartAssessment}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "12px 18px",
                  borderRadius: "10px",
                  border: "1px solid #d0d5dd",
                  background: "#ffffff",
                  color: "#344054",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                <RotateCcw size={17} />
                Try Another Assessment
              </button>

              <button
                type="button"
                onClick={() => navigate("/training")}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "12px 18px",
                  borderRadius: "10px",
                  border: "none",
                  background: "#175cd3",
                  color: "#ffffff",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                <BookOpen size={17} />
                Practice Weak Topics
              </button>

              <button
                type="button"
                onClick={() => navigate("/dashboard")}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "12px 18px",
                  borderRadius: "10px",
                  border: "1px solid #175cd3",
                  background: "#ffffff",
                  color: "#175cd3",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Dashboard
              </button>
            </div>
          </div>
        ) : assessment ? (
          /* ACTIVE ASSESSMENT */
          <div>
            {/* Assessment progress */}
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "16px",
                padding: "20px 22px",
                marginBottom: "18px",
                boxShadow: "0 2px 8px rgba(16, 24, 40, 0.04)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "15px",
                  flexWrap: "wrap",
                }}
              >
                <div>
                  <div
                    style={{
                      color: "#667085",
                      fontSize: "11px",
                      fontWeight: 800,
                      marginBottom: "5px",
                    }}
                  >
                    CURRENT ASSESSMENT
                  </div>

                  <h2
                    style={{
                      margin: 0,
                      fontSize: "21px",
                      fontWeight: 800,
                    }}
                  >
                    {assessment.skill}
                  </h2>
                </div>

                <div
                  style={{
                    padding: "9px 13px",
                    borderRadius: "10px",
                    background: "#eff8ff",
                    color: "#175cd3",
                    fontSize: "13px",
                    fontWeight: 800,
                  }}
                >
                  {answeredCount} / {assessment.total_questions} answered
                </div>
              </div>

              <div
                style={{
                  marginTop: "18px",
                  height: "9px",
                  borderRadius: "999px",
                  background: "#eaecf0",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${progressPercentage}%`,
                    height: "100%",
                    borderRadius: "999px",
                    background:
                      "linear-gradient(90deg, #175cd3, #2e90fa)",
                    transition: "width 0.3s ease",
                  }}
                />
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: "8px",
                  color: "#667085",
                  fontSize: "12px",
                }}
              >
                <span>
                  Question {currentQuestionIndex + 1} of{" "}
                  {assessment.total_questions}
                </span>

                <span>{progressPercentage}%</span>
              </div>
            </section>

            {/* Question */}
            {currentQuestion && (
              <section
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "16px",
                  padding: "28px",
                  boxShadow: "0 2px 8px rgba(16, 24, 40, 0.04)",
                }}
              >
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "7px",
                    padding: "7px 11px",
                    borderRadius: "999px",
                    background: "#f2f4f7",
                    color: "#475467",
                    fontSize: "11px",
                    fontWeight: 800,
                    marginBottom: "18px",
                  }}
                >
                  <Target size={14} />
                  {currentQuestion.topic}
                </div>

                <h2
                  style={{
                    margin: "0 0 25px",
                    fontSize: "22px",
                    lineHeight: 1.45,
                    fontWeight: 800,
                  }}
                >
                  {currentQuestion.question}
                </h2>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "11px",
                  }}
                >
                  {currentQuestion.options.map((option, index) => {
                    const selected =
                      answers[currentQuestion.id] === option;

                    return (
                      <button
                        key={option}
                        type="button"
                        onClick={() => handleSelectOption(option)}
                        style={{
                          width: "100%",
                          display: "flex",
                          alignItems: "center",
                          gap: "13px",
                          padding: "15px 16px",
                          textAlign: "left",
                          borderRadius: "11px",
                          border: selected
                            ? "2px solid #175cd3"
                            : "1px solid #d0d5dd",
                          background: selected ? "#eff8ff" : "#ffffff",
                          color: "#344054",
                          cursor: "pointer",
                          transition: "all 0.18s ease",
                        }}
                      >
                        <span
                          style={{
                            width: "32px",
                            height: "32px",
                            borderRadius: "9px",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                            background: selected
                              ? "#dbeafe"
                              : "#f2f4f7",
                            color: selected
                              ? "#175cd3"
                              : "#475467",
                            fontWeight: 800,
                            fontSize: "12px",
                          }}
                        >
                          {String.fromCharCode(65 + index)}
                        </span>

                        <span
                          style={{
                            flex: 1,
                            fontSize: "14px",
                            lineHeight: 1.5,
                            fontWeight: selected ? 700 : 500,
                          }}
                        >
                          {option}
                        </span>

                        {selected && (
                          <CheckCircle2
                            size={19}
                            style={{
                              color: "#175cd3",
                              flexShrink: 0,
                            }}
                          />
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Question navigation */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "12px",
                    marginTop: "28px",
                    paddingTop: "20px",
                    borderTop: "1px solid #eaecf0",
                    flexWrap: "wrap",
                  }}
                >
                  <button
                    type="button"
                    onClick={handlePrevious}
                    disabled={currentQuestionIndex === 0}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "7px",
                      padding: "10px 15px",
                      borderRadius: "9px",
                      border: "1px solid #d0d5dd",
                      background: "#ffffff",
                      color: "#344054",
                      fontWeight: 700,
                      cursor:
                        currentQuestionIndex === 0
                          ? "not-allowed"
                          : "pointer",
                      opacity: currentQuestionIndex === 0 ? 0.45 : 1,
                    }}
                  >
                    <ChevronLeft size={17} />
                    Previous
                  </button>

                  <div
                    style={{
                      color: "#667085",
                      fontSize: "12px",
                      fontWeight: 700,
                    }}
                  >
                    {currentQuestionIndex + 1} /{" "}
                    {assessment.total_questions}
                  </div>

                  {currentQuestionIndex ===
                  assessment.questions.length - 1 ? (
                    <button
                      type="button"
                      onClick={submitAssessment}
                      disabled={submitting || answeredCount === 0}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "11px 18px",
                        borderRadius: "9px",
                        border: "none",
                        background: "#175cd3",
                        color: "#ffffff",
                        fontWeight: 800,
                        cursor:
                          submitting || answeredCount === 0
                            ? "not-allowed"
                            : "pointer",
                        opacity:
                          submitting || answeredCount === 0 ? 0.55 : 1,
                      }}
                    >
                      {submitting ? (
                        <Loader2
                          size={17}
                          style={{
                            animation: "spin 1s linear infinite",
                          }}
                        />
                      ) : (
                        <Award size={17} />
                      )}
                      {submitting
                        ? "Evaluating..."
                        : "Submit Assessment"}
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={handleNext}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "7px",
                        padding: "10px 15px",
                        borderRadius: "9px",
                        border: "1px solid #175cd3",
                        background: "#175cd3",
                        color: "#ffffff",
                        fontWeight: 700,
                        cursor: "pointer",
                      }}
                    >
                      Next
                      <ChevronRight size={17} />
                    </button>
                  )}
                </div>
              </section>
            )}
          </div>
        ) : (
          /* START SCREEN */
          <div>
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "18px",
                padding: "30px",
                boxShadow: "0 4px 14px rgba(16, 24, 40, 0.05)",
              }}
            >
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "minmax(0, 1fr) 280px",
                  gap: "28px",
                  alignItems: "start",
                }}
              >
                <div>
                  <div
                    style={{
                      width: "52px",
                      height: "52px",
                      borderRadius: "14px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: "#eff8ff",
                      color: "#175cd3",
                      marginBottom: "17px",
                    }}
                  >
                    <Target size={26} />
                  </div>

                  <h2
                    style={{
                      margin: "0 0 9px",
                      fontSize: "23px",
                      fontWeight: 800,
                    }}
                  >
                    Test your placement skills
                  </h2>

                  <p
                    style={{
                      margin: "0 0 22px",
                      color: "#667085",
                      fontSize: "14px",
                      lineHeight: 1.65,
                      maxWidth: "680px",
                    }}
                  >
                    Select a skill and complete a placement-focused
                    assessment. Your answers will be evaluated automatically
                    and broken down by topic.
                  </p>

                  <label
                    style={{
                      display: "block",
                      marginBottom: "8px",
                      fontSize: "13px",
                      fontWeight: 800,
                      color: "#344054",
                    }}
                  >
                    Select Skill
                  </label>

                  <select
                    value={selectedSkill}
                    onChange={(event) =>
                      setSelectedSkill(event.target.value)
                    }
                    disabled={loadingSkills || starting}
                    style={{
                      width: "100%",
                      maxWidth: "520px",
                      padding: "12px 14px",
                      borderRadius: "10px",
                      border: "1px solid #d0d5dd",
                      background: "#ffffff",
                      color: "#344054",
                      fontSize: "14px",
                      fontWeight: 600,
                      outline: "none",
                    }}
                  >
                    {skills.map((skill) => (
                      <option key={skill} value={skill}>
                        {skill}
                      </option>
                    ))}
                  </select>

                  <button
                    type="button"
                    onClick={startAssessment}
                    disabled={starting || loadingSkills}
                    style={{
                      marginTop: "18px",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "9px",
                      padding: "12px 20px",
                      borderRadius: "10px",
                      border: "none",
                      background: "#175cd3",
                      color: "#ffffff",
                      fontSize: "14px",
                      fontWeight: 800,
                      cursor:
                        starting || loadingSkills
                          ? "not-allowed"
                          : "pointer",
                      opacity:
                        starting || loadingSkills ? 0.65 : 1,
                    }}
                  >
                    {starting ? (
                      <Loader2
                        size={18}
                        style={{
                          animation: "spin 1s linear infinite",
                        }}
                      />
                    ) : (
                      <Trophy size={18} />
                    )}
                    {starting ? "Starting..." : "Start Assessment"}
                  </button>
                </div>

                <div
                  style={{
                    padding: "20px",
                    borderRadius: "14px",
                    background: "#f8fafc",
                    border: "1px solid #eaecf0",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      marginBottom: "16px",
                    }}
                  >
                    <BookOpen size={18} />
                    <strong style={{ fontSize: "14px" }}>
                      Assessment Format
                    </strong>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "12px",
                    }}
                  >
                    <div>
                      <strong
                        style={{
                          display: "block",
                          fontSize: "13px",
                        }}
                      >
                        10 Questions
                      </strong>
                      <span
                        style={{
                          color: "#667085",
                          fontSize: "11px",
                        }}
                      >
                        Placement-focused MCQs
                      </span>
                    </div>

                    <div>
                      <strong
                        style={{
                          display: "block",
                          fontSize: "13px",
                        }}
                      >
                        Automatic Scoring
                      </strong>
                      <span
                        style={{
                          color: "#667085",
                          fontSize: "11px",
                        }}
                      >
                        Instant evaluation
                      </span>
                    </div>

                    <div>
                      <strong
                        style={{
                          display: "block",
                          fontSize: "13px",
                        }}
                      >
                        Topic Analysis
                      </strong>
                      <span
                        style={{
                          color: "#667085",
                          fontSize: "11px",
                        }}
                      >
                        Find your strengths and gaps
                      </span>
                    </div>

                    <div>
                      <strong
                        style={{
                          display: "block",
                          fontSize: "13px",
                        }}
                      >
                        Personalized Next Step
                      </strong>
                      <span
                        style={{
                          color: "#667085",
                          fontSize: "11px",
                        }}
                      >
                        Recommendations based on your score
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Assessment purpose */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(230px, 1fr))",
                gap: "15px",
                marginTop: "18px",
              }}
            >
              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "14px",
                  padding: "18px",
                }}
              >
                <Target size={20} />
                <h3
                  style={{
                    margin: "10px 0 5px",
                    fontSize: "15px",
                  }}
                >
                  Measure
                </h3>
                <p
                  style={{
                    margin: 0,
                    color: "#667085",
                    fontSize: "12px",
                    lineHeight: 1.5,
                  }}
                >
                  Measure your actual understanding instead of relying only
                  on your self-rated skill percentage.
                </p>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "14px",
                  padding: "18px",
                }}
              >
                <TrendingDown size={20} />
                <h3
                  style={{
                    margin: "10px 0 5px",
                    fontSize: "15px",
                  }}
                >
                  Identify Gaps
                </h3>
                <p
                  style={{
                    margin: 0,
                    color: "#667085",
                    fontSize: "12px",
                    lineHeight: 1.5,
                  }}
                >
                  Find the exact topics where additional preparation is
                  required.
                </p>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "14px",
                  padding: "18px",
                }}
              >
                <Lightbulb size={20} />
                <h3
                  style={{
                    margin: "10px 0 5px",
                    fontSize: "15px",
                  }}
                >
                  Improve
                </h3>
                <p
                  style={{
                    margin: 0,
                    color: "#667085",
                    fontSize: "12px",
                    lineHeight: 1.5,
                  }}
                >
                  Use the results to decide what you should study next.
                </p>
              </div>
            </div>
          </div>
        )}

        <style>
          {`
            @keyframes spin {
              from {
                transform: rotate(0deg);
              }
              to {
                transform: rotate(360deg);
              }
            }

            @media (max-width: 800px) {
              .assessment-start-grid {
                grid-template-columns: 1fr !important;
              }
            }
          `}
        </style>
      </div>
    </div>
  );
}
