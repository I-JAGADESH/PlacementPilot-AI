import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  BarChart3,
  BookOpen,
  Brain,
  ClipboardCheck,
  Briefcase,
  ChevronRight,
  FileText,
  GitBranch,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Menu,
  Route,
  Target,
  User,
  X,
  Zap,
} from "lucide-react";

import api from "../services/api";

interface Skill {
  id: number;
  name: string;
  category?: string | null;
  proficiency: number;
}

interface Project {
  id: number;
  title: string;
  description?: string | null;
  technologies?: string | null;
  github_url?: string | null;
  live_url?: string | null;
}

interface Certification {
  id: number;
  name: string;
  issuer?: string | null;
  issue_year?: number | null;
}

interface Profile {
  id: number;
  user_id: number;
  cgpa?: number | null;
  attendance?: number | null;
  backlogs: number;
  aptitude_score?: number | null;
  communication_score?: number | null;
  target_role?: string | null;
  target_company?: string | null;
  college?: string | null;
  degree?: string | null;
  graduation_year?: number | null;
  bio?: string | null;
  is_complete: boolean;
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
}

interface SkillGapItem {
  name: string;
  status: string;
  priority: string;
  reason: string;
}

interface SkillAnalysisItem {
  name: string;
  proficiency: number;
  status: string;
  priority: string;
  reason: string;
}

interface SkillGapResponse {
  overall_skill_score: number;
  strong_skills: SkillAnalysisItem[];
  weak_skills: SkillAnalysisItem[];
  missing_skills: SkillGapItem[];
  recommendations: string[];
  total_profile_skills: number;
  total_missing_skills: number;
}

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

interface ReadinessPriorityGap {
  area: string;
  current_score: number;
  target_score: number;
  gap: number;
}

interface ReadinessResponse {
  overall_score: number;
  level: string;
  probability: number;
  target: {
    role: string;
    company: string;
  };
  breakdown: {
    technical_score: number;
    dsa_score: number;
    resume_score: number;
    project_score: number;
    communication_score: number;
    aptitude_score: number;
    interview_score: number;
    academic_score: number;
    attendance_score: number;
    certification_score: number;
  };
  factors: Record<string, number>;
  strong_areas: string[];
  weak_areas: string[];
  priority_gaps: ReadinessPriorityGap[];
  recommendations: string[];
}

const DEFAULT_JOB_DESCRIPTION =
  "Software Engineer. We are looking for a Software Engineer with experience in C++, Python, Data Structures, Algorithms, SQL, Git, GitHub, REST APIs, cloud technologies and problem solving. Requirements: Strong programming fundamentals, Data Structures and Algorithms, C++ or Python, SQL, Git and GitHub, REST APIs, Cloud computing, Good problem solving skills.";

export default function Dashboard() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState<Profile | null>(null);
  const [skillGap, setSkillGap] =
    useState<SkillGapResponse | null>(null);
  const [roadmap, setRoadmap] =
    useState<RoadmapResponse | null>(null);
  const [readiness, setReadiness] =
    useState<ReadinessResponse | null>(null);
  const [readinessLoading, setReadinessLoading] =
    useState(false);

  const [jobDescription, setJobDescription] = useState(
    DEFAULT_JOB_DESCRIPTION
  );

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingRoadmap, setGeneratingRoadmap] =
    useState(false);

  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadReadiness = async () => {
    try {
      setReadinessLoading(true);

      const response = await api.get(
        "/api/v1/readiness"
      );

      setReadiness(response.data);
    } catch (err: any) {
      console.error("READINESS ERROR:", err);

      if (err.response?.status === 401) {
        handleLogout();
        return;
      }

      setReadiness(null);
    } finally {
      setReadinessLoading(false);
    }
  };

  const loadProfile = async () => {
    try {
      setLoading(true);

      const response = await api.get(
        "/api/v1/profile"
      );

      setProfile(response.data);

      await loadReadiness();
    } catch (err: any) {
      console.error("PROFILE ERROR:", err);

      if (err.response?.status === 401) {
        handleLogout();
        return;
      }

      setError("Unable to load your profile.");
    } finally {
      setLoading(false);
    }
  };

  const analyzeSkills = async () => {
    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    try {
      setAnalyzing(true);
      setError("");

      const response = await api.post(
        "/api/v1/intelligence/skill-gap",
        {
          job_description: jobDescription,
        }
      );

      setSkillGap(response.data);
    } catch (err: any) {
      console.error("SKILL GAP ERROR:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to analyze the skill gap."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const generateRoadmap = async () => {
    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    try {
      setGeneratingRoadmap(true);
      setError("");

      const response = await api.post(
        "/api/v1/roadmap/generate",
        {
          job_description: jobDescription,
        }
      );

      setRoadmap(response.data);
    } catch (err: any) {
      console.error("ROADMAP ERROR:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to generate the roadmap."
      );
    } finally {
      setGeneratingRoadmap(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  };

  const openProfile = () => {
    setSidebarOpen(false);
    navigate("/profile");
  };

  const openInterview = () => {
    setSidebarOpen(false);
    navigate("/interview");
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
        <p>Loading your placement dashboard...</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="error-screen">
        <h2>Unable to load profile</h2>

        <p>
          {error || "Student profile not found."}
        </p>

        <button onClick={loadProfile}>
          Retry
        </button>
      </div>
    );
  }

  const averageSkill =
    profile.skills.length > 0
      ? profile.skills.reduce(
          (sum, skill) => sum + skill.proficiency,
          0
        ) / profile.skills.length
      : 0;

  const strongCount =
    skillGap?.strong_skills.length ?? 0;

  const missingCount =
    skillGap?.missing_skills.length ?? 0;

  const readinessScore =
    readiness?.overall_score ??
    skillGap?.overall_skill_score ??
    averageSkill;

  const readinessLevel = readiness?.level
    ? readiness.level
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) =>
          letter.toUpperCase()
        )
    : "Profile Based";

  return (
    <div className="dashboard-layout">

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`dashboard-sidebar ${
          sidebarOpen ? "sidebar-open" : ""
        }`}
      >

        <div className="sidebar-brand">

          <div className="brand-icon">
            <Zap size={20} />
          </div>

          <div>
            <h2>PlacementPilot</h2>
                          
          </div>

          <button
            className="mobile-close"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>

        </div>

        <nav className="sidebar-nav">

          <div className="nav-section">

            <p>MAIN</p>

            <button
              className="nav-item active"
              onClick={() => {
                setSidebarOpen(false);
                navigate("/dashboard");
              }}
            >
              <LayoutDashboard size={19} />
              Dashboard
            </button>

            <button
              className="nav-item"
              onClick={openProfile}
            >
              <User size={19} />
              My Profile
            </button>

          </div>

          <div className="nav-section">

            <p>PLACEMENT TOOLS</p>

            <button
              className="nav-item"
              onClick={() => {
                setSidebarOpen(false);
                navigate("/ats");
              }}
            >
              <FileText size={19} />
              ATS Analyzer
            </button>

            <button
              className="nav-item"
              onClick={() => {
                setSidebarOpen(false);
                navigate("/skill-intelligence");
              }}
            >
              <BarChart3 size={19} />
              Skill Intelligence
            </button>

            <button
              className="nav-item"
              onClick={() => {
                setSidebarOpen(false);
                navigate("/roadmap");
              }}
            >
              <Route size={19} />
              Preparation Roadmap
            </button>

            {/* Personalized Training */}
    <button
      className="nav-item"
      onClick={() => {
        setSidebarOpen(false);
        navigate("/training");
      }}
    >
      <BookOpen size={19} />
      Personalized Training
    </button>
    {/* Skill Assessment */}
            <button
              className="nav-item"
              onClick={() => {
                setSidebarOpen(false);
                navigate("/assessment");
              }}
            >
              <ClipboardCheck size={19} />
              Skill Assessment
            </button>

            {/* AI INTERVIEW */}
            <button
              className="nav-item"
              onClick={openInterview}
            >
              <Brain size={19} />
              AI Interview
            </button>

          </div>

        </nav>

        <div className="sidebar-bottom">

          <button
            className="nav-item logout-button"
            onClick={handleLogout}
          >
            <LogOut size={19} />
            Logout
          </button>

        </div>

      </aside>

      {/* Main */}
      <main className="dashboard-main">

        {/* Header */}
        <header className="dashboard-header">

          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={23} />
          </button>

          <div className="header-title">

            <h1>Dashboard</h1>

            <p>
              Your personalized placement command center
            </p>

          </div>

          <div className="header-profile">

            <div className="avatar">
              {profile.target_role?.charAt(0) || "J"}
            </div>

            <div>

              <strong>
                {profile.target_role || "Student"}
              </strong>

                          
              <span>
                {profile.target_company ||
                  "Placement Journey"}
              </span>

            </div>

          </div>

        </header>

        <div className="dashboard-content">

          {/* Welcome */}
          <section className="welcome-section">

            <div>

              <p className="eyebrow">
                WELCOME BACK
              </p>

              <h2>
                Ready to level up your placement game? 👋
              </h2>

              <p>
                Track your skills, analyze job requirements,
                and build a personalized preparation roadmap.
              </p>

            </div>

            <div className="target-badge">

              <Target size={18} />

              <div>

                          

                <strong>
                  {profile.target_role || "Not set"}
                </strong>

              </div>

            </div>

          </section>

          {/* Error */}
          {error && (
            <div className="dashboard-error">
              {error}
            </div>
          )}

          {/* Stats */}
          <section className="stats-grid">

            <div className="stat-card primary-stat">

              <div className="stat-icon">
                <Target size={21} />
              </div>

              <div>

                <span>
                  Placement Readiness
                </span>

                <strong>
                  {readinessScore.toFixed(1)}%
                </strong>

                <small>
                  Based on your current profile
                </small>

              </div>

            </div>

            <div className="stat-card">

              <div className="stat-icon purple">
                <BarChart3 size={21} />
              </div>

              <div>

                <span>
                  Profile Skills
                </span>

                <strong>
                  {profile.skills.length}
                </strong>

                <small>
                  {strongCount > 0
                    ? `${strongCount} strong`
                    : "Analyze to classify"}
                </small>

              </div>

            </div>

            <div className="stat-card">

              <div className="stat-icon orange">
                <BookOpen size={21} />
              </div>

              <div>

                <span>
                  Skill Gaps
                </span>

                <strong>
                  {missingCount}
                </strong>

                <small>
                  {missingCount > 0
                    ? "Skills to improve"
                    : "Run skill analysis"}
                </small>

              </div>

            </div>

            <div className="stat-card">

              <div className="stat-icon green">
                <GraduationCap size={21} />
              </div>

              <div>

                <span>
                  CGPA
                </span>

                <strong>
                  {profile.cgpa?.toFixed(2) || "--"}
                </strong>

                <small>
                  {profile.backlogs === 0
                    ? "No backlogs"
                    : `${profile.backlogs} backlog(s)`}
                </small>

              </div>

            </div>

          </section>

          {/* Placement Readiness */}
          <section className="dashboard-card readiness-card">

            <div className="card-header">

              <div>

                <p className="card-eyebrow">
                  AI PLACEMENT INTELLIGENCE
                </p>

                <h3>
                  Placement Readiness
                </h3>

                <p className="card-description">
                  Your readiness is calculated from academics,
                  skills, projects, resume strength, aptitude,
                  communication and interview performance.
                </p>

              </div>

              <div className="readiness-score-circle">

                <strong>
                  {readinessLoading
                    ? "..."
                    : readinessScore.toFixed(1)}
                </strong>

                          

              </div>

            </div>

            {readinessLoading ? (

              <div className="readiness-loading">
                Calculating your placement readiness...
              </div>

            ) : readiness ? (

              <>

                <div className="readiness-summary">

                  <div>
                          
                    <strong>{readinessLevel}</strong>
                  </div>

                  <div>
                          

                    <strong>
                      {readiness.target.role ||
                        profile.target_role ||
                        "Software Engineer"}

                      {readiness.target.company
                        ? ` @ ${readiness.target.company}`
                        : profile.target_company
                        ? ` @ ${profile.target_company}`
                        : ""}
                    </strong>

                  </div>

                  <div>
                          

                    <strong>
                      {(readiness.probability * 100).toFixed(1)}%
                    </strong>
                  </div>

                </div>

                <div className="readiness-progress">

                  <div className="readiness-progress-track">

                    <div
                      className="readiness-progress-fill"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(
                            0,
                            readiness.overall_score
                          )
                        )}%`,
                      }}
                    />

                  </div>

                </div>

                <div className="readiness-columns">

                  <div className="readiness-panel">

                    <h4>
                      Strong Areas
                    </h4>

                    {readiness.strong_areas.map(
                      (area) => (
                        <div
                          className="readiness-area"
                          key={area}
                        >
                          
                          <strong>{area}</strong>
                        </div>
                      )
                    )}

                    {readiness.strong_areas.length === 0 && (
                      <p className="muted">
                        No strong areas identified yet.
                      </p>
                    )}

                  </div>

                  <div className="readiness-panel">

                    <h4>
                      Priority Gaps
                    </h4>

                    {readiness.priority_gaps
                      .slice(0, 5)
                      .map((gap) => (

                        <div
                          className="readiness-gap"
                          key={gap.area}
                        >

                          <div>
                            <strong>
                              {gap.area}
                            </strong>

                          
                            <span>
                              {gap.current_score.toFixed(1)}
                              {" → "}
                              {gap.target_score.toFixed(0)}
                            </span>
                          </div>

                          <b>
                            -{gap.gap.toFixed(1)}
                          </b>

                        </div>

                      ))}

                  </div>

                </div>

                {readiness.recommendations.length > 0 && (

                  <div className="readiness-recommendations">

                    <h4>
                      <Zap size={16} />
                      What you should do next
                    </h4>

                    {readiness.recommendations
                      .slice(0, 4)
                      .map((item, index) => (

                        <p key={index}>
                          <span>
                            {index + 1}
                          </span>

                          {item}
                        </p>

                      ))}

                  </div>

                )}

              </>

            ) : (

              <div className="empty-state">

                <p>
                  Placement readiness could not be calculated.
                </p>

                <button
                  className="secondary-button"
                  onClick={loadReadiness}
                >
                  Try Again
                </button>

              </div>

            )}

          </section>

          {/* Main grid */}
          <section className="dashboard-grid">

            {/* Skills */}
            <div className="dashboard-card skills-card">

              <div className="card-header">

                <div>

                  <p className="card-eyebrow">
                    YOUR PROFILE
                  </p>

                  <h3>
                    Skill Readiness
                  </h3>

                </div>

                <span className="score-pill">
                  {averageSkill.toFixed(0)}% avg
                </span>

              </div>

              <div className="skills-list">

                {profile.skills.length === 0 ? (

                  <div className="empty-state">
                    <p>No skills added yet.</p>
                  </div>

                ) : (

                  profile.skills.map((skill) => (

                    <div
                      className="skill-row"
                      key={skill.id}
                    >

                      <div className="skill-info">

                        <strong>
                          {skill.name}
                        </strong>

                          <span>
                            {skill.category ||
                              "Technical Skill"}
                          </span>

                      </div>

                      <div className="skill-progress-container">

                        <div className="skill-progress">

                          <div
                            className="skill-progress-fill"
                            style={{
                              width: `${skill.proficiency}%`,
                            }}
                          />

                        </div>

                        <strong>
                          {skill.proficiency}%
                        </strong>

                      </div>

                    </div>

                  ))

                )}

              </div>

            </div>

            {/* Profile snapshot */}
            <div className="dashboard-card profile-card">

              <div className="card-header">

                <div>

                  <p className="card-eyebrow">
                    PROFILE
                  </p>

                  <h3>
                    Profile Snapshot
                  </h3>

                </div>

                <User size={21} />

              </div>

              <div className="profile-details">

                <div className="profile-detail">
                          

                  <strong>
                    {profile.college || "--"}
                  </strong>
                </div>

                <div className="profile-detail">
                          

                  <strong>
                    {profile.degree || "--"}
                  </strong>
                </div>

                <div className="profile-detail">
                          

                  <strong>
                    {profile.graduation_year || "--"}
                  </strong>
                </div>

                <div className="profile-detail">
                          

                  <strong>
                    {profile.attendance
                      ? `${profile.attendance}%`
                      : "--"}
                  </strong>
                </div>

                <div className="profile-detail">
                          

                  <strong>
                    {profile.aptitude_score
                      ? `${profile.aptitude_score}%`
                      : "--"}
                  </strong>
                </div>

                <div className="profile-detail">
                          

                  <strong>
                    {profile.communication_score
                      ? `${profile.communication_score}%`
                      : "--"}
                  </strong>
                </div>

              </div>

              <div className="profile-complete">

                <div>

                  <span>
                    Profile completion
                  </span>

                  <strong>
                    {profile.is_complete
                      ? "Complete"
                      : "Incomplete"}
                  </strong>

                </div>

                <div className="completion-bar">

                  <div
                    style={{
                      width: profile.is_complete
                        ? "100%"
                        : "60%",
                    }}
                  />

                </div>

              </div>

            </div>

          </section>

          {/* Job analysis */}
          <section className="dashboard-card analysis-card">

            <div className="card-header">

              <div>

                <p className="card-eyebrow">
                  AI INTELLIGENCE
                </p>

                <h3>
                  Analyze Your Target Job
                </h3>

                <p className="card-description">
                  Compare your current profile against
                  the skills required for your target role.
                </p>

              </div>

              <div className="ai-card-icon">
                <Brain size={24} />
              </div>

            </div>

            <textarea
              className="job-description-input"
              value={jobDescription}
              onChange={(event) =>
                setJobDescription(event.target.value)
              }
              placeholder="Paste your target job description here..."
              rows={6}
            />

            <div className="analysis-actions">

              <button
                className="primary-button"
                onClick={analyzeSkills}
                disabled={analyzing}
              >
                {analyzing
                  ? "Analyzing..."
                  : "Analyze Skill Gap"}

                <ChevronRight size={18} />
              </button>

              <button
                className="secondary-button"
                onClick={generateRoadmap}
                disabled={generatingRoadmap}
              >
                <Route size={18} />

                {generatingRoadmap
                  ? "Generating..."
                  : "Generate Roadmap"}

              </button>

            </div>

          </section>

          {/* Skill gap results */}
          {skillGap && (

            <section className="dashboard-grid">

              <div className="dashboard-card">

                <div className="card-header">

                  <div>

                    <p className="card-eyebrow">
                      AI ANALYSIS
                    </p>

                    <h3>
                      Skill Gap Results
                    </h3>

                  </div>

                  <div className="large-score">
                    {skillGap.overall_skill_score.toFixed(1)}%
                  </div>

                </div>

                <div className="gap-columns">

                  <div>

                    <h4 className="strong-title">
                      Strong Skills
                    </h4>

                    {skillGap.strong_skills.map(
                      (skill) => (

                        <div
                          className="gap-item strong"
                          key={skill.name}
                        >

                          <div>

                            <strong>
                              {skill.name}
                            </strong>

                            <span>
                              {skill.reason}
                            </span>

                          </div>

                          <b>
                            {skill.proficiency}%
                          </b>

                        </div>

                      )
                    )}

                    {skillGap.strong_skills.length === 0 && (
                      <p className="muted">
                        No strong skills identified yet.
                      </p>
                    )}

                  </div>

                  <div>

                    <h4 className="missing-title">
                      Missing Skills
                    </h4>

                    {skillGap.missing_skills.map(
                      (skill) => (

                        <div
                          className="gap-item missing"
                          key={skill.name}
                        >

                          <div>

                            <strong>
                              {skill.name}
                            </strong>

                            <span>
                              {skill.reason}
                            </span>

                          </div>

                          <b>
                            {skill.priority}
                          </b>

                        </div>

                      )
                    )}

                    {skillGap.missing_skills.length === 0 && (
                      <p className="muted">
                        No missing skills identified.
                      </p>
                    )}

                  </div>

                </div>

                {skillGap.recommendations.length > 0 && (

                  <div className="recommendations">

                    <h4>
                      AI Recommendations
                    </h4>

                    {skillGap.recommendations.map(
                      (recommendation, index) => (

                        <p key={index}>
                          <Zap size={15} />
                          {recommendation}
                        </p>

                      )
                    )}

                  </div>

                )}

              </div>

            </section>

          )}

          {/* Roadmap */}
          {roadmap && (

            <section className="dashboard-card roadmap-card">

              <div className="card-header">

                <div>

                  <p className="card-eyebrow">
                    PERSONALIZED PLAN
                  </p>

                  <h3>
                    {roadmap.target_role} Roadmap
                  </h3>

                  <p className="card-description">
                    A {roadmap.total_days}-day preparation
                    plan generated from your current skill profile.
                  </p>

                </div>

                <div className="roadmap-days">

                  <strong>
                    {roadmap.total_days}
                  </strong>

                  <span>
                    days
                  </span>

                </div>

              </div>

              <div className="roadmap-tasks">

                {roadmap.tasks.map((task) => (

                  <div
                    className="roadmap-task"
                    key={task.skill}
                  >

                    <div className="roadmap-task-number">
                      {task.duration_days}
                    </div>

                    <div className="roadmap-task-content">

                      <div className="roadmap-task-top">

                        <strong>
                          {task.skill}
                        </strong>

                        <span
                          className={`priority ${task.priority}`}
                        >
                          {task.priority}
                        </span>

                      </div>

                      <p>
                        {task.reason}
                      </p>

                      <div className="topic-list">

                        {task.topics.map((topic) => (

                          <span key={topic}>
                            {topic}
                          </span>

                        ))}

                      </div>

                    </div>

                  </div>

                ))}

              </div>

            </section>

          )}

          {/* Projects */}
          <section className="dashboard-card">

            <div className="card-header">

              <div>

                <p className="card-eyebrow">
                  EXPERIENCE
                </p>

                <h3>
                  Your Projects
                </h3>

              </div>

              <Briefcase size={21} />

            </div>

            <div className="projects-grid">

              {profile.projects.length === 0 ? (

                <div className="empty-state">
                  <p>No projects added yet.</p>
                </div>

              ) : (

                profile.projects.map((project) => (

                  <div
                    className="project-card"
                    key={project.id}
                  >

                    <div className="project-icon">
                      <GitBranch size={20} />
                    </div>

                    <h4>
                      {project.title}
                    </h4>

                    <p>
                      {project.description ||
                        "Project description not available."}
                    </p>

                    {project.technologies && (

                      <div className="technology-list">

                        {project.technologies
                          .split(",")
                          .map((technology) => (

                            <span key={technology}>
                              {technology.trim()}
                            </span>

                          ))}

                      </div>

                    )}

                  </div>

                ))

              )}

            </div>

          </section>

          {/* Certifications */}
          <section className="dashboard-card">

            <div className="card-header">

              <div>

                <p className="card-eyebrow">
                  CREDENTIALS
                </p>

                <h3>
                  Certifications
                </h3>

              </div>

              <GraduationCap size={21} />

            </div>

            <div className="certifications-list">

              {profile.certifications.length === 0 ? (

                <div className="empty-state">
                  <p>No certifications added yet.</p>
                </div>

              ) : (

                profile.certifications.map(
                  (certification) => (

                    <div
                      className="certification-item"
                      key={certification.id}
                    >

                      <div className="cert-icon">
                        <GraduationCap size={20} />
                      </div>

                      <div>

                        <strong>
                          {certification.name}
                        </strong>

                          <span>
                          {certification.issuer ||
                            "Certification"}

                          {certification.issue_year
                            ? ` • ${certification.issue_year}`
                            : ""}
                        </span>

                      </div>

                    </div>

                  )
                )

              )}

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}