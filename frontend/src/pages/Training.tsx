import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Circle,
  Clock3,
  Code2,
  ExternalLink,
  Lightbulb,
  Loader2,
  PlayCircle,
  Target,
  Trophy,
} from "lucide-react";

import api from "../services/api";
import BackButton from "../components/BackButton";

import "../App.css";

interface TrainingTopic {
  skill: string;
  topic: string;
  explanation: string;
  key_points: string[];
  practice_questions: string[];
}

interface TrainingResponse {
  skill: string;
  total_topics: number;
  completed_topics: number;
  progress_percentage: number;
  topics: TrainingTopic[];
}

interface TopicCompletionResponse {
  skill: string;
  topic: string;
  completed: boolean;
  progress_percentage: number;
  completed_topics: number;
  total_topics: number;
}

const TRAINING_SKILLS = [
  {
    name: "Algorithms",
    icon: "algorithm",
    description: "Searching, sorting, greedy strategies and dynamic programming.",
  },
  {
    name: "Data Structures",
    icon: "code",
    description: "Core structures used in technical interviews and problem solving.",
  },
  {
    name: "Python",
    icon: "python",
    description: "Programming fundamentals, OOP, exceptions and interview practice.",
  },
  {
    name: "Java",
    icon: "java",
    description: "Exception handling, multithreading and interview preparation.",
  },
  {
    name: "C++",
    icon: "cpp",
    description: "Pointers, references, problem solving and interview practice.",
  },
  {
    name: "SQL",
    icon: "sql",
    description: "Joins, aggregation, subqueries and database optimization.",
  },
  {
    name: "React",
    icon: "react",
    description: "Hooks, forms, API integration and practical React development.",
  },
  {
    name: "Git",
    icon: "git",
    description: "Version control, branches, merging and collaboration workflows.",
  },
  {
    name: "GitHub",
    icon: "github",
    description: "Repositories, documentation, issues, pull requests and Actions.",
  },
  {
    name: "REST API",
    icon: "api",
    description: "HTTP methods, REST principles, responses and authentication.",
  },
];

function getSkillIcon(icon: string) {
  switch (icon) {
    case "algorithm":
      return <Target size={21} />;
    case "python":
      return <Code2 size={21} />;
    case "java":
      return <Code2 size={21} />;
    case "cpp":
      return <Code2 size={21} />;
    case "sql":
      return <BookOpen size={21} />;
    case "react":
      return <Code2 size={21} />;
    case "git":
      return <Code2 size={21} />;
    case "github":
      return <Code2 size={21} />;
    case "api":
      return <ExternalLink size={21} />;
    default:
      return <BookOpen size={21} />;
  }
}

export default function Training() {
  const navigate = useNavigate();

  const [selectedSkill, setSelectedSkill] = useState("Algorithms");
  const [training, setTraining] = useState<TrainingResponse | null>(null);

  const [currentTopicIndex, setCurrentTopicIndex] = useState(0);
  const [completedTopicNames, setCompletedTopicNames] = useState<string[]>([]);

  const [loading, setLoading] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [error, setError] = useState("");

  const currentTopic = useMemo(() => {
    if (!training || training.topics.length === 0) {
      return null;
    }

    return training.topics[currentTopicIndex];
  }, [training, currentTopicIndex]);

  const loadTraining = async (skill: string) => {
    try {
      setLoading(true);
      setError("");
      setCurrentTopicIndex(0);

      const response = await api.get<TrainingResponse>(
        `/api/v1/training/${encodeURIComponent(skill)}`
      );

      setTraining(response.data);

      // The backend currently returns the number of completed topics.
      // Reconstruct the completed topic names in the same order as the
      // training path so the button state is tracked per topic.
      setCompletedTopicNames(
        response.data.topics
          .slice(0, response.data.completed_topics)
          .map((topic) => topic.topic)
      );
    } catch (err: any) {
      console.error("Training load error:", err);

      const message =
        err?.response?.data?.detail ||
        "Unable to load training content. Please try again.";

      setError(message);
      setTraining(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTraining(selectedSkill);
  }, [selectedSkill]);

  const handleComplete = async () => {
    if (!training || !currentTopic || completing) {
      return;
    }

    try {
      setCompleting(true);
      setError("");

      const response = await api.post<TopicCompletionResponse>(
        "/api/v1/training/complete",
        {
          skill: training.skill,
          topic: currentTopic.topic,
          completed: true,
        }
      );

      setTraining((previous) => {
        if (!previous) {
          return previous;
        }

        return {
          ...previous,
          completed_topics: response.data.completed_topics,
          progress_percentage: response.data.progress_percentage,
        };
      });

      setCompletedTopicNames((previous) => {
        if (previous.includes(currentTopic.topic)) {
          return previous;
        }

        return [...previous, currentTopic.topic];
      });
    } catch (err: any) {
      console.error("Training completion error:", err);

      const message =
        err?.response?.data?.detail ||
        "Unable to save your progress. Please try again.";

      setError(message);
    } finally {
      setCompleting(false);
    }
  };

  const handlePrevious = () => {
    setCurrentTopicIndex((previous) => Math.max(previous - 1, 0));
  };

  const handleNext = () => {
    if (!training) {
      return;
    }

    setCurrentTopicIndex((previous) =>
      Math.min(previous + 1, training.topics.length - 1)
    );
  };

  const isCurrentTopicCompleted =
    !!currentTopic && completedTopicNames.includes(currentTopic.topic);

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
          maxWidth: "1400px",
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
            marginBottom: "28px",
            flexWrap: "wrap",
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
              <BookOpen size={15} />
              AI-POWERED TRAINING
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
              Personalized Training
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
              Learn the skills identified by your Skill Intelligence and
              Preparation Roadmap. Complete each topic to build measurable
              preparation progress.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate("/roadmap")}
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
            <Target size={17} />
            View Roadmap
          </button>
        </div>

        {/* Main layout */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "300px minmax(0, 1fr)",
            gap: "24px",
            alignItems: "start",
          }}
        >
          {/* Skill selector */}
          <aside
            style={{
              background: "#ffffff",
              border: "1px solid #eaecf0",
              borderRadius: "16px",
              padding: "18px",
              boxShadow: "0 2px 8px rgba(16, 24, 40, 0.04)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "9px",
                marginBottom: "15px",
              }}
            >
              <Target size={18} color="#175cd3" />
              <h2
                style={{
                  margin: 0,
                  fontSize: "16px",
                  fontWeight: 800,
                }}
              >
                Training Skills
              </h2>
            </div>

            <p
              style={{
                margin: "0 0 16px",
                color: "#667085",
                fontSize: "12px",
                lineHeight: 1.5,
              }}
            >
              Select a skill to begin your personalized learning path.
            </p>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              {TRAINING_SKILLS.map((skill) => {
                const active = selectedSkill === skill.name;

                return (
                  <button
                    key={skill.name}
                    type="button"
                    onClick={() => setSelectedSkill(skill.name)}
                    style={{
                      width: "100%",
                      textAlign: "left",
                      display: "flex",
                      alignItems: "center",
                      gap: "11px",
                      padding: "11px 12px",
                      borderRadius: "11px",
                      border: active
                        ? "1px solid #b2ddff"
                        : "1px solid transparent",
                      background: active ? "#eff8ff" : "#ffffff",
                      color: active ? "#175cd3" : "#344054",
                      cursor: "pointer",
                      transition: "all 0.18s ease",
                    }}
                  >
                    <span
                      style={{
                        width: "34px",
                        height: "34px",
                        borderRadius: "9px",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        background: active ? "#dbeafe" : "#f2f4f7",
                        flexShrink: 0,
                      }}
                    >
                      {getSkillIcon(skill.icon)}
                    </span>

                    <span
                      style={{
                        minWidth: 0,
                        flex: 1,
                      }}
                    >
                      <span
                        style={{
                          display: "block",
                          fontSize: "13px",
                          fontWeight: 800,
                        }}
                      >
                        {skill.name}
                      </span>

                      <span
                        style={{
                          display: "block",
                          marginTop: "3px",
                          color: active ? "#475467" : "#98a2b3",
                          fontSize: "10px",
                          lineHeight: 1.35,
                        }}
                      >
                        {skill.description}
                      </span>
                    </span>
                  </button>
                );
              })}
            </div>
          </aside>

          {/* Training content */}
          <main>
            {loading ? (
              <div
                style={{
                  minHeight: "480px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexDirection: "column",
                  gap: "12px",
                  background: "#ffffff",
                  border: "1px solid #eaecf0",
                  borderRadius: "16px",
                }}
              >
                <Loader2
                  size={30}
                  style={{
                    animation: "spin 1s linear infinite",
                  }}
                />

                <span
                  style={{
                    color: "#667085",
                    fontSize: "14px",
                  }}
                >
                  Loading your training path...
                </span>
              </div>
            ) : error && !training ? (
              <div
                style={{
                  background: "#ffffff",
                  border: "1px solid #fecdca",
                  borderRadius: "16px",
                  padding: "32px",
                  textAlign: "center",
                }}
              >
                <div
                  style={{
                    width: "52px",
                    height: "52px",
                    margin: "0 auto 14px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "#fef3f2",
                    color: "#d92d20",
                  }}
                >
                  <Circle size={25} />
                </div>

                <h2
                  style={{
                    margin: "0 0 8px",
                    fontSize: "18px",
                  }}
                >
                  Training unavailable
                </h2>

                <p
                  style={{
                    margin: "0 0 20px",
                    color: "#667085",
                    fontSize: "14px",
                  }}
                >
                  {error}
                </p>

                <button
                  type="button"
                  onClick={() => loadTraining(selectedSkill)}
                  style={{
                    padding: "10px 16px",
                    border: "none",
                    borderRadius: "9px",
                    background: "#175cd3",
                    color: "#ffffff",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  Try Again
                </button>
              </div>
            ) : training ? (
              <>
                {/* Progress header */}
                <section
                  style={{
                    background: "#ffffff",
                    border: "1px solid #eaecf0",
                    borderRadius: "16px",
                    padding: "22px",
                    marginBottom: "18px",
                    boxShadow: "0 2px 8px rgba(16, 24, 40, 0.04)",
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
                          color: "#667085",
                          fontSize: "12px",
                          fontWeight: 700,
                          marginBottom: "5px",
                        }}
                      >
                        CURRENT TRAINING PATH
                      </div>

                      <h2
                        style={{
                          margin: 0,
                          fontSize: "24px",
                          fontWeight: 800,
                        }}
                      >
                        {training.skill}
                      </h2>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "9px",
                        padding: "10px 13px",
                        borderRadius: "10px",
                        background: "#f0fdf4",
                        color: "#15803d",
                        fontSize: "13px",
                        fontWeight: 800,
                      }}
                    >
                      <Trophy size={17} />
                      {training.progress_percentage}% Complete
                    </div>
                  </div>

                  <div
                    style={{
                      marginTop: "20px",
                      height: "10px",
                      borderRadius: "999px",
                      background: "#eaecf0",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${Math.min(
                          Math.max(training.progress_percentage, 0),
                          100
                        )}%`,
                        height: "100%",
                        borderRadius: "999px",
                        background:
                          "linear-gradient(90deg, #175cd3, #2e90fa)",
                        transition: "width 0.35s ease",
                      }}
                    />
                  </div>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginTop: "9px",
                      color: "#667085",
                      fontSize: "12px",
                    }}
                  >
                    <span>
                      {training.completed_topics} of{" "}
                      {training.total_topics} topics completed
                    </span>

                    <span>
                      {Math.max(
                        training.total_topics - training.completed_topics,
                        0
                      )}{" "}
                      remaining
                    </span>
                  </div>
                </section>

                {error && (
                  <div
                    style={{
                      marginBottom: "18px",
                      padding: "11px 14px",
                      borderRadius: "10px",
                      background: "#fef3f2",
                      border: "1px solid #fecdca",
                      color: "#b42318",
                      fontSize: "13px",
                    }}
                  >
                    {error}
                  </div>
                )}

                {currentTopic ? (
                  <>
                    {/* Topic navigation */}
                    <section
                      style={{
                        background: "#ffffff",
                        border: "1px solid #eaecf0",
                        borderRadius: "16px",
                        padding: "22px",
                        boxShadow: "0 2px 8px rgba(16, 24, 40, 0.04)",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: "12px",
                          marginBottom: "20px",
                        }}
                      >
                        <div
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "7px",
                            color: "#667085",
                            fontSize: "12px",
                            fontWeight: 700,
                          }}
                        >
                          <BookOpen size={15} />
                          TOPIC {currentTopicIndex + 1} OF{" "}
                          {training.total_topics}
                        </div>

                        <div
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            color: "#667085",
                            fontSize: "12px",
                          }}
                        >
                          <Clock3 size={14} />
                          Focused learning
                        </div>
                      </div>

                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "12px",
                          marginBottom: "10px",
                        }}
                      >
                        <div
                          style={{
                            width: "42px",
                            height: "42px",
                            borderRadius: "11px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "#eff8ff",
                            color: "#175cd3",
                            flexShrink: 0,
                          }}
                        >
                          <PlayCircle size={22} />
                        </div>

                        <h2
                          style={{
                            margin: 0,
                            fontSize: "25px",
                            fontWeight: 800,
                          }}
                        >
                          {currentTopic.topic}
                        </h2>
                      </div>

                      <p
                        style={{
                          margin: "0 0 25px",
                          color: "#475467",
                          fontSize: "15px",
                          lineHeight: 1.75,
                        }}
                      >
                        {currentTopic.explanation}
                      </p>

                      {/* Key points */}
                      <div
                        style={{
                          marginBottom: "25px",
                          padding: "18px",
                          borderRadius: "13px",
                          background: "#f8fafc",
                          border: "1px solid #eaecf0",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                            marginBottom: "13px",
                            fontSize: "14px",
                            fontWeight: 800,
                          }}
                        >
                          <Lightbulb size={17} />
                          Key Points
                        </div>

                        <ul
                          style={{
                            margin: 0,
                            paddingLeft: "21px",
                            color: "#475467",
                            fontSize: "13px",
                            lineHeight: 1.75,
                          }}
                        >
                          {currentTopic.key_points.map((point, index) => (
                            <li key={`${point}-${index}`}>{point}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Practice questions */}
                      <div>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                            marginBottom: "13px",
                            fontSize: "14px",
                            fontWeight: 800,
                          }}
                        >
                          <Code2 size={17} />
                          Practice Questions
                        </div>

                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "9px",
                          }}
                        >
                          {currentTopic.practice_questions.map(
                            (question, index) => (
                              <div
                                key={`${question}-${index}`}
                                style={{
                                  display: "flex",
                                  gap: "11px",
                                  alignItems: "flex-start",
                                  padding: "13px 14px",
                                  borderRadius: "10px",
                                  border: "1px solid #eaecf0",
                                  background: "#ffffff",
                                }}
                              >
                                <span
                                  style={{
                                    width: "24px",
                                    height: "24px",
                                    borderRadius: "7px",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    background: "#f2f4f7",
                                    color: "#475467",
                                    fontSize: "11px",
                                    fontWeight: 800,
                                    flexShrink: 0,
                                  }}
                                >
                                  {index + 1}
                                </span>

                                <span
                                  style={{
                                    color: "#344054",
                                    fontSize: "13px",
                                    lineHeight: 1.55,
                                  }}
                                >
                                  {question}
                                </span>
                              </div>
                            )
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: "12px",
                          marginTop: "26px",
                          paddingTop: "20px",
                          borderTop: "1px solid #eaecf0",
                          flexWrap: "wrap",
                        }}
                      >
                        <button
                          type="button"
                          onClick={handlePrevious}
                          disabled={currentTopicIndex === 0}
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "7px",
                            padding: "10px 14px",
                            borderRadius: "9px",
                            border: "1px solid #d0d5dd",
                            background: "#ffffff",
                            color: "#344054",
                            fontWeight: 700,
                            cursor:
                              currentTopicIndex === 0
                                ? "not-allowed"
                                : "pointer",
                            opacity: currentTopicIndex === 0 ? 0.45 : 1,
                          }}
                        >
                          <ChevronLeft size={17} />
                          Previous
                        </button>

                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "9px",
                          }}
                        >
                          <button
                            type="button"
                            onClick={handleComplete}
                            disabled={completing || isCurrentTopicCompleted}
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "8px",
                              padding: "11px 17px",
                              borderRadius: "9px",
                              border: "none",
                              background: isCurrentTopicCompleted
                                ? "#dcfce7"
                                : "#175cd3",
                              color: isCurrentTopicCompleted
                                ? "#15803d"
                                : "#ffffff",
                              fontWeight: 800,
                              cursor:
                                completing || isCurrentTopicCompleted
                                  ? "not-allowed"
                                  : "pointer",
                              opacity: completing ? 0.7 : 1,
                            }}
                          >
                            {completing ? (
                              <Loader2
                                size={17}
                                style={{
                                  animation: "spin 1s linear infinite",
                                }}
                              />
                            ) : (
                              <CheckCircle2 size={17} />
                            )}

                            {isCurrentTopicCompleted
                              ? "Completed"
                              : "Mark Complete"}
                          </button>

                          <button
                            type="button"
                            onClick={handleNext}
                            disabled={
                              currentTopicIndex === training.topics.length - 1
                            }
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "7px",
                              padding: "10px 14px",
                              borderRadius: "9px",
                              border: "1px solid #175cd3",
                              background: "#175cd3",
                              color: "#ffffff",
                              fontWeight: 700,
                              cursor:
                                currentTopicIndex === training.topics.length - 1
                                  ? "not-allowed"
                                  : "pointer",
                              opacity:
                                currentTopicIndex === training.topics.length - 1
                                  ? 0.45
                                  : 1,
                            }}
                          >
                            Next
                            <ChevronRight size={17} />
                          </button>
                        </div>
                      </div>
                    </section>

                    {/* Completion message */}
                    {training.progress_percentage >= 100 && (
                      <section
                        style={{
                          marginTop: "18px",
                          padding: "22px",
                          borderRadius: "16px",
                          border: "1px solid #abefc6",
                          background:
                            "linear-gradient(135deg, #f0fdf4, #ecfdf3)",
                          display: "flex",
                          alignItems: "center",
                          gap: "15px",
                        }}
                      >
                        <div
                          style={{
                            width: "48px",
                            height: "48px",
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "#dcfce7",
                            color: "#15803d",
                            flexShrink: 0,
                          }}
                        >
                          <Trophy size={23} />
                        </div>

                        <div>
                          <h3
                            style={{
                              margin: "0 0 4px",
                              fontSize: "16px",
                              fontWeight: 800,
                            }}
                          >
                            Training path completed! 🎉
                          </h3>

                          <p
                            style={{
                              margin: 0,
                              color: "#475467",
                              fontSize: "13px",
                              lineHeight: 1.5,
                            }}
                          >
                            Great work. Continue with assessments and AI
                            interviews to validate what you learned.
                          </p>
                        </div>
                      </section>
                    )}
                  </>
                ) : (
                  <div
                    style={{
                      background: "#ffffff",
                      border: "1px solid #eaecf0",
                      borderRadius: "16px",
                      padding: "40px",
                      textAlign: "center",
                    }}
                  >
                    <BookOpen size={34} />
                    <h2>No topics available</h2>
                    <p style={{ color: "#667085" }}>
                      There are currently no training topics for this skill.
                    </p>
                  </div>
                )}
              </>
            ) : null}
          </main>
        </div>
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

          @media (max-width: 900px) {
            div[style*="grid-template-columns: 300px"] {
              grid-template-columns: 1fr !important;
            }
          }
        `}
      </style>
    </div>
  );
}
