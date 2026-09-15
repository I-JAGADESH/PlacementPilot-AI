import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  BookOpen,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Lightbulb,
  Loader2,
  Map,
  Target,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";

import api from "../services/api";
import BackButton from "../components/BackButton";

interface RoadmapTask {
  skill: string;
  priority: string;
  duration_days: number;
  topics: string[];
  reason: string;
}

interface RoadmapResponse {
  target_role: string;
  overall_skill_score: number;
  total_days: number;
  tasks: RoadmapTask[];
  daily_plan: string[];
  recommendations: string[];
}

const DEFAULT_JOB_DESCRIPTION = `
Software Engineer responsible for designing, developing, testing, debugging,
and maintaining software applications.

Strong programming, data structures, algorithms, problem-solving, database,
software engineering, cloud computing, Git, GitHub, REST APIs and communication
skills are expected.

Experience with C++, Python, Java, SQL, React, backend development and
software engineering practices is preferred.
`.trim();

export default function Roadmap() {
  const navigate = useNavigate();

  const [jobDescription, setJobDescription] = useState(
    DEFAULT_JOB_DESCRIPTION
  );

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateRoadmap = async () => {
    if (jobDescription.trim().length < 10) {
      setError("Please provide a valid job description.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await api.post<RoadmapResponse>(
        "/api/v1/roadmap/generate",
        {
          job_description: jobDescription.trim(),
        }
      );

      setRoadmap(response.data);
    } catch (err: any) {
      console.error("Roadmap generation error:", err);

      const detail = err?.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(
          detail
            .map((item: any) => item?.msg || "Invalid request")
            .join(", ")
        );
      } else {
        setError(
          "Unable to generate the roadmap. Please make sure the backend is running."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const getPriorityStyle = (priority: string) => {
    const value = priority.toLowerCase();

    if (value.includes("high")) {
      return {
        background: "#fef3f2",
        color: "#b42318",
        border: "1px solid #fecdca",
      };
    }

    if (value.includes("medium")) {
      return {
        background: "#fffaeb",
        color: "#b54708",
        border: "1px solid #fedf89",
      };
    }

    return {
      background: "#ecfdf3",
      color: "#027a48",
      border: "1px solid #abefc6",
    };
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "28px",
        color: "#101828",
      }}
    >
      <div
        style={{
          maxWidth: "1250px",
          margin: "0 auto",
        }}
      >
        <BackButton />

        {/* Header */}
        <div
          style={{
            background: "linear-gradient(135deg, #155eef, #2e90fa)",
            borderRadius: "20px",
            padding: "30px",
            color: "#ffffff",
            marginBottom: "24px",
            boxShadow: "0 10px 30px rgba(21, 94, 239, 0.18)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "14px",
              marginBottom: "10px",
            }}
          >
            <Map size={30} />

            <h1
              style={{
                margin: 0,
                fontSize: "28px",
                fontWeight: 800,
              }}
            >
              Personalized Preparation Roadmap
            </h1>
          </div>

          <p
            style={{
              margin: 0,
              maxWidth: "850px",
              lineHeight: 1.6,
              fontSize: "15px",
              opacity: 0.95,
            }}
          >
            Turn your current skills and target job requirements into a
            structured placement preparation plan.
          </p>
        </div>

        {/* Job Description */}
        <section
          style={{
            background: "#ffffff",
            border: "1px solid #eaecf0",
            borderRadius: "18px",
            padding: "24px",
            marginBottom: "24px",
            boxShadow: "0 2px 8px rgba(16, 24, 40, 0.04)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "8px",
            }}
          >
            <Target size={21} color="#155eef" />

            <h2
              style={{
                margin: 0,
                fontSize: "19px",
                fontWeight: 750,
              }}
            >
              Target Job Description
            </h2>
          </div>

          <p
            style={{
              margin: "0 0 16px",
              color: "#667085",
              fontSize: "13px",
            }}
          >
            The AI uses this job description to identify what you should
            prioritize.
          </p>

          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste your target job description here..."
            rows={8}
            style={{
              width: "100%",
              boxSizing: "border-box",
              resize: "vertical",
              border: "1px solid #d0d5dd",
              borderRadius: "12px",
              padding: "14px",
              fontSize: "14px",
              lineHeight: 1.6,
              outline: "none",
              fontFamily: "inherit",
              color: "#101828",
            }}
          />

          {error && (
            <div
              style={{
                marginTop: "14px",
                padding: "12px 14px",
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
              <AlertTriangle size={17} />
              {error}
            </div>
          )}

          <button
            type="button"
            onClick={generateRoadmap}
            disabled={loading}
            style={{
              marginTop: "18px",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "9px",
              padding: "12px 20px",
              border: "none",
              borderRadius: "10px",
              background: loading ? "#98a2b3" : "#155eef",
              color: "#ffffff",
              fontSize: "14px",
              fontWeight: 750,
              cursor: loading ? "not-allowed" : "pointer",
              boxShadow: loading
                ? "none"
                : "0 5px 12px rgba(21, 94, 239, 0.2)",
            }}
          >
            {loading ? (
              <>
                <Loader2 size={17} className="roadmap-spin" />
                Generating Roadmap...
              </>
            ) : (
              <>
                <Map size={17} />
                Generate My Roadmap
              </>
            )}
          </button>
        </section>

        {/* Empty State */}
        {!roadmap && !loading && (
          <section
            style={{
              background: "#ffffff",
              border: "1px solid #eaecf0",
              borderRadius: "18px",
              padding: "55px 25px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                width: "64px",
                height: "64px",
                borderRadius: "50%",
                background: "#eff4ff",
                color: "#155eef",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 16px",
              }}
            >
              <Map size={30} />
            </div>

            <h2
              style={{
                margin: "0 0 8px",
                fontSize: "21px",
              }}
            >
              Your personalized roadmap is waiting
            </h2>

            <p
              style={{
                margin: 0,
                color: "#667085",
                fontSize: "14px",
              }}
            >
              Generate your roadmap to see exactly what you should focus on
              next.
            </p>
          </section>
        )}

        {/* Roadmap Result */}
        {roadmap && (
          <>
            {/* Overview Cards */}
            <section
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(220px, 1fr))",
                gap: "16px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "16px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    color: "#155eef",
                    marginBottom: "12px",
                  }}
                >
                  <Target size={19} />
                  <span
                    style={{
                      fontSize: "13px",
                      fontWeight: 700,
                    }}
                  >
                    Target Role
                  </span>
                </div>

                <div
                  style={{
                    fontSize: "20px",
                    fontWeight: 800,
                  }}
                >
                  {roadmap.target_role}
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "16px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    color: "#12b76a",
                    marginBottom: "12px",
                  }}
                >
                  <TrendingUp size={19} />
                  <span
                    style={{
                      fontSize: "13px",
                      fontWeight: 700,
                    }}
                  >
                    Current Skill Score
                  </span>
                </div>

                <div
                  style={{
                    fontSize: "30px",
                    fontWeight: 850,
                    color: "#12b76a",
                  }}
                >
                  {Number(roadmap.overall_skill_score).toFixed(1)}%
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "16px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    color: "#7f56d9",
                    marginBottom: "12px",
                  }}
                >
                  <CalendarDays size={19} />
                  <span
                    style={{
                      fontSize: "13px",
                      fontWeight: 700,
                    }}
                  >
                    Roadmap Duration
                  </span>
                </div>

                <div
                  style={{
                    fontSize: "30px",
                    fontWeight: 850,
                    color: "#7f56d9",
                  }}
                >
                  {roadmap.total_days}
                  <span
                    style={{
                      fontSize: "14px",
                      fontWeight: 600,
                      marginLeft: "5px",
                    }}
                  >
                    days
                  </span>
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "16px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    color: "#f79009",
                    marginBottom: "12px",
                  }}
                >
                  <BookOpen size={19} />
                  <span
                    style={{
                      fontSize: "13px",
                      fontWeight: 700,
                    }}
                  >
                    Focus Areas
                  </span>
                </div>

                <div
                  style={{
                    fontSize: "30px",
                    fontWeight: 850,
                    color: "#f79009",
                  }}
                >
                  {roadmap.tasks.length}
                </div>
              </div>
            </section>

            {/* Tasks */}
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "18px",
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
                <Map size={21} color="#155eef" />

                <h2
                  style={{
                    margin: 0,
                    fontSize: "20px",
                  }}
                >
                  Your Learning Roadmap
                </h2>
              </div>

              {roadmap.tasks.length === 0 ? (
                <div
                  style={{
                    padding: "20px",
                    background: "#ecfdf3",
                    borderRadius: "12px",
                    color: "#027a48",
                    textAlign: "center",
                    fontWeight: 650,
                  }}
                >
                  No additional learning tasks were generated.
                </div>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "16px",
                  }}
                >
                  {roadmap.tasks.map((task, index) => (
                    <div
                      key={`${task.skill}-${index}`}
                      style={{
                        border: "1px solid #eaecf0",
                        borderRadius: "15px",
                        padding: "20px",
                        background: "#fcfcfd",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "flex-start",
                          gap: "15px",
                          flexWrap: "wrap",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            gap: "14px",
                            alignItems: "flex-start",
                          }}
                        >
                          <div
                            style={{
                              minWidth: "38px",
                              width: "38px",
                              height: "38px",
                              borderRadius: "10px",
                              background: "#eff4ff",
                              color: "#155eef",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              fontWeight: 800,
                            }}
                          >
                            {index + 1}
                          </div>

                          <div>
                            <h3
                              style={{
                                margin: "0 0 6px",
                                fontSize: "18px",
                              }}
                            >
                              {task.skill}
                            </h3>

                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "6px",
                                color: "#667085",
                                fontSize: "13px",
                              }}
                            >
                              <Clock3 size={15} />
                              {task.duration_days} day
                              {task.duration_days === 1 ? "" : "s"}
                            </div>
                          </div>
                        </div>

                        <span
                          style={{
                            ...getPriorityStyle(task.priority),
                            padding: "6px 11px",
                            borderRadius: "999px",
                            fontSize: "12px",
                            fontWeight: 750,
                            whiteSpace: "nowrap",
                          }}
                        >
                          {task.priority}
                        </span>
                      </div>

                      <div
                        style={{
                          marginTop: "18px",
                          padding: "14px",
                          background: "#ffffff",
                          borderRadius: "10px",
                          border: "1px solid #eaecf0",
                        }}
                      >
                        <div
                          style={{
                            fontSize: "12px",
                            color: "#667085",
                            fontWeight: 700,
                            marginBottom: "6px",
                          }}
                        >
                          WHY THIS MATTERS
                        </div>

                        <div
                          style={{
                            fontSize: "14px",
                            lineHeight: 1.6,
                            color: "#344054",
                          }}
                        >
                          {task.reason}
                        </div>
                      </div>

                      {task.topics.length > 0 && (
                        <div style={{ marginTop: "16px" }}>
                          <div
                            style={{
                              fontSize: "12px",
                              color: "#667085",
                              fontWeight: 700,
                              marginBottom: "9px",
                            }}
                          >
                            TOPICS TO COVER
                          </div>

                          <div
                            style={{
                              display: "flex",
                              flexWrap: "wrap",
                              gap: "8px",
                            }}
                          >
                            {task.topics.map((topic, topicIndex) => (
                              <span
                                key={`${topic}-${topicIndex}`}
                                style={{
                                  padding: "7px 10px",
                                  borderRadius: "8px",
                                  background: "#f2f4f7",
                                  color: "#344054",
                                  fontSize: "12px",
                                  fontWeight: 650,
                                }}
                              >
                                {topic}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Daily Plan */}
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "18px",
                padding: "24px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "18px",
                }}
              >
                <CalendarDays size={21} color="#7f56d9" />

                <h2
                  style={{
                    margin: 0,
                    fontSize: "20px",
                  }}
                >
                  Daily Preparation Plan
                </h2>
              </div>

              {roadmap.daily_plan.length === 0 ? (
                <p
                  style={{
                    color: "#667085",
                    margin: 0,
                  }}
                >
                  No daily plan was generated.
                </p>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px",
                  }}
                >
                  {roadmap.daily_plan.map((plan, index) => (
                    <div
                      key={index}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "12px",
                        padding: "13px 15px",
                        background: "#f9f5ff",
                        borderRadius: "10px",
                      }}
                    >
                      <CheckCircle2
                        size={18}
                        color="#7f56d9"
                        style={{
                          marginTop: "1px",
                          flexShrink: 0,
                        }}
                      />

                      <div
                        style={{
                          fontSize: "14px",
                          lineHeight: 1.55,
                          color: "#344054",
                        }}
                      >
                        <strong>Day {index + 1}:</strong> {plan}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Recommendations */}
            <section
              style={{
                background: "#ffffff",
                border: "1px solid #eaecf0",
                borderRadius: "18px",
                padding: "24px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginBottom: "18px",
                }}
              >
                <Lightbulb size={21} color="#f79009" />

                <h2
                  style={{
                    margin: 0,
                    fontSize: "20px",
                  }}
                >
                  AI Recommendations
                </h2>
              </div>

              {roadmap.recommendations.length === 0 ? (
                <p
                  style={{
                    color: "#667085",
                    margin: 0,
                  }}
                >
                  No additional recommendations.
                </p>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px",
                  }}
                >
                  {roadmap.recommendations.map((recommendation, index) => (
                    <div
                      key={index}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "11px",
                        padding: "13px 15px",
                        background: "#fffaeb",
                        borderRadius: "10px",
                      }}
                    >
                      <Lightbulb
                        size={17}
                        color="#f79009"
                        style={{
                          marginTop: "2px",
                          flexShrink: 0,
                        }}
                      />

                      <span
                        style={{
                          fontSize: "14px",
                          lineHeight: 1.55,
                          color: "#344054",
                        }}
                      >
                        {recommendation}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </section>

            {/* Next Actions */}
            <section
              style={{
                background: "linear-gradient(135deg, #eff4ff, #f5f3ff)",
                border: "1px solid #dbe5ff",
                borderRadius: "18px",
                padding: "24px",
              }}
            >
              <h2
                style={{
                  margin: "0 0 8px",
                  fontSize: "20px",
                }}
              >
                Continue Your Placement Journey 🚀
              </h2>

              <p
                style={{
                  margin: "0 0 18px",
                  color: "#667085",
                  fontSize: "14px",
                }}
              >
                Use the roadmap to identify what to improve, then validate
                your progress through skill analysis and AI interviews.
              </p>

              <div
                style={{
                  display: "flex",
                  gap: "10px",
                  flexWrap: "wrap",
                }}
              >
                <button
                  type="button"
                  onClick={() => navigate("/skill-intelligence")}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "11px 16px",
                    border: "none",
                    borderRadius: "10px",
                    background: "#155eef",
                    color: "#ffffff",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  <TrendingUp size={17} />
                  Skill Intelligence
                </button>

                <button
                  type="button"
                  onClick={() => navigate("/interview")}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "11px 16px",
                    border: "1px solid #d0d5dd",
                    borderRadius: "10px",
                    background: "#ffffff",
                    color: "#344054",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  <BookOpen size={17} />
                  Practice AI Interview
                </button>

                <button
                  type="button"
                  onClick={() => navigate("/ats")}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "11px 16px",
                    border: "1px solid #d0d5dd",
                    borderRadius: "10px",
                    background: "#ffffff",
                    color: "#344054",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  <ArrowLeft
                    size={17}
                    style={{
                      transform: "rotate(180deg)",
                    }}
                  />
                  Improve Resume
                </button>
              </div>
            </section>
          </>
        )}
      </div>

      <style>
        {`
          @keyframes roadmap-spin {
            from {
              transform: rotate(0deg);
            }
            to {
              transform: rotate(360deg);
            }
          }

          .roadmap-spin {
            animation: roadmap-spin 1s linear infinite;
          }

          @media (max-width: 700px) {
            body {
              overflow-x: hidden;
            }
          }
        `}
      </style>
    </div>
  );
}