import re

from sqlalchemy.orm import Session

from app.profile.models import StudentProfile


# ============================================================
# KNOWN SKILLS + ALIASES
# ============================================================

SKILL_ALIASES = {
    "C++": [
        "c++",
        "cpp",
    ],
    "Python": [
        "python",
        "python3",
    ],
    "Java": [
        "java",
    ],
    "C": [
        "c programming",
        "c language",
    ],
    "SQL": [
        "sql",
        "structured query language",
    ],
    "Data Structures": [
        "data structures",
        "data structure",
    ],
    "Algorithms": [
        "algorithms",
        "algorithm",
    ],
    "DSA": [
        "dsa",
        "data structures and algorithms",
    ],
    "Git": [
        "git",
        "git version control",
        "version control",
    ],
    "GitHub": [
        "github",
    ],
    "Docker": [
        "docker",
        "containerization",
        "containers",
    ],
    "AWS": [
        "aws",
        "amazon web services",
    ],
    "Azure": [
        "azure",
        "microsoft azure",
    ],
    "GCP": [
        "gcp",
        "google cloud",
        "google cloud platform",
    ],
    "React": [
        "react",
        "reactjs",
        "react.js",
    ],
    "FastAPI": [
        "fastapi",
        "fast api",
    ],
    "Node.js": [
        "node.js",
        "nodejs",
        "node",
    ],
    "JavaScript": [
        "javascript",
        "js",
    ],
    "TypeScript": [
        "typescript",
        "ts",
    ],
    "HTML": [
        "html",
    ],
    "CSS": [
        "css",
    ],
    "REST API": [
        "rest api",
        "restful api",
    ],
    "OOP": [
        "oop",
        "object oriented programming",
        "object-oriented programming",
    ],
    "DBMS": [
        "dbms",
        "database management systems",
        "database management system",
    ],
    "Operating Systems": [
        "operating systems",
        "operating system",
    ],
    "Computer Networks": [
        "computer networks",
        "computer network",
        "networking",
    ],
    "Machine Learning": [
        "machine learning",
    ],
    "Artificial Intelligence": [
        "artificial intelligence",
    ],
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for reliable skill matching.
    """

    if not text:
        return ""

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SKILL MATCHING
# ============================================================

def contains_skill(text: str, skill: str) -> bool:
    """
    Determine whether a skill or one of its aliases
    exists inside the supplied text.
    """

    normalized_text = normalize_text(text)

    aliases = SKILL_ALIASES.get(
        skill,
        [skill],
    )

    for alias in aliases:

        normalized_alias = normalize_text(alias)

        if not normalized_alias:
            continue

        # Use word boundaries for short aliases.
        if len(normalized_alias) <= 2:

            pattern = (
                r"(?<![a-z0-9+#])"
                + re.escape(normalized_alias)
                + r"(?![a-z0-9+#])"
            )

            if re.search(
                pattern,
                normalized_text,
            ):
                return True

        else:

            if normalized_alias in normalized_text:
                return True

    return False


# ============================================================
# EXTRACT SKILLS FROM JOB DESCRIPTION
# ============================================================

def extract_job_skills(
    job_description: str,
) -> list[str]:
    """
    Detect known skills mentioned in a job description.
    """

    if not job_description:
        return []

    detected = []

    for skill in SKILL_ALIASES:

        if contains_skill(
            job_description,
            skill,
        ):
            detected.append(skill)

    return detected


# ============================================================
# PROFILE SKILL PROFICIENCY
# ============================================================

def get_skill_status(
    proficiency: float,
) -> tuple[str, str]:
    """
    Convert proficiency into readiness status and priority.
    """

    if proficiency >= 75:
        return "strong", "low"

    if proficiency >= 60:
        return "good", "medium"

    return "weak", "high"


# ============================================================
# BUILD SKILL EVIDENCE
# ============================================================

def build_skill_evidence(
    profile: StudentProfile,
) -> dict[str, list[str]]:
    """
    Build evidence for skills from:

    1. Explicit profile skills
    2. Project technologies
    3. Project descriptions
    4. Certification names
    5. Certification issuers
    """

    evidence: dict[str, list[str]] = {}

    def add_evidence(
        skill_name: str,
        source: str,
    ):
        key = skill_name.lower()

        if key not in evidence:
            evidence[key] = []

        if source not in evidence[key]:
            evidence[key].append(source)

    # --------------------------------------------------------
    # Explicit profile skills
    # --------------------------------------------------------

    for skill in profile.skills or []:

        skill_name = skill.name.strip()

        for known_skill in SKILL_ALIASES:

            if contains_skill(
                skill_name,
                known_skill,
            ):

                add_evidence(
                    known_skill,
                    "profile_skill",
                )

    # --------------------------------------------------------
    # Project evidence
    # --------------------------------------------------------

    for project in profile.projects or []:

        project_text = " ".join(
            [
                project.title or "",
                project.description or "",
                project.technologies or "",
            ]
        )

        for known_skill in SKILL_ALIASES:

            if contains_skill(
                project_text,
                known_skill,
            ):

                add_evidence(
                    known_skill,
                    f"project:{project.title}",
                )

    # --------------------------------------------------------
    # Certification evidence
    # --------------------------------------------------------

    for certification in profile.certifications or []:

        certification_text = " ".join(
            [
                certification.name or "",
                certification.issuer or "",
            ]
        )

        for known_skill in SKILL_ALIASES:

            if contains_skill(
                certification_text,
                known_skill,
            ):

                add_evidence(
                    known_skill,
                    f"certification:{certification.name}",
                )

    return evidence


# ============================================================
# ESTIMATE PROFICIENCY FROM EVIDENCE
# ============================================================

def evidence_proficiency(
    evidence: list[str],
) -> float:
    """
    Estimate a baseline proficiency when a skill is
    demonstrated through projects or certifications
    but does not exist as an explicit profile skill.

    This is intentionally conservative.
    """

    if not evidence:
        return 0.0

    has_profile = any(
        item == "profile_skill"
        for item in evidence
    )

    project_count = sum(
        1
        for item in evidence
        if item.startswith("project:")
    )

    certification_count = sum(
        1
        for item in evidence
        if item.startswith("certification:")
    )

    # Explicit profile skill is handled separately.
    if has_profile:
        return 0.0

    # Project evidence is stronger than certification-only
    # evidence for practical engineering skills.
    if project_count >= 2:
        return 70.0

    if project_count == 1:
        return 60.0

    if certification_count >= 1:
        return 45.0

    return 0.0


# ============================================================
# MAIN INTELLIGENCE ENGINE
# ============================================================

def analyze_skill_intelligence(
    db: Session,
    user_id: int,
    job_description: str | None = None,
):
    """
    Analyze the student's skills using:

    - Profile skills
    - Projects
    - Certifications
    - Job description
    """

    profile = (
        db.query(StudentProfile)
        .filter(
            StudentProfile.user_id == user_id
        )
        .first()
    )

    if not profile:
        return None

    student_skills = profile.skills or []

    # --------------------------------------------------------
    # Explicit profile skill map
    # --------------------------------------------------------

    student_skill_map = {}

    for skill in student_skills:

        skill_name = skill.name.strip()

        student_skill_map[
            skill_name.lower()
        ] = {
            "name": skill_name,
            "proficiency": float(
                skill.proficiency
            ),
        }

    # --------------------------------------------------------
    # Build evidence
    # --------------------------------------------------------

    evidence_map = build_skill_evidence(
        profile
    )

    # --------------------------------------------------------
    # Analyze existing profile skills
    # --------------------------------------------------------

    strong_skills = []
    weak_skills = []

    proficiency_values = []

    for skill in student_skill_map.values():

        skill_name = skill["name"]
        proficiency = skill["proficiency"]

        proficiency_values.append(
            proficiency
        )

        status, priority = get_skill_status(
            proficiency
        )

        evidence = evidence_map.get(
            skill_name.lower(),
            ["profile_skill"],
        )

        if status in ("strong", "good"):

            strong_skills.append(
                {
                    "name": skill_name,
                    "proficiency": proficiency,
                    "status": status,
                    "priority": priority,
                    "evidence": evidence,
                    "reason": (
                        f"Your current proficiency is "
                        f"{proficiency:.0f}%. "
                        "You have a good foundation in "
                        f"{skill_name}."
                    ),
                }
            )

        else:

            weak_skills.append(
                {
                    "name": skill_name,
                    "proficiency": proficiency,
                    "status": "weak",
                    "priority": "high",
                    "evidence": evidence,
                    "reason": (
                        f"Your current proficiency is "
                        f"{proficiency:.0f}%. "
                        f"{skill_name} should be "
                        "prioritized for improvement."
                    ),
                }
            )

    # --------------------------------------------------------
    # Skills found through projects/certifications
    # but not explicitly entered into the profile
    # --------------------------------------------------------

    known_profile_names = {
        skill["name"].lower()
        for skill in student_skill_map.values()
    }

    evidence_only_skills = []

    for known_skill, evidence in evidence_map.items():

        if known_skill in known_profile_names:
            continue

        estimated = evidence_proficiency(
            evidence
        )

        if estimated <= 0:
            continue

        evidence_only_skills.append(
            {
                "name": known_skill,
                "proficiency": estimated,
                "status": "evidence",
                "priority": "medium",
                "evidence": evidence,
                "reason": (
                    f"{known_skill} was detected from "
                    "your projects or certifications. "
                    "Add it to your profile with an "
                    "accurate proficiency level."
                ),
            }
        )

    # --------------------------------------------------------
    # Job description
    # --------------------------------------------------------

    required_job_skills = extract_job_skills(
        job_description or ""
    )

    missing_skills = []

    # --------------------------------------------------------
    # Compare required skills against ALL evidence
    # --------------------------------------------------------

    for required_skill in required_job_skills:

        matched_profile_skill = None

        # First check explicit profile skills.
        for profile_skill in student_skill_map.values():

            if contains_skill(
                profile_skill["name"],
                required_skill,
            ):

                matched_profile_skill = profile_skill
                break

        # ----------------------------------------------------
        # Explicit profile skill found
        # ----------------------------------------------------

        if matched_profile_skill:

            proficiency = (
                matched_profile_skill[
                    "proficiency"
                ]
            )

            if proficiency < 60:

                already_exists = any(
                    item["name"].lower()
                    == matched_profile_skill[
                        "name"
                    ].lower()
                    for item in weak_skills
                )

                if not already_exists:

                    weak_skills.append(
                        {
                            "name": matched_profile_skill[
                                "name"
                            ],
                            "proficiency": proficiency,
                            "status": "weak",
                            "priority": "high",
                            "evidence": evidence_map.get(
                                matched_profile_skill[
                                    "name"
                                ].lower(),
                                ["profile_skill"],
                            ),
                            "reason": (
                                f"{required_skill} is "
                                "relevant to the target "
                                "job, but your current "
                                f"proficiency is only "
                                f"{proficiency:.0f}%."
                            ),
                        }
                    )

            continue

        # ----------------------------------------------------
        # Check project/certification evidence
        # ----------------------------------------------------

        matched_evidence = None

        for known_skill, evidence in evidence_map.items():

            if known_skill == required_skill.lower():

                matched_evidence = evidence
                break

        if matched_evidence:

            estimated = evidence_proficiency(
                matched_evidence
            )

            if estimated >= 60:

                evidence_only_skills.append(
                    {
                        "name": required_skill,
                        "proficiency": estimated,
                        "status": "evidence",
                        "priority": "medium",
                        "evidence": matched_evidence,
                        "reason": (
                            f"{required_skill} is relevant "
                            "to the target job and is "
                            "supported by your project or "
                            "certification evidence."
                        ),
                    }
                )

            else:

                missing_skills.append(
                    {
                        "name": required_skill,
                        "status": "weak_evidence",
                        "priority": "high",
                        "evidence": matched_evidence,
                        "reason": (
                            f"{required_skill} appears in "
                            "the target job, but your current "
                            "evidence is not strong enough "
                            "to consider you placement-ready "
                            "in this skill."
                        ),
                    }
                )

            continue

        # ----------------------------------------------------
        # Completely missing
        # ----------------------------------------------------

        missing_skills.append(
            {
                "name": required_skill,
                "status": "missing",
                "priority": "high",
                "evidence": [],
                "reason": (
                    f"{required_skill} appears to be "
                    "required by the target job but there "
                    "is currently no evidence of this skill "
                    "in your profile, projects, or "
                    "certifications."
                ),
            }
        )

    # --------------------------------------------------------
    # Overall skill score
    # --------------------------------------------------------

    if proficiency_values:

        overall_skill_score = round(
            sum(proficiency_values)
            / len(proficiency_values),
            2,
        )

    else:

        overall_skill_score = 0.0

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = []

    if weak_skills:

        weak_names = [
            item["name"]
            for item in weak_skills[:5]
        ]

        recommendations.append(
            "Prioritize improving: "
            + ", ".join(weak_names)
            + "."
        )

    if missing_skills:

        missing_names = [
            item["name"]
            for item in missing_skills[:5]
        ]

        recommendations.append(
            "Focus on these job-relevant gaps: "
            + ", ".join(missing_names)
            + "."
        )

    if evidence_only_skills:

        evidence_names = [
            item["name"]
            for item in evidence_only_skills[:5]
        ]

        recommendations.append(
            "Your projects or certifications already "
            "provide evidence for: "
            + ", ".join(evidence_names)
            + ". Add these skills to your profile with "
            "accurate proficiency levels."
        )

    if not recommendations:

        recommendations.append(
            "Continue building and documenting "
            "job-relevant skills."
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "overall_skill_score": overall_skill_score,
        "strong_skills": strong_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
        "total_profile_skills": len(
            student_skills
        ),
        "total_missing_skills": len(
            missing_skills
        ),
    }