import { useState } from "react";
import {
  ArrowLeft,
  Upload,
  FileText,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Sparkles,
  RefreshCw,
  Target,
  FileCheck2,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

interface ATSAnalyzeResponse {
  filename: string;
  text_length: number;
  page_count: number;
  extracted_text: string;
  ats_score: number;
  matched_skills: string[];
  missing_skills: string[];
  sections_found: string[];
  recommendations: string[];
}

function safeErrorMessage(error: any): string {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

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
    "Unable to analyze the resume. Please try again."
  );
}

function getScoreColor(score: number): string {
  if (score >= 80) {
    return "#12b76a";
  }

  if (score >= 60) {
    return "#f79009";
  }

  return "#f04438";
}

function getScoreLabel(score: number): string {
  if (score >= 85) {
    return "Excellent";
  }

  if (score >= 70) {
    return "Good";
  }

  if (score >= 50) {
    return "Needs Improvement";
  }

  return "Needs Major Improvement";
}

function formatSectionName(section: string): string {
  return section
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function ATSAnalyzer() {
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");

  const [result, setResult] =
    useState<ATSAnalyzeResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    if (
      !selectedFile.name
        .toLowerCase()
        .endsWith(".pdf")
    ) {
      setFile(null);
      setError("Please select a PDF resume.");
      return;
    }

    setFile(selectedFile);
    setError("");
    setResult(null);
  };

  const analyzeResume = async () => {
    if (!file) {
      setError("Please upload your PDF resume first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const formData = new FormData();

      formData.append("file", file);

      if (jobDescription.trim()) {
        formData.append(
          "job_description",
          jobDescription.trim()
        );
      }

      const response =
        await api.post<ATSAnalyzeResponse>(
          "/api/v1/ats/analyze",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

      setResult(response.data);
    } catch (err: any) {
      console.error("ATS Analysis Error:", err);
      setError(safeErrorMessage(err));
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalyzer = () => {
    setFile(null);
    setJobDescription("");
    setResult(null);
    setError("");

    const input =
      document.getElementById(
        "resume-upload"
      ) as HTMLInputElement | null;

    if (input) {
      input.value = "";
    }
  };

  const goBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate("/dashboard");
    }
  };

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
        {/* Back button */}
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
              "linear-gradient(135deg, #175cd3 0%, #2e90fa 55%, #53b1fd 100%)",
            borderRadius: "20px",
            padding: "30px",
            color: "#ffffff",
            marginBottom: "24px",
            boxShadow:
              "0 12px 32px rgba(46,144,250,0.18)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "14px",
            }}
          >
            <FileCheck2 size={32} />

            <div>
              <h1
                style={{
                  margin: "0 0 8px",
                  fontSize: "28px",
                  fontWeight: 800,
                }}
              >
                ATS Resume Analyzer
              </h1>

              <p
                style={{
                  margin: 0,
                  maxWidth: "760px",
                  lineHeight: 1.6,
                  opacity: 0.94,
                }}
              >
                Upload your resume and let PlacementPilot
                analyze its ATS compatibility, technical
                skills, resume sections, missing keywords,
                and improvement areas.
              </p>
            </div>
          </div>
        </div>

        {/* Upload section */}
        {!result && (
          <div
            style={{
              background: "#ffffff",
              border: "1px solid #eaecf0",
              borderRadius: "18px",
              padding: "28px",
              marginBottom: "24px",
            }}
          >
            <h2
              style={{
                margin: "0 0 6px",
                color: "#101828",
                fontSize: "20px",
              }}
            >
              Analyze Your Resume
            </h2>

            <p
              style={{
                margin: "0 0 22px",
                color: "#667085",
                fontSize: "14px",
              }}
            >
              Upload a PDF resume. You can optionally add
              a job description for a role-specific ATS
              score.
            </p>

            {/* File upload */}
            <label
              htmlFor="resume-upload"
              style={{
                display: "block",
                border:
                  "2px dashed #b2ddff",
                background: "#f5faff",
                borderRadius: "16px",
                padding: "36px 20px",
                textAlign: "center",
                cursor: "pointer",
                marginBottom: "22px",
              }}
            >
              <input
                id="resume-upload"
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                style={{
                  display: "none",
                }}
              />

              <Upload
                size={38}
                style={{
                  color: "#2e90fa",
                  marginBottom: "12px",
                }}
              />

              <div
                style={{
                  color: "#175cd3",
                  fontWeight: 800,
                  fontSize: "15px",
                  marginBottom: "5px",
                }}
              >
                {file
                  ? "Resume selected"
                  : "Click to upload your resume"}
              </div>

              <div
                style={{
                  color: "#667085",
                  fontSize: "13px",
                }}
              >
                PDF files only
              </div>

              {file && (
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                    marginTop: "16px",
                    padding: "9px 13px",
                    background: "#ffffff",
                    border:
                      "1px solid #b2ddff",
                    borderRadius: "10px",
                    color: "#344054",
                    fontSize: "13px",
                    fontWeight: 700,
                  }}
                >
                  <FileText size={16} />
                  {file.name}
                </div>
              )}
            </label>

            {/* Job description */}
            <div style={{ marginBottom: "22px" }}>
              <label
                htmlFor="job-description"
                style={{
                  display: "block",
                  color: "#344054",
                  fontSize: "14px",
                  fontWeight: 800,
                  marginBottom: "8px",
                }}
              >
                Target Job Description
                <span
                  style={{
                    color: "#98a2b3",
                    fontWeight: 500,
                    marginLeft: "6px",
                  }}
                >
                  Optional
                </span>
              </label>

              <textarea
                id="job-description"
                value={jobDescription}
                onChange={(event) =>
                  setJobDescription(event.target.value)
                }
                placeholder="Paste the job description here to get a role-specific ATS score and identify missing skills..."
                rows={7}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  border:
                    "1px solid #d0d5dd",
                  borderRadius: "12px",
                  padding: "14px",
                  resize: "vertical",
                  fontFamily: "inherit",
                  fontSize: "14px",
                  color: "#101828",
                  outline: "none",
                }}
              />
            </div>

            {/* Error */}
            {error && (
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "10px",
                  background: "#fef3f2",
                  border:
                    "1px solid #fecdca",
                  borderRadius: "12px",
                  padding: "14px",
                  marginBottom: "18px",
                }}
              >
                <AlertTriangle
                  size={19}
                  style={{
                    color: "#b42318",
                    flexShrink: 0,
                  }}
                />

                <span
                  style={{
                    color: "#b42318",
                    fontSize: "13px",
                    lineHeight: 1.5,
                  }}
                >
                  {error}
                </span>
              </div>
            )}

            {/* Analyze */}
            <button
              type="button"
              onClick={analyzeResume}
              disabled={loading || !file}
              style={{
                width: "100%",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                gap: "9px",
                padding: "13px 18px",
                border: "none",
                borderRadius: "11px",
                background:
                  loading || !file
                    ? "#98a2b3"
                    : "#175cd3",
                color: "#ffffff",
                fontSize: "14px",
                fontWeight: 800,
                cursor:
                  loading || !file
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              {loading ? (
                <>
                  <RefreshCw
                    size={17}
                    style={{
                      animation:
                        "spin 1s linear infinite",
                    }}
                  />
                  Analyzing Resume...
                </>
              ) : (
                <>
                  <Sparkles size={17} />
                  Analyze Resume
                </>
              )}
            </button>
          </div>
        )}

        {/* Results */}
        {result && (
          <>
            {/* Score */}
            <div
              style={{
                background: "#ffffff",
                border:
                  "1px solid #eaecf0",
                borderRadius: "18px",
                padding: "28px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent:
                    "space-between",
                  alignItems: "center",
                  gap: "20px",
                  flexWrap: "wrap",
                }}
              >
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      marginBottom: "8px",
                    }}
                  >
                    <Target
                      size={22}
                      style={{
                        color: "#175cd3",
                      }}
                    />

                    <h2
                      style={{
                        margin: 0,
                        color: "#101828",
                        fontSize: "20px",
                      }}
                    >
                      ATS Score
                    </h2>
                  </div>

                  <p
                    style={{
                      margin: 0,
                      color: "#667085",
                      fontSize: "14px",
                    }}
                  >
                    {result.filename}
                  </p>
                </div>

                <div
                  style={{
                    textAlign: "right",
                  }}
                >
                  <div
                    style={{
                      fontSize: "44px",
                      fontWeight: 900,
                      color: getScoreColor(
                        result.ats_score
                      ),
                      lineHeight: 1,
                    }}
                  >
                    {result.ats_score}%
                  </div>

                  <div
                    style={{
                      color: getScoreColor(
                        result.ats_score
                      ),
                      fontWeight: 800,
                      fontSize: "13px",
                      marginTop: "7px",
                    }}
                  >
                    {getScoreLabel(
                      result.ats_score
                    )}
                  </div>
                </div>
              </div>

              {/* Score bar */}
              <div
                style={{
                  marginTop: "22px",
                  height: "12px",
                  background: "#eaecf0",
                  borderRadius: "999px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${Math.min(
                      100,
                      Math.max(
                        0,
                        result.ats_score
                      )
                    )}%`,
                    background:
                      getScoreColor(
                        result.ats_score
                      ),
                    borderRadius: "999px",
                    transition:
                      "width 0.6s ease",
                  }}
                />
              </div>
            </div>

            {/* Stats */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(190px, 1fr))",
                gap: "16px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  background: "#ffffff",
                  border:
                    "1px solid #eaecf0",
                  borderRadius: "15px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    fontWeight: 700,
                    marginBottom: "8px",
                  }}
                >
                  Resume Pages
                </div>

                <div
                  style={{
                    color: "#101828",
                    fontSize: "28px",
                    fontWeight: 800,
                  }}
                >
                  {result.page_count}
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border:
                    "1px solid #eaecf0",
                  borderRadius: "15px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    fontWeight: 700,
                    marginBottom: "8px",
                  }}
                >
                  Matched Skills
                </div>

                <div
                  style={{
                    color: "#12b76a",
                    fontSize: "28px",
                    fontWeight: 800,
                  }}
                >
                  {result.matched_skills.length}
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border:
                    "1px solid #eaecf0",
                  borderRadius: "15px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    fontWeight: 700,
                    marginBottom: "8px",
                  }}
                >
                  Missing Skills
                </div>

                <div
                  style={{
                    color:
                      result.missing_skills
                        .length > 0
                        ? "#f04438"
                        : "#12b76a",
                    fontSize: "28px",
                    fontWeight: 800,
                  }}
                >
                  {result.missing_skills.length}
                </div>
              </div>

              <div
                style={{
                  background: "#ffffff",
                  border:
                    "1px solid #eaecf0",
                  borderRadius: "15px",
                  padding: "20px",
                }}
              >
                <div
                  style={{
                    color: "#667085",
                    fontSize: "13px",
                    fontWeight: 700,
                    marginBottom: "8px",
                  }}
                >
                  Sections Found
                </div>

                <div
                  style={{
                    color: "#175cd3",
                    fontSize: "28px",
                    fontWeight: 800,
                  }}
                >
                  {result.sections_found.length}
                </div>
              </div>
            </div>

            {/* Matched skills */}
            <section
              style={{
                background: "#ffffff",
                border:
                  "1px solid #eaecf0",
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
                <CheckCircle2
                  size={22}
                  style={{
                    color: "#12b76a",
                  }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "19px",
                  }}
                >
                  Matched Skills
                </h2>
              </div>

              {result.matched_skills.length ===
              0 ? (
                <p
                  style={{
                    color: "#667085",
                    margin: 0,
                  }}
                >
                  No recognized technical skills were
                  detected in this resume.
                </p>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "9px",
                  }}
                >
                  {result.matched_skills.map(
                    (skill) => (
                      <span
                        key={skill}
                        style={{
                          padding:
                            "8px 12px",
                          background:
                            "#ecfdf3",
                          border:
                            "1px solid #abefc6",
                          color: "#027a48",
                          borderRadius:
                            "999px",
                          fontSize: "13px",
                          fontWeight: 700,
                        }}
                      >
                        {skill}
                      </span>
                    )
                  )}
                </div>
              )}
            </section>

            {/* Missing skills */}
            <section
              style={{
                background: "#ffffff",
                border:
                  "1px solid #eaecf0",
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
                <XCircle
                  size={22}
                  style={{
                    color: "#f04438",
                  }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "19px",
                  }}
                >
                  Missing Skills
                </h2>
              </div>

              {result.missing_skills.length ===
              0 ? (
                <div
                  style={{
                    background: "#ecfdf3",
                    border:
                      "1px solid #abefc6",
                    borderRadius: "12px",
                    padding: "14px",
                    color: "#027a48",
                    fontSize: "14px",
                  }}
                >
                  No missing skills detected against
                  the provided job description.
                </div>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "9px",
                  }}
                >
                  {result.missing_skills.map(
                    (skill) => (
                      <span
                        key={skill}
                        style={{
                          padding:
                            "8px 12px",
                          background:
                            "#fef3f2",
                          border:
                            "1px solid #fecdca",
                          color: "#b42318",
                          borderRadius:
                            "999px",
                          fontSize: "13px",
                          fontWeight: 700,
                        }}
                      >
                        {skill}
                      </span>
                    )
                  )}
                </div>
              )}
            </section>

            {/* Sections */}
            <section
              style={{
                background: "#ffffff",
                border:
                  "1px solid #eaecf0",
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
                <FileText
                  size={22}
                  style={{
                    color: "#175cd3",
                  }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "19px",
                  }}
                >
                  Resume Sections Detected
                </h2>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(170px, 1fr))",
                  gap: "10px",
                }}
              >
                {result.sections_found.map(
                  (section) => (
                    <div
                      key={section}
                      style={{
                        display: "flex",
                        alignItems:
                          "center",
                        gap: "8px",
                        padding: "12px",
                        background:
                          "#f5faff",
                        border:
                          "1px solid #b2ddff",
                        borderRadius:
                          "10px",
                        color: "#175cd3",
                        fontSize: "13px",
                        fontWeight: 700,
                      }}
                    >
                      <CheckCircle2
                        size={16}
                      />
                      {formatSectionName(
                        section
                      )}
                    </div>
                  )
                )}
              </div>
            </section>

            {/* Recommendations */}
            <section
              style={{
                background: "#ffffff",
                border:
                  "1px solid #eaecf0",
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
                <Sparkles
                  size={22}
                  style={{
                    color: "#7f56d9",
                  }}
                />

                <h2
                  style={{
                    margin: 0,
                    color: "#101828",
                    fontSize: "19px",
                  }}
                >
                  AI Resume Improvements
                </h2>
              </div>

              <div
                style={{
                  display: "grid",
                  gap: "11px",
                }}
              >
                {result.recommendations.map(
                  (recommendation, index) => (
                    <div
                      key={`${index}-${recommendation}`}
                      style={{
                        display: "flex",
                        alignItems:
                          "flex-start",
                        gap: "12px",
                        padding: "14px",
                        background:
                          "#f9f5ff",
                        border:
                          "1px solid #e9d7fe",
                        borderRadius:
                          "11px",
                      }}
                    >
                      <div
                        style={{
                          width: "26px",
                          height: "26px",
                          minWidth: "26px",
                          borderRadius:
                            "50%",
                          background:
                            "#7f56d9",
                          color: "#ffffff",
                          display: "flex",
                          alignItems:
                            "center",
                          justifyContent:
                            "center",
                          fontSize: "12px",
                          fontWeight: 800,
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
            </section>

            {/* Extracted text info */}
            <section
              style={{
                background: "#ffffff",
                border:
                  "1px solid #eaecf0",
                borderRadius: "18px",
                padding: "24px",
                marginBottom: "24px",
              }}
            >
              <h2
                style={{
                  margin: "0 0 12px",
                  color: "#101828",
                  fontSize: "18px",
                }}
              >
                Resume Processing
              </h2>

              <p
                style={{
                  margin: 0,
                  color: "#667085",
                  fontSize: "14px",
                  lineHeight: 1.6,
                }}
              >
                Successfully extracted{" "}
                <strong>
                  {result.text_length.toLocaleString()}
                </strong>{" "}
                characters from your{" "}
                <strong>
                  {result.page_count}
                </strong>{" "}
                page PDF.
              </p>
            </section>

            {/* Actions */}
            <div
              style={{
                display: "flex",
                gap: "12px",
                flexWrap: "wrap",
              }}
            >
              <button
                type="button"
                onClick={resetAnalyzer}
                style={{
                  flex: "1 1 220px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent:
                    "center",
                  gap: "8px",
                  padding: "13px 18px",
                  border:
                    "1px solid #d0d5dd",
                  borderRadius: "11px",
                  background: "#ffffff",
                  color: "#344054",
                  fontSize: "14px",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                <RefreshCw size={17} />
                Analyze Another Resume
              </button>

              <button
                type="button"
                onClick={() =>
                  navigate("/skill-intelligence")
                }
                style={{
                  flex: "1 1 220px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent:
                    "center",
                  gap: "8px",
                  padding: "13px 18px",
                  border: "none",
                  borderRadius: "11px",
                  background: "#6941c6",
                  color: "#ffffff",
                  fontSize: "14px",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                <Sparkles size={17} />
                Continue to Skill Intelligence
              </button>
            </div>
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