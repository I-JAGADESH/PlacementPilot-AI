import { useEffect, useState } from "react";
import {
  ArrowLeft,
  BarChart3,
  Brain,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Target,
  Lightbulb,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

interface SkillAnalysisItem {
  name: string;
  proficiency: number;
  status: string;
  priority: string;
  evidence: string[];
  reason: string;
}

interface SkillGapItem {
  name: string;
  status: string;
  priority: string;
  evidence: string[];
  reason: string;
}

interface SkillIntelligenceResponse {
  overall_skill_score: number;
  strong_skills: SkillAnalysisItem[];
  weak_skills: SkillAnalysisItem[];
  missing_skills: SkillGapItem[];
  recommendations: string[];
  total_profile_skills: number;
  total_missing_skills: number;
}

function getPriorityStyle(priority: string) {
  const value = priority.toLowerCase();

  if (value === "high" || value === "critical") {
    return {
      background: "#fef3f2",
      color: "#b42318",
    };
  }

  if (value === "medium") {
    return {
      background: "#fffaeb",
      color: "#b54708",
    };
  }

  return {
    background: "#ecfdf3",
    color: "#027a48",
  };
}

function getProficiencyColor(value: number) {
  if (value >= 80) return "#12b76a";
  if (value >= 60) return "#f79009";
  return "#f04438";
}

function safeErrorMessage(error: any): string {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;

        if (item?.msg) {
          const location = Array.isArray(item?.loc)
            ? item.loc.join(" → ")
            : "";

          return location
            ? `${location}: ${item.msg}`
            : item.msg;
        }

        return JSON.stringify(item);
      })
      .join(", ");
  }

  if (detail && typeof detail === "object") {
    return detail.msg || JSON.stringify(detail);
  }

  return (
    error?.message ||
    "Unable to analyze skills. Please try again."
  );
}

export default function SkillIntelligence() {
  const navigate = useNavigate();

  const [data, setData] =
    useState<SkillIntelligenceResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const analyzeSkills = async () => {
    try {
      setError("");

      if (!data) {
        setLoading(true);
      } else {
        setAnalyzing(true);
      }

      const response =
        await api.post<SkillIntelligenceResponse>(
          "/api/v1/intelligence/skill-gap",
          {
            job_description:
              "Software Engineer responsible for designing, developing, testing, debugging, and maintaining software applications. Strong programming, data structures, algorithms, problem-solving, database, software engineering, cloud computing, and communication skills are expected.",
          }
        );

      setData(response.data);
    } catch (err: any) {
      console.error("Skill Intelligence Error:", err);
      setError(safeErrorMessage(err));
    } finally {
      setLoading(false);
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    analyzeSkills();
  }, []);

  const goBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate("/dashboard");
    }
  };

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#f8fafc",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "24px",
        }}
      >
        <div
          style={{
            background: "#ffffff",
            borderRadius: "18px",
            padding: "40px",
            textAlign: "center",
            boxShadow: "0 10px 30px rgba(16,24,40,0.08)",
            maxWidth: "420px",
            width: "100%",
          }}
        >
          <Brain
            size={44}
            style={{
              color: "#7f56d9",
              marginBottom: "16px",
            }}
          />

          <h2
            style={{
              margin: "0 0 8px",
              color: "#101828",
              fontSize: "22px",
            }}
          >
            Analyzing Your Skills
          </h2>

          <p
            style={{
              margin: 0,
              color: "#667085",
              fontSize: "14px",
            }}
          >
            Comparing your profile with Software Engineer
            requirements...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        padding: "28px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
        }}
      >
        {/* Back */}
        <button
          type="button"
          onClick={goBack}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "9px 14px",
            border: "1px solid #d0d5dd",
            borderRadius: "10px",
            background: "#ffffff",
            color: "#344054",
            fontSize: "13px",
            fontWeight: 700,
            cursor: "pointer",
            marginBottom: "22px",
          }}
        >
          <ArrowLeft size={16} />
          Back
        </button>

        {/* Header */}
        <div
          style={{
            background:
              "linear-gradient(135deg, #6941c6 0%, #7f56d9 55%, #9e77ed 100%)",
            borderRadius: "20px",
            padding: "30px",
            color: "#ffffff",
            marginBottom: "24px",
            boxShadow: "0 12px 32px rgba(105,65,198,0.18)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              gap: "20px",
              flexWrap: "wrap",
            }}
          >
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  marginBottom: "10px",
                }}
              >
                <BarChart3 size={30} />

                <h1
                  style={{
                    margin: 0,
                    fontSize: "28px",
                    fontWeight: 800,
                  }}
                >
                  Skill Intelligence
                </h1>
              </div>

              <p
                style={{
                  margin: 0,
                  maxWidth: "700px",
                  lineHeight: 1.6,
                  opacity: 0.92,
                }}
              >
                AI-powered analysis of your current skills,
                strengths, weaknesses, and missing skills for
                your target software engineering role.
              </p>
            </div>

            <button
              type="button"
              onClick={analyzeSkills}
              disabled={analyzing}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                border: "none",
                borderRadius: "10px",
                padding: "11px 16px",
                background: "#ffffff",
                color: "#6941c6",
                fontWeight: 800,
                cursor: analyzing
                  ? "not-allowed"
                  : "pointer",
                opacity: analyzing ? 0.7 : 1,
              }}
            >
              <RefreshCw
                size={16}
                style={{
                  animation: analyzing
                    ? "spin 1s linear infinite"
                    : "none",
                }}
              />

              {analyzing
                ? "Analyzing..."
                : "Re-analyze"}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              background: "#fef3f2",
              border: "1px solid #fecdca",
              borderRadius: "14px",
              padding: "16px",
              marginBottom: "24px",
              display: "flex",
              alignItems: "flex-start",
              gap: "12px",
            }}
          >
            <AlertTriangle
              size={20}
              style={{
                color: "#b42318",
                flexShrink: 0,
              }}
            />

            <div>
              <strong
                style={{
                  color: "#912018",
                  display: "block",
                  marginBottom: "4px",
                }}
              >
                Skill analysis failed
              </strong>

              <span
                style={{
                  color: "#b42318",
                  fontSize: "14px",
                }}
              >
                {error}
              </span>
            </div>
          </div>
        )}

        {data && (
          <>
            {/* Score + stats */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(210px, 1fr))",
                gap: "18px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "16px",
                  padding: "22px",
                  border: "1px solid #eaecf0",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    color: "#667085",
                    fontSize: "13px",
                    fontWeight: 700,
                    marginBottom: "12px",
                  }}
                >
                  <Target size={18} />
                  Overall Skill Score
                </div>

                <div
                  style={{
                    fontSize: "38px",
                    fontWeight: 800,
                    color: "#6941c6",
                  }}
                >
                  {Number(
                    data.overall_skill_score || 0
                  ).toFixed(1)}
                  %
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "16px",
                  padding: "22px",
                  border: "1px solid #eaecf0",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    fontWeight: 700,
                    marginBottom: "12px",
                  }}
                >
                  Profile Skills
                </div>

                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: 800,
                    color: "#101828",
                  }}
                >
                  {data.total_profile_skills}
                </div>

                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    marginTop: "4px",
                  }}
                >
                  skills analyzed
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  borderRadius: "16px",
                  padding: "22px",
                  border: "1px solid #eaecf0",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    fontWeight: 700,
                    marginBottom: "12px",
                  }}
                >
                  Missing Skills
                </div>

                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: 800,
                    color:
                      data.total_missing_skills > 0
                        ? "#d92d20"
                        : "#12b76a",
                  }}
                >
                  {data.total_missing_skills}
                </div>

                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    marginTop: "4px",
                  }}
                >
                  skills to develop
                </div>
              </div>
            </div>

            {/* Strong skills */}
            <section
              style={{
                background: "#ffffff",
                borderRadius: "18px",
                border: "1px solid #eaecf0",
                padding: "24px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "20px",
                }}
              >
                <CheckCircle2
                  size={22}
                  style={{ color: "#12b76a" }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "20px",
                  }}
                >
                  Strong Skills
                </h2>
              </div>

              {data.strong_skills.length === 0 ? (
                <p style={{ color: "#667085" }}>
                  No strong skills identified yet.
                </p>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(auto-fit, minmax(280px, 1fr))",
                    gap: "16px",
                  }}
                >
                  {data.strong_skills.map((skill) => (
                    <div
                      key={skill.name}
                      style={{
                        border: "1px solid #d1fadf",
                        background: "#f6fef9",
                        borderRadius: "14px",
                        padding: "18px",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          marginBottom: "10px",
                        }}
                      >
                        <strong
                          style={{
                            color: "#101828",
                            fontSize: "16px",
                          }}
                        >
                          {skill.name}
                        </strong>

                        <span
                          style={{
                            fontWeight: 800,
                            color: getProficiencyColor(
                              skill.proficiency
                            ),
                          }}
                        >
                          {skill.proficiency}%
                        </span>
                      </div>

                      <div
                        style={{
                          height: "8px",
                          background: "#e4e7ec",
                          borderRadius: "999px",
                          overflow: "hidden",
                          marginBottom: "12px",
                        }}
                      >
                        <div
                          style={{
                            height: "100%",
                            width: `${Math.min(
                              100,
                              Math.max(
                                0,
                                skill.proficiency
                              )
                            )}%`,
                            background:
                              getProficiencyColor(
                                skill.proficiency
                              ),
                            borderRadius: "999px",
                          }}
                        />
                      </div>

                      <p
                        style={{
                          margin: 0,
                          color: "#667085",
                          fontSize: "13px",
                          lineHeight: 1.5,
                        }}
                      >
                        {skill.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Weak skills */}
            <section
              style={{
                background: "#ffffff",
                borderRadius: "18px",
                border: "1px solid #eaecf0",
                padding: "24px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "20px",
                }}
              >
                <AlertTriangle
                  size={22}
                  style={{ color: "#f79009" }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "20px",
                  }}
                >
                  Weak Skills
                </h2>
              </div>

              {data.weak_skills.length === 0 ? (
                <p style={{ color: "#667085" }}>
                  No weak skills identified.
                </p>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "repeat(auto-fit, minmax(280px, 1fr))",
                    gap: "16px",
                  }}
                >
                  {data.weak_skills.map((skill) => (
                    <div
                      key={skill.name}
                      style={{
                        border: "1px solid #fedf89",
                        background: "#fffdf5",
                        borderRadius: "14px",
                        padding: "18px",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: "10px",
                          marginBottom: "10px",
                        }}
                      >
                        <strong
                          style={{
                            color: "#101828",
                            fontSize: "16px",
                          }}
                        >
                          {skill.name}
                        </strong>

                        <span
                          style={{
                            ...getPriorityStyle(
                              skill.priority
                            ),
                            padding: "5px 9px",
                            borderRadius: "999px",
                            fontSize: "11px",
                            fontWeight: 800,
                            textTransform: "uppercase",
                          }}
                        >
                          {skill.priority}
                        </span>
                      </div>

                      <div
                        style={{
                          fontSize: "24px",
                          fontWeight: 800,
                          color: getProficiencyColor(
                            skill.proficiency
                          ),
                          marginBottom: "8px",
                        }}
                      >
                        {skill.proficiency}%
                      </div>

                      <p
                        style={{
                          margin: 0,
                          color: "#667085",
                          fontSize: "13px",
                          lineHeight: 1.5,
                        }}
                      >
                        {skill.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Missing skills */}
            <section
              style={{
                background: "#ffffff",
                borderRadius: "18px",
                border: "1px solid #eaecf0",
                padding: "24px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "20px",
                }}
              >
                <XCircle
                  size={22}
                  style={{ color: "#f04438" }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "20px",
                  }}
                >
                  Missing Skills
                </h2>
              </div>

              {data.missing_skills.length === 0 ? (
                <div
                  style={{
                    background: "#ecfdf3",
                    border: "1px solid #abefc6",
                    borderRadius: "12px",
                    padding: "16px",
                    color: "#027a48",
                  }}
                >
                  Great! No major missing skills were detected
                  for the current target.
                </div>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gap: "14px",
                  }}
                >
                  {data.missing_skills.map((skill) => (
                    <div
                      key={skill.name}
                      style={{
                        border: "1px solid #fecdca",
                        background: "#fff8f7",
                        borderRadius: "14px",
                        padding: "18px",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: "12px",
                          flexWrap: "wrap",
                          marginBottom: "8px",
                        }}
                      >
                        <strong
                          style={{
                            fontSize: "16px",
                            color: "#101828",
                          }}
                        >
                          {skill.name}
                        </strong>

                        <span
                          style={{
                            ...getPriorityStyle(
                              skill.priority
                            ),
                            padding: "5px 9px",
                            borderRadius: "999px",
                            fontSize: "11px",
                            fontWeight: 800,
                            textTransform: "uppercase",
                          }}
                        >
                          {skill.priority}
                        </span>
                      </div>

                      <p
                        style={{
                          margin: 0,
                          color: "#667085",
                          fontSize: "13px",
                          lineHeight: 1.5,
                        }}
                      >
                        {skill.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Recommendations */}
            <section
              style={{
                background: "#ffffff",
                borderRadius: "18px",
                border: "1px solid #eaecf0",
                padding: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "20px",
                }}
              >
                <Lightbulb
                  size={22}
                  style={{ color: "#7f56d9" }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "20px",
                  }}
                >
                  AI Recommendations
                </h2>
              </div>

              {data.recommendations.length === 0 ? (
                <p style={{ color: "#667085" }}>
                  No recommendations available.
                </p>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gap: "12px",
                  }}
                >
                  {data.recommendations.map(
                    (recommendation, index) => (
                      <div
                        key={`${index}-${recommendation}`}
                        style={{
                          display: "flex",
                          gap: "12px",
                          alignItems: "flex-start",
                          background: "#f9f5ff",
                          border: "1px solid #e9d7fe",
                          borderRadius: "12px",
                          padding: "15px",
                        }}
                      >
                        <div
                          style={{
                            width: "26px",
                            height: "26px",
                            borderRadius: "50%",
                            background: "#7f56d9",
                            color: "#ffffff",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: "12px",
                            fontWeight: 800,
                            flexShrink: 0,
                          }}
                        >
                          {index + 1}
                        </div>

                        <span
                          style={{
                            color: "#344054",
                            fontSize: "14px",
                            lineHeight: 1.55,
                          }}
                        >
                          {recommendation}
                        </span>
                      </div>
                    )
                  )}
                </div>
              )}
            </section>
          </>
        )}
      </div>

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
        `}
      </style>
    </div>
  );
}