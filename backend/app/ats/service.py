import re

from app.ats.parser import extract_text_from_pdf
from app.database.database import SessionLocal
from app.ats.models import ATSResult


# ============================================================
# Skill Knowledge Base
# ============================================================

SKILL_KEYWORDS = {
    "C": ["c"],
    "C++": ["c++", "cpp"],
    "Java": ["java"],
    "Python": ["python"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "SQL": ["sql"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Spring Boot": ["spring boot"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Azure": ["azure", "microsoft azure"],
    "AWS": ["aws", "amazon web services"],
    "GCP": ["gcp", "google cloud"],
    "Linux": ["linux"],
    "Data Structures": [
        "data structures",
        "data structure",
    ],
    "Algorithms": [
        "algorithms",
        "algorithm",
    ],
    "Machine Learning": [
        "machine learning",
        "ml",
    ],
    "Artificial Intelligence": [
        "artificial intelligence",
        "ai",
    ],
    "Deep Learning": [
        "deep learning",
    ],
    "TensorFlow": [
        "tensorflow",
    ],
    "PyTorch": [
        "pytorch",
    ],
    "OpenCV": [
        "opencv",
    ],
    "PostgreSQL": [
        "postgresql",
        "postgres",
    ],
    "MySQL": [
        "mysql",
    ],
    "MongoDB": [
        "mongodb",
        "mongo",
    ],
    "REST API": [
        "rest api",
        "restful api",
    ],
}


# ============================================================
# Resume Sections
# ============================================================

SECTION_ALIASES = {
    "skills": [
        "skills",
        "technical skills",
        "technical skill",
        "key skills",
        "core skills",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualification",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "internships",
    ],
    "projects": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
    ],
    "certifications": [
        "certifications",
        "certification",
        "certificates",
    ],
    "summary": [
        "summary",
        "profile",
        "career objective",
        "careerobjective",
        "objective",
    ],
    "achievements": [
        "achievements",
        "accomplishments",
    ],
    "languages": [
        "languages",
        "languages known",
    ],
}


# ============================================================
# Main Resume Analysis
# ============================================================

def analyze_resume(
    file_bytes: bytes,
    filename: str,
    page_count: int,
    job_description: str | None = None,
    user_id: int | None = None,
) -> dict:
    """
    Analyze a resume.

    Current capabilities:
    - PDF extraction
    - text normalization
    - section detection
    - skill extraction
    - optional job-description skill matching
    - ATS score
    - recommendations
    """

    extracted_text = extract_text_from_pdf(file_bytes)

    sections_found = detect_sections(extracted_text)

    matched_skills = extract_skills(extracted_text)

    missing_skills = []

    if job_description:
        required_skills = extract_skills(job_description)

        missing_skills = [
            skill
            for skill in required_skills
            if skill not in matched_skills
        ]

        ats_score = calculate_ats_score(
            resume_text=extracted_text,
            required_skills=required_skills,
            matched_skills=matched_skills,
            sections_found=sections_found,
        )
    else:
        ats_score = calculate_basic_ats_score(
            extracted_text,
            sections_found,
            matched_skills,
        )

    recommendations = generate_recommendations(
        extracted_text=extracted_text,
        sections_found=sections_found,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        job_description=job_description,
    )

    # ------------------------------------------------------------
    # Persist ATS result for placement-readiness integration
    # ------------------------------------------------------------

    if user_id is not None:
        try:
            if ats_score >= 80:
                performance_level = "excellent"
            elif ats_score >= 65:
                performance_level = "good"
            elif ats_score >= 50:
                performance_level = "developing"
            else:
                performance_level = "needs_improvement"

            db = SessionLocal()

            ats_result = ATSResult(
                user_id=int(user_id),
                filename=filename,
                job_description_provided=1 if job_description else 0,
                ats_score=float(ats_score),
                matched_skills_count=len(matched_skills),
                missing_skills_count=len(missing_skills),
                sections_count=len(sections_found),
                performance_level=performance_level,
            )

            db.add(ats_result)
            db.commit()
            db.close()

        except Exception:
            try:
                db.rollback()
                db.close()
            except Exception:
                pass

    return {
        "filename": filename,
        "text_length": len(extracted_text),
        "page_count": page_count,
        "extracted_text": extracted_text,
        "ats_score": ats_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "sections_found": sections_found,
        "recommendations": recommendations,
    }


# ============================================================
# Skill Extraction
# ============================================================

def extract_skills(text: str) -> list[str]:
    """
    Detect known skills in text.
    """

    normalized_text = text.lower()

    found = []

    for canonical_name, keywords in SKILL_KEYWORDS.items():

        for keyword in keywords:

            pattern = (
                r"(?<![a-z0-9+#])"
                + re.escape(keyword.lower())
                + r"(?![a-z0-9+#])"
            )

            if re.search(pattern, normalized_text):
                found.append(canonical_name)
                break

    return sorted(set(found))


# ============================================================
# Section Detection
# ============================================================

def detect_sections(text: str) -> list[str]:
    """
    Detect common resume sections using normalized text.
    """

    normalized_text = normalize_for_matching(text)

    found_sections = []

    for section_name, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            normalized_alias = normalize_for_matching(alias)

            if normalized_alias in normalized_text:
                found_sections.append(section_name)
                break

    return found_sections


def normalize_for_matching(text: str) -> str:
    """
    Normalize text specifically for keyword/section matching.

    Spaces and punctuation are removed so that:

        CAREER OBJECTIVE
        CAREEROBJECTIVE
        Career-Objective

    can all match the same keyword.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#]+",
        "",
        text,
    )

    return text


# ============================================================
# Basic ATS Score
# ============================================================

def calculate_basic_ats_score(
    resume_text: str,
    sections_found: list[str],
    matched_skills: list[str],
) -> float:
    """
    Calculate an initial ATS score when no job description
    is supplied.

    This is a baseline heuristic score.
    It is NOT an ML prediction.
    """

    score = 0.0

    # --------------------------------------------------------
    # Section completeness: 35 points
    # --------------------------------------------------------

    important_sections = {
        "skills",
        "education",
        "projects",
        "certifications",
        "summary",
        "experience",
    }

    section_score = (
        len(
            set(sections_found) & important_sections
        )
        / len(important_sections)
    ) * 35

    score += section_score

    # --------------------------------------------------------
    # Skills: 25 points
    # --------------------------------------------------------

    skill_score = min(
        len(matched_skills) / 8,
        1.0,
    ) * 25

    score += skill_score

    # --------------------------------------------------------
    # Resume content: 20 points
    # --------------------------------------------------------

    text_length = len(resume_text)

    if text_length >= 2000:
        score += 20

    elif text_length >= 1200:
        score += 15

    elif text_length >= 700:
        score += 10

    else:
        score += 5

    # --------------------------------------------------------
    # Contact information: 10 points
    # --------------------------------------------------------

    contact_score = 0

    if "@" in resume_text:
        contact_score += 5

    if re.search(
        r"\+?\d[\d\s-]{8,}",
        resume_text,
    ):
        contact_score += 5

    score += contact_score

    # --------------------------------------------------------
    # Links: 10 points
    # --------------------------------------------------------

    links = 0

    normalized_text = normalize_for_matching(resume_text)

    if "githubcom" in normalized_text:
        links += 5

    if "linkedincom" in normalized_text:
        links += 5

    score += links

    return round(
        min(score, 100),
        2,
    )


# ============================================================
# Job-Specific ATS Score
# ============================================================

def calculate_ats_score(
    resume_text: str,
    required_skills: list[str],
    matched_skills: list[str],
    sections_found: list[str],
) -> float:
    """
    Calculate job-specific ATS score.

    Weighting:

    Required skill match -> 60 points
    Resume sections      -> 20 points
    Content signals      -> 20 points
    """

    # --------------------------------------------------------
    # Required skill match
    # --------------------------------------------------------

    if required_skills:

        matched_required = len(
            set(required_skills)
            & set(matched_skills)
        )

        skill_match_score = (
            matched_required
            / len(set(required_skills))
        ) * 60

    else:
        skill_match_score = 60

    # --------------------------------------------------------
    # Section score
    # --------------------------------------------------------

    important_sections = {
        "skills",
        "education",
        "projects",
        "experience",
        "summary",
    }

    section_score = (
        len(
            set(sections_found)
            & important_sections
        )
        / len(important_sections)
    ) * 20

    # --------------------------------------------------------
    # Content signals
    # --------------------------------------------------------

    content_score = 0

    normalized_text = resume_text.lower()

    if len(resume_text) >= 1500:
        content_score += 10

    if (
        "github.com" in normalized_text
        or "github" in normalized_text
    ):
        content_score += 5

    if (
        "linkedin.com" in normalized_text
        or "linkedin" in normalized_text
    ):
        content_score += 5

    return round(
        min(
            skill_match_score
            + section_score
            + content_score,
            100,
        ),
        2,
    )


# ============================================================
# Recommendations
# ============================================================

def generate_recommendations(
    extracted_text: str,
    sections_found: list[str],
    matched_skills: list[str],
    missing_skills: list[str],
    job_description: str | None,
) -> list[str]:
    """
    Generate actionable resume recommendations.
    """

    recommendations = []

    normalized_text = extracted_text.lower()

    # --------------------------------------------------------
    # Summary / Career Objective
    # --------------------------------------------------------

    if "summary" not in sections_found:
        recommendations.append(
            "Add a concise professional summary or career objective."
        )

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    if "skills" not in sections_found:
        recommendations.append(
            "Add a clearly labeled Technical Skills section."
        )

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    if "projects" not in sections_found:
        recommendations.append(
            "Add relevant projects with technologies and measurable outcomes."
        )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    if "experience" not in sections_found:
        recommendations.append(
            "Add internships, work experience, or relevant practical experience if available."
        )

    # --------------------------------------------------------
    # Technical Skills
    # --------------------------------------------------------

    if len(matched_skills) < 5:
        recommendations.append(
            "Increase the number of relevant technical skills demonstrated through projects or experience."
        )

    # --------------------------------------------------------
    # Missing Job Skills
    # --------------------------------------------------------

    if missing_skills:
        recommendations.append(
            "Focus your preparation on the missing skills required by the target job."
        )

    # --------------------------------------------------------
    # GitHub
    # --------------------------------------------------------

    if (
        "github.com" not in normalized_text
        and "github" not in normalized_text
    ):
        recommendations.append(
            "Add a GitHub profile or relevant repository links."
        )

    # --------------------------------------------------------
    # LinkedIn
    # --------------------------------------------------------

    if (
        "linkedin.com" not in normalized_text
        and "linkedin" not in normalized_text
    ):
        recommendations.append(
            "Add your LinkedIn profile."
        )

    # --------------------------------------------------------
    # Final fallback
    # --------------------------------------------------------

    if not recommendations:
        recommendations.append(
            "Resume structure looks good. Continue improving measurable project impact and role-specific keywords."
        )

    return recommendations