import { useEffect, useState } from "react";
import {
  Award,
  BookOpen,
  Briefcase,
  GitBranch,
  GraduationCap,
  Plus,
  RefreshCw,
  Save,
  Trash2,
  User,
  Pencil,
  X,
  ExternalLink,
  Unplug,
} from "lucide-react";
import api from "../services/api";
import BackButton from "../components/BackButton";
import "./Profile.css";

interface Skill {
  id: number;
  name: string;
  category: string | null;
  proficiency: number;
}

interface Project {
  id: number;
  title: string;
  description: string | null;
  technologies: string | null;
  github_url: string | null;
  live_url: string | null;
}

interface Certification {
  id: number;
  name: string;
  issuer: string | null;
  issue_year: number | null;
  credential_url: string | null;
}

interface ProfileData {
  id: number;
  user_id: number;
  cgpa: number | null;
  attendance: number | null;
  backlogs: number;
  aptitude_score: number | null;
  communication_score: number | null;
  target_role: string | null;
  target_company: string | null;
  phone: string | null;
  college: string | null;
  degree: string | null;
  graduation_year: number | null;
  github_url: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  bio: string | null;
  is_complete: boolean;
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
}

interface GitHubRepository {
  name?: string;
  full_name?: string;
  description?: string | null;
  html_url?: string;
  language?: string | null;
  stars?: number;
  forks?: number;
  topics?: string[];
  updated_at?: string;
  created_at?: string;
  private?: boolean;
}

interface GitHubProfile {
  github_user_id?: string;
  username?: string;
  name?: string | null;
  bio?: string | null;
  company?: string | null;
  location?: string | null;
  email?: string | null;
  profile_url?: string;
  avatar_url?: string;
  public_repositories?: number;
  followers?: number;
  following?: number;
}

interface GitHubStatistics {
  public_repositories: number;
  total_stars: number;
  total_forks: number;
  languages: Record<string, number>;
  technologies: string[];
  repositories: GitHubRepository[];
}

interface GitHubSyncResult {
  success?: boolean;
  message?: string;
  profile?: GitHubProfile;
  statistics: GitHubStatistics;
  synced_at?: string;
}

interface GitHubStatus {
  connected: boolean;
  username?: string | null;
  profile_url?: string | null;
  avatar_url?: string | null;
  public_repositories?: number;
  total_stars?: number;
  total_forks?: number;
  last_synced_at?: string | null;
}

export default function Profile() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [skillSaving, setSkillSaving] = useState(false);
  const [deletingSkillId, setDeletingSkillId] = useState<number | null>(null);
  const [editingSkillId, setEditingSkillId] = useState<number | null>(null);

  const [githubStatus, setGithubStatus] = useState<GitHubStatus | null>(null);
  const [githubLoading, setGithubLoading] = useState(true);
  const [githubSyncing, setGithubSyncing] = useState(false);
  const [githubResult, setGithubResult] =
    useState<GitHubSyncResult | null>(null);

  const [skillForm, setSkillForm] = useState({
    name: "",
    category: "",
    proficiency: "50",
  });

  const [editSkillForm, setEditSkillForm] = useState({
    name: "",
    category: "",
    proficiency: "50",
  });

  const [form, setForm] = useState({
    cgpa: "",
    attendance: "",
    backlogs: "0",
    aptitude_score: "",
    communication_score: "",
    target_role: "",
    target_company: "",
    phone: "",
    college: "",
    degree: "",
    graduation_year: "",
    github_url: "",
    linkedin_url: "",
    portfolio_url: "",
    bio: "",
  });

  useEffect(() => {
    loadProfile();
    loadGitHubStatus();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await api.get("/api/v1/profile");
      const data: ProfileData = response.data;

      setProfile(data);

      setForm({
        cgpa: data.cgpa?.toString() || "",
        attendance: data.attendance?.toString() || "",
        backlogs: data.backlogs?.toString() || "0",
        aptitude_score: data.aptitude_score?.toString() || "",
        communication_score:
          data.communication_score?.toString() || "",
        target_role: data.target_role || "",
        target_company: data.target_company || "",
        phone: data.phone || "",
        college: data.college || "",
        degree: data.degree || "",
        graduation_year:
          data.graduation_year?.toString() || "",
        github_url: data.github_url || "",
        linkedin_url: data.linkedin_url || "",
        portfolio_url: data.portfolio_url || "",
        bio: data.bio || "",
      });
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to load your profile."
      );
    } finally {
      setLoading(false);
    }
  };

  const loadGitHubStatus = async () => {
    setGithubLoading(true);

    try {
      const response = await api.get("/api/v1/github/status");
      setGithubStatus(response.data);
    } catch {
      setGithubStatus({
        connected: false,
      });
    } finally {
      setGithubLoading(false);
    }
  };

  const handleConnectGitHub = async () => {
    setMessage("");
    setError("");

    try {
      const response = await api.get("/api/v1/github/connect");

      const authorizationUrl =
        response.data?.authorization_url;

      if (!authorizationUrl) {
        throw new Error(
          "GitHub authorization URL was not returned."
        );
      }

      window.location.href = authorizationUrl;
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Unable to connect GitHub."
      );
    }
  };

  const handleSyncGitHub = async () => {
    setGithubSyncing(true);
    setMessage("");
    setError("");

    try {
      const response = await api.post("/api/v1/github/sync");

      const data: GitHubSyncResult = response.data;

      setGithubResult(data);

      if (data.statistics) {
        setGithubStatus((previous) => ({
          ...(previous || { connected: true }),
          connected: true,
          username:
            data.profile?.username ||
            previous?.username ||
            null,
          profile_url:
            data.profile?.profile_url ||
            previous?.profile_url ||
            null,
          avatar_url:
            data.profile?.avatar_url ||
            previous?.avatar_url ||
            null,
          public_repositories:
            data.statistics.public_repositories,
          total_stars:
            data.statistics.total_stars,
          total_forks:
            data.statistics.total_forks,
          last_synced_at:
            data.synced_at ||
            previous?.last_synced_at ||
            null,
        }));
      } else {
        await loadGitHubStatus();
      }

      setMessage(
        data.message ||
          "GitHub profile synchronized successfully."
      );
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to synchronize GitHub."
      );
    } finally {
      setGithubSyncing(false);
    }
  };

  const handleDisconnectGitHub = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to disconnect your GitHub account?"
    );

    if (!confirmed) {
      return;
    }

    setMessage("");
    setError("");

    try {
      await api.delete("/api/v1/github/disconnect");

      setGithubStatus({
        connected: false,
      });

      setGithubResult(null);

      setMessage(
        "GitHub account disconnected successfully."
      );
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to disconnect GitHub."
      );
    }
  };

  const updateField = (
    field: keyof typeof form,
    value: string
  ) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    setError("");

    try {
      const payload = {
        cgpa: form.cgpa ? Number(form.cgpa) : null,
        attendance: form.attendance
          ? Number(form.attendance)
          : null,
        backlogs: Number(form.backlogs || 0),
        aptitude_score: form.aptitude_score
          ? Number(form.aptitude_score)
          : null,
        communication_score:
          form.communication_score
            ? Number(form.communication_score)
            : null,
        target_role: form.target_role || null,
        target_company: form.target_company || null,
        phone: form.phone || null,
        college: form.college || null,
        degree: form.degree || null,
        graduation_year: form.graduation_year
          ? Number(form.graduation_year)
          : null,
        github_url: form.github_url || null,
        linkedin_url: form.linkedin_url || null,
        portfolio_url: form.portfolio_url || null,
        bio: form.bio || null,
      };

      const response = await api.put(
        "/api/v1/profile",
        payload
      );

      setProfile(response.data);
      setMessage("Profile updated successfully.");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to update your profile."
      );
    } finally {
      setSaving(false);
    }
  };

  const updateSkillField = (
    field: keyof typeof skillForm,
    value: string
  ) => {
    setSkillForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const updateEditSkillField = (
    field: keyof typeof editSkillForm,
    value: string
  ) => {
    setEditSkillForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleAddSkill = async () => {
    setMessage("");
    setError("");

    const skillName = skillForm.name.trim();

    if (!skillName) {
      setError("Please enter a skill name.");
      return;
    }

    const proficiency = Number(skillForm.proficiency);

    if (
      Number.isNaN(proficiency) ||
      proficiency < 0 ||
      proficiency > 100
    ) {
      setError("Proficiency must be between 0 and 100.");
      return;
    }

    setSkillSaving(true);

    try {
      const payload = {
        name: skillName,
        category: skillForm.category.trim() || null,
        proficiency,
      };

      const response = await api.post(
        "/api/v1/profile/skills",
        payload
      );

      const newSkill: Skill = response.data;

      setProfile((previous) => {
        if (!previous) {
          return previous;
        }

        return {
          ...previous,
          skills: [...previous.skills, newSkill],
        };
      });

      setSkillForm({
        name: "",
        category: "",
        proficiency: "50",
      });

      setMessage("Skill added successfully.");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to add skill."
      );
    } finally {
      setSkillSaving(false);
    }
  };

  const handleStartEditSkill = (skill: Skill) => {
    setMessage("");
    setError("");

    setEditingSkillId(skill.id);

    setEditSkillForm({
      name: skill.name,
      category: skill.category || "",
      proficiency: skill.proficiency.toString(),
    });
  };

  const handleCancelEditSkill = () => {
    setEditingSkillId(null);

    setEditSkillForm({
      name: "",
      category: "",
      proficiency: "50",
    });
  };

  const handleUpdateSkill = async (skillId: number) => {
    setMessage("");
    setError("");

    const skillName = editSkillForm.name.trim();

    if (!skillName) {
      setError("Please enter a skill name.");
      return;
    }

    const proficiency = Number(
      editSkillForm.proficiency
    );

    if (
      Number.isNaN(proficiency) ||
      proficiency < 0 ||
      proficiency > 100
    ) {
      setError("Proficiency must be between 0 and 100.");
      return;
    }

    setSkillSaving(true);

    try {
      const payload = {
        name: skillName,
        category:
          editSkillForm.category.trim() || null,
        proficiency,
      };

      const response = await api.put(
        `/api/v1/profile/skills/${skillId}`,
        payload
      );

      const updatedSkill: Skill = response.data;

      setProfile((previous) => {
        if (!previous) {
          return previous;
        }

        return {
          ...previous,
          skills: previous.skills.map((skill) =>
            skill.id === skillId
              ? updatedSkill
              : skill
          ),
        };
      });

      setEditingSkillId(null);

      setEditSkillForm({
        name: "",
        category: "",
        proficiency: "50",
      });

      setMessage("Skill updated successfully.");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to update skill."
      );
    } finally {
      setSkillSaving(false);
    }
  };

  const handleDeleteSkill = async (skillId: number) => {
    const skill = profile?.skills.find(
      (item) => item.id === skillId
    );

    if (!skill) {
      return;
    }

    const confirmed = window.confirm(
      `Are you sure you want to delete "${skill.name}"?`
    );

    if (!confirmed) {
      return;
    }

    setMessage("");
    setError("");
    setDeletingSkillId(skillId);

    try {
      await api.delete(
        `/api/v1/profile/skills/${skillId}`
      );

      setProfile((previous) => {
        if (!previous) {
          return previous;
        }

        return {
          ...previous,
          skills: previous.skills.filter(
            (item) => item.id !== skillId
          ),
        };
      });

      if (editingSkillId === skillId) {
        setEditingSkillId(null);
      }

      setMessage("Skill deleted successfully.");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Unable to delete skill."
      );
    } finally {
      setDeletingSkillId(null);
    }
  };

  if (loading) {
    return (
      <div className="profile-loading">
        Loading your profile...
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-loading">
        {error || "Profile not found."}
      </div>
    );
  }

  const repositories =
    githubResult?.statistics?.repositories || [];

  const languages =
    githubResult?.statistics?.languages || {};

  return (
    <div className="profile-page">
      <header className="profile-header">
        <BackButton />

        <div>
          <h1>My Profile</h1>
          <p>
            Manage the information PlacementPilot AI uses
            to personalize your preparation.
          </p>
        </div>

        <button
          className="save-button"
          onClick={handleSave}
          disabled={saving}
        >
          <Save size={18} />
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </header>

      {message && (
        <div className="profile-success">
          {message}
        </div>
      )}

      {error && (
        <div className="profile-error">
          {error}
        </div>
      )}

      <section className="profile-grid">
        <div className="profile-card">
          <div className="card-heading">
            <User size={20} />
            <div>
              <h2>Personal Information</h2>
              <p>Basic details about you</p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>Phone</label>
              <input
                value={form.phone}
                onChange={(e) =>
                  updateField(
                    "phone",
                    e.target.value
                  )
                }
                placeholder="+91..."
              />
            </div>

            <div className="form-group">
              <label>College</label>
              <input
                value={form.college}
                onChange={(e) =>
                  updateField(
                    "college",
                    e.target.value
                  )
                }
              />
            </div>

            <div className="form-group full-width">
              <label>Degree</label>
              <input
                value={form.degree}
                onChange={(e) =>
                  updateField(
                    "degree",
                    e.target.value
                  )
                }
              />
            </div>

            <div className="form-group">
              <label>Graduation Year</label>
              <input
                type="number"
                value={form.graduation_year}
                onChange={(e) =>
                  updateField(
                    "graduation_year",
                    e.target.value
                  )
                }
              />
            </div>

            <div className="form-group">
              <label>Backlogs</label>
              <input
                type="number"
                min="0"
                value={form.backlogs}
                onChange={(e) =>
                  updateField(
                    "backlogs",
                    e.target.value
                  )
                }
              />
            </div>
          </div>
        </div>

        <div className="profile-card">
          <div className="card-heading">
            <Briefcase size={20} />
            <div>
              <h2>Placement Target</h2>
              <p>Your career target</p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>Target Role</label>
              <input
                value={form.target_role}
                onChange={(e) =>
                  updateField(
                    "target_role",
                    e.target.value
                  )
                }
              />
            </div>

            <div className="form-group">
              <label>Target Company</label>
              <input
                value={form.target_company}
                onChange={(e) =>
                  updateField(
                    "target_company",
                    e.target.value
                  )
                }
              />
            </div>
          </div>
        </div>

        <div className="profile-card">
          <div className="card-heading">
            <GraduationCap size={20} />
            <div>
              <h2>Academic & Assessment</h2>
              <p>Your current preparation metrics</p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>CGPA</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="10"
                value={form.cgpa}
                onChange={(e) =>
                  updateField(
                    "cgpa",
                    e.target.value
                  )
                }
              />
            </div>

            <div className="form-group">
              <label>Attendance %</label>
              <input
                type="number"
                min="0"
                max="100"
                value={form.attendance}
                onChange={(e) =>
                  updateField(
                    "attendance",
                    e.target.value
                  )
                }
              />
            </div>

            <div className="form-group">
              <label>Aptitude Score</label>
              <input
                type="number"
                min="0"
                max="100"
                value={form.aptitude_score}
                onChange={(e) =>
                  updateField(
                    "aptitude_score",
                    e.target.value
                  )
                }
              />
            </div>

            <div className="form-group">
              <label>Communication Score</label>
              <input
                type="number"
                min="0"
                max="100"
                value={form.communication_score}
                onChange={(e) =>
                  updateField(
                    "communication_score",
                    e.target.value
                  )
                }
              />
            </div>
          </div>
        </div>

        <div className="profile-card">
          <div className="card-heading">
            <BookOpen size={20} />
            <div>
              <h2>About Me</h2>
              <p>Tell PlacementPilot about yourself</p>
            </div>
          </div>

          <div className="form-group">
            <label>Bio</label>
            <textarea
              rows={5}
              value={form.bio}
              onChange={(e) =>
                updateField(
                  "bio",
                  e.target.value
                )
              }
              placeholder="Write a short professional bio..."
            />
          </div>
        </div>

        <div className="profile-card profile-card-wide">
          <div className="card-heading">
            <GitBranch size={20} />
            <div>
              <h2>GitHub Integration</h2>
              <p>
                Connect GitHub to automatically import your
                developer profile and repository activity.
              </p>
            </div>
          </div>

          {githubLoading ? (
            <div className="profile-loading">
              Checking GitHub connection...
            </div>
          ) : !githubStatus?.connected ? (
            <div className="github-connect-box">
              <div>
                <h3>Connect your GitHub account</h3>
                <p>
                  Securely connect your GitHub account
                  using GitHub OAuth.
                </p>
              </div>

              <button
                type="button"
                className="save-button"
                onClick={handleConnectGitHub}
              >
                <GitBranch size={18} />
                Connect GitHub
              </button>
            </div>
          ) : (
            <>
              <div className="github-account-box">
                <div className="github-account-info">
                  {githubStatus.avatar_url ? (
                    <img
                      src={githubStatus.avatar_url}
                      alt="GitHub avatar"
                      className="github-avatar"
                    />
                  ) : (
                    <div className="github-avatar github-avatar-fallback">
                      <GitBranch size={28} />
                    </div>
                  )}

                  <div>
                    <h3>
                      {githubStatus.username ||
                        "GitHub Account"}
                    </h3>

                    <p>
                      GitHub account connected successfully.
                    </p>

                    {githubStatus.profile_url && (
                      <a
                        href={githubStatus.profile_url}
                        target="_blank"
                        rel="noreferrer"
                        className="github-profile-link"
                      >
                        View GitHub Profile
                        <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                </div>

                <div className="github-actions">
                  <button
                    type="button"
                    className="save-button"
                    onClick={handleSyncGitHub}
                    disabled={githubSyncing}
                  >
                    <RefreshCw
                      size={18}
                      className={
                        githubSyncing
                          ? "github-spin"
                          : ""
                      }
                    />
                    {githubSyncing
                      ? "Syncing..."
                      : "Sync GitHub"}
                  </button>

                  <button
                    type="button"
                    className="skill-cancel-btn"
                    onClick={handleDisconnectGitHub}
                    disabled={githubSyncing}
                  >
                    <Unplug size={16} />
                    Disconnect
                  </button>
                </div>
              </div>

              <div className="github-stats-grid">
                <div className="github-stat">
                  <strong>
                    {githubResult?.statistics
                      ?.public_repositories ??
                      githubStatus.public_repositories ??
                      0}
                  </strong>
                  <span>Repositories</span>
                </div>

                <div className="github-stat">
                  <strong>
                    {githubResult?.statistics
                      ?.total_stars ??
                      githubStatus.total_stars ??
                      0}
                  </strong>
                  <span>Total Stars</span>
                </div>

                <div className="github-stat">
                  <strong>
                    {githubResult?.statistics
                      ?.total_forks ??
                      githubStatus.total_forks ??
                      0}
                  </strong>
                  <span>Total Forks</span>
                </div>
              </div>

              {githubResult && (
                <div className="github-sync-result">
                  <h3>Latest GitHub Data</h3>

                  {githubResult.profile && (
                    <div className="github-result-grid">
                      {githubResult.profile.name && (
                        <div>
                          <small>Name</small>
                          <strong>
                            {githubResult.profile.name}
                          </strong>
                        </div>
                      )}

                      {githubResult.profile.followers !==
                        undefined && (
                        <div>
                          <small>Followers</small>
                          <strong>
                            {githubResult.profile.followers}
                          </strong>
                        </div>
                      )}

                      {githubResult.profile.following !==
                        undefined && (
                        <div>
                          <small>Following</small>
                          <strong>
                            {githubResult.profile.following}
                          </strong>
                        </div>
                      )}

                      {githubResult.profile.company && (
                        <div>
                          <small>Company</small>
                          <strong>
                            {githubResult.profile.company}
                          </strong>
                        </div>
                      )}
                    </div>
                  )}

                  {githubResult.profile?.bio && (
                    <div className="github-bio">
                      <small>Bio</small>
                      <p>
                        {githubResult.profile.bio}
                      </p>
                    </div>
                  )}

                  {Object.keys(languages).length > 0 && (
                    <div className="github-languages">
                      <h4>Languages Detected</h4>

                      <div className="github-language-list">
                        {Object.entries(languages)
                          .sort(
                            ([, a], [, b]) => b - a
                          )
                          .map(
                            ([language, count]) => (
                              <span
                                key={language}
                                className="github-language-tag"
                              >
                                {language} · {count}
                              </span>
                            )
                          )}
                      </div>
                    </div>
                  )}

                  {repositories.length > 0 && (
                    <div className="github-repositories">
                      <h4>Repositories</h4>

                      <div className="github-repository-list">
                        {repositories.map(
                          (repository, index) => (
                            <div
                              className="github-repository"
                              key={
                                repository.full_name ||
                                repository.name ||
                                index
                              }
                            >
                              <div>
                                <strong>
                                  {repository.name ||
                                    "Repository"}
                                </strong>

                                {repository.description && (
                                  <p>
                                    {
                                      repository.description
                                    }
                                  </p>
                                )}

                                <div>
                                  {repository.language && (
                                    <small>
                                      {
                                        repository.language
                                      }
                                    </small>
                                  )}

                                  {repository.stars !==
                                    undefined && (
                                    <small>
                                      {" "}
                                      · ⭐{" "}
                                      {
                                        repository.stars
                                      }
                                    </small>
                                  )}

                                  {repository.forks !==
                                    undefined && (
                                    <small>
                                      {" "}
                                      · Forks:{" "}
                                      {
                                        repository.forks
                                      }
                                    </small>
                                  )}
                                </div>
                              </div>

                              {repository.html_url && (
                                <a
                                  href={
                                    repository.html_url
                                  }
                                  target="_blank"
                                  rel="noreferrer"
                                  aria-label={`Open ${
                                    repository.name ||
                                    "repository"
                                  } on GitHub`}
                                >
                                  <ExternalLink
                                    size={16}
                                  />
                                </a>
                              )}
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        <div className="profile-card profile-card-wide">
          <div className="card-heading">
            <Award size={20} />
            <div>
              <h2>Skills</h2>
              <p>
                Build your technical profile and track your
                proficiency.
              </p>
            </div>
          </div>

          <div className="skill-add-box">
            <div className="skill-add-title">
              <Plus size={18} />
              <h3>Add Skill</h3>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label>Skill Name</label>
                <input
                  value={skillForm.name}
                  onChange={(e) =>
                    updateSkillField(
                      "name",
                      e.target.value
                    )
                  }
                  placeholder="e.g. Java"
                  disabled={skillSaving}
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <input
                  value={skillForm.category}
                  onChange={(e) =>
                    updateSkillField(
                      "category",
                      e.target.value
                    )
                  }
                  placeholder="e.g. Programming"
                  disabled={skillSaving}
                />
              </div>

              <div className="form-group">
                <label>Proficiency (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={skillForm.proficiency}
                  onChange={(e) =>
                    updateSkillField(
                      "proficiency",
                      e.target.value
                    )
                  }
                  disabled={skillSaving}
                />
              </div>

              <div className="skill-add-action">
                <button
                  type="button"
                  className="save-button"
                  onClick={handleAddSkill}
                  disabled={skillSaving}
                >
                  <Plus size={18} />
                  {skillSaving
                    ? "Adding..."
                    : "Add Skill"}
                </button>
              </div>
            </div>
          </div>

          <div className="skill-list">
            {profile.skills.length === 0 ? (
              <p>No skills added yet.</p>
            ) : (
              profile.skills.map((skill) => (
                <div
                  className={`skill-row ${
                    editingSkillId === skill.id
                      ? "skill-row-editing"
                      : ""
                  }`}
                  key={skill.id}
                >
                  {editingSkillId === skill.id ? (
                    <>
                      <div className="skill-edit-fields">
                        <div className="form-group">
                          <label>Skill Name</label>
                          <input
                            value={editSkillForm.name}
                            onChange={(e) =>
                              updateEditSkillField(
                                "name",
                                e.target.value
                              )
                            }
                            disabled={skillSaving}
                          />
                        </div>

                        <div className="form-group">
                          <label>Category</label>
                          <input
                            value={
                              editSkillForm.category
                            }
                            onChange={(e) =>
                              updateEditSkillField(
                                "category",
                                e.target.value
                              )
                            }
                            disabled={skillSaving}
                          />
                        </div>

                        <div className="form-group">
                          <label>Proficiency (%)</label>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={
                              editSkillForm.proficiency
                            }
                            onChange={(e) =>
                              updateEditSkillField(
                                "proficiency",
                                e.target.value
                              )
                            }
                            disabled={skillSaving}
                          />
                        </div>
                      </div>

                      <div className="skill-edit-actions">
                        <button
                          type="button"
                          className="skill-save-btn"
                          onClick={() =>
                            handleUpdateSkill(
                              skill.id
                            )
                          }
                          disabled={skillSaving}
                        >
                          <Save size={16} />
                          Save
                        </button>

                        <button
                          type="button"
                          className="skill-cancel-btn"
                          onClick={
                            handleCancelEditSkill
                          }
                          disabled={skillSaving}
                        >
                          <X size={16} />
                          Cancel
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="skill-info">
                        <strong>{skill.name}</strong>
                        <small>
                          {skill.category ||
                            "General"}
                        </small>
                      </div>

                      <div className="skill-progress">
                        <div className="skill-bar">
                          <span
                            style={{
                              width: `${skill.proficiency}%`,
                            }}
                          />
                        </div>

                        <strong>
                          {skill.proficiency}%
                        </strong>
                      </div>

                      <button
                        type="button"
                        className="skill-edit-icon"
                        onClick={() =>
                          handleStartEditSkill(
                            skill
                          )
                        }
                        disabled={
                          deletingSkillId ===
                            skill.id ||
                          skillSaving
                        }
                        title={`Edit ${skill.name}`}
                        aria-label={`Edit ${skill.name}`}
                      >
                        <Pencil size={17} />
                      </button>

                      <button
                        type="button"
                        className="skill-delete-icon"
                        onClick={() =>
                          handleDeleteSkill(
                            skill.id
                          )
                        }
                        disabled={
                          deletingSkillId ===
                            skill.id ||
                          skillSaving
                        }
                        title={`Delete ${skill.name}`}
                        aria-label={`Delete ${skill.name}`}
                      >
                        <Trash2 size={17} />
                      </button>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="profile-card">
          <div className="card-heading">
            <Briefcase size={20} />
            <div>
              <h2>Projects</h2>
              <p>Your practical experience</p>
            </div>
          </div>

          <div className="project-list">
            {profile.projects.length === 0 ? (
              <p>No projects added yet.</p>
            ) : (
              profile.projects.map((project) => (
                <div
                  className="project-item"
                  key={project.id}
                >
                  <h3>{project.title}</h3>

                  {project.description && (
                    <p>{project.description}</p>
                  )}

                  {project.technologies && (
                    <small>
                      {project.technologies}
                    </small>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="profile-card">
          <div className="card-heading">
            <Award size={20} />
            <div>
              <h2>Certifications</h2>
              <p>Your credentials</p>
            </div>
          </div>

          <div className="certification-list">
            {profile.certifications.length === 0 ? (
              <p>No certifications added yet.</p>
            ) : (
              profile.certifications.map(
                (certification) => (
                  <div
                    className="certification-item"
                    key={certification.id}
                  >
                    <div>
                      <h3>
                        {certification.name}
                      </h3>

                      <p>
                        {certification.issuer ||
                          "Unknown issuer"}
                      </p>
                    </div>

                    {certification.issue_year && (
                      <span>
                        {certification.issue_year}
                      </span>
                    )}
                  </div>
                )
              )
            )}
          </div>
        </div>
      </section>
    </div>
  );
}



