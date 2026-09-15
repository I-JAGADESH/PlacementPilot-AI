from typing import Dict, List

from sqlalchemy.orm import Session

from app.profile.models import (
    StudentProfile,
    StudentSkill,
    StudentProject,
    StudentCertification,
)
from app.roadmap.schemas import RoadmapTask, RoadmapResponse


# ============================================================
# PERSONALIZED TRAINING KNOWLEDGE BASE
# ============================================================

SKILL_TOPICS: Dict[str, List[str]] = {
    "C++": [
        "C++ Fundamentals",
        "OOP",
        "STL",
        "Pointers and References",
        "Problem Solving",
        "Interview Practice",
    ],
    "Python": [
        "Python Fundamentals",
        "Collections",
        "Functions and Modules",
        "OOP",
        "Exception Handling",
        "Interview Practice",
    ],
    "Java": [
        "Java Fundamentals",
        "OOP",
        "Collections Framework",
        "Exception Handling",
        "Multithreading",
        "Interview Practice",
    ],
    "Data Structures": [
        "Arrays",
        "Strings",
        "Linked Lists",
        "Stacks and Queues",
        "Trees",
        "Graphs",
        "Hashing",
        "Problem Solving",
    ],
    "Algorithms": [
        "Searching",
        "Sorting",
        "Binary Search",
        "Greedy Algorithms",
        "Dynamic Programming",
        "Graph Algorithms",
        "Complexity Analysis",
    ],
    "SQL": [
        "SELECT Queries",
        "Filtering and Sorting",
        "Joins",
        "Aggregate Functions",
        "Subqueries",
        "Indexes",
        "Transactions",
        "SQL Interview Practice",
    ],
    "DBMS": [
        "ER Model",
        "Normalization",
        "Keys and Constraints",
        "Transactions",
        "ACID Properties",
        "Indexing",
        "Concurrency Control",
        "DBMS Interview Practice",
    ],
    "Git": [
        "Git Basics",
        "Branches",
        "Merge and Rebase",
        "Conflict Resolution",
        "Remote Repositories",
        "Practical Git Workflow",
    ],
    "GitHub": [
        "Repositories",
        "README Documentation",
        "Issues",
        "Pull Requests",
        "GitHub Actions",
        "Project Presentation",
    ],
    "Docker": [
        "Containers",
        "Images",
        "Dockerfile",
        "Docker Compose",
        "Container Networking",
        "Deployment Practice",
    ],
    "REST API": [
        "HTTP Methods",
        "REST Principles",
        "Request and Response",
        "Status Codes",
        "Authentication",
        "API Design Practice",
    ],
    "FastAPI": [
        "Routing",
        "Pydantic",
        "Dependency Injection",
        "Authentication",
        "Database Integration",
        "API Project Practice",
    ],
    "React": [
        "Components",
        "Props and State",
        "Hooks",
        "Forms",
        "API Integration",
        "React Project Practice",
    ],
    "AWS": [
        "Cloud Fundamentals",
        "EC2",
        "S3",
        "IAM",
        "RDS",
        "Deployment Practice",
    ],
    "Azure": [
        "Azure Fundamentals",
        "Virtual Machines",
        "Storage",
        "App Service",
        "Identity and Access",
        "Deployment Practice",
    ],
}


SUPPORTED_SKILLS = list(SKILL_TOPICS.keys())


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_required_skills(job_description: str) -> List[str]:
    """
    Detect supported skills from a job description.

    Matching is case-insensitive and uses word/phrase presence.
    """

    text = (job_description or "").lower()

    found: List[str] = []

    for skill in SUPPORTED_SKILLS:
        if skill.lower() in text:
            found.append(skill)

    return found


# ============================================================
# PROFICIENCY ANALYSIS
# ============================================================

def get_priority(proficiency: float) -> str:
    if proficiency < 40:
        return "critical"

    if proficiency < 60:
        return "high"

    if proficiency < 75:
        return "medium"

    return "low"


def get_duration(proficiency: float) -> int:
    """
    Estimate training duration from current proficiency.
    """

    if proficiency < 40:
        return 7

    if proficiency < 60:
        return 5

    if proficiency < 75:
        return 3

    return 2


def get_training_mode(proficiency: float) -> str:
    if proficiency < 40:
        return "learn_and_practice"

    if proficiency < 60:
        return "practice_and_assess"

    if proficiency < 75:
        return "strengthen_and_assess"

    return "interview_and_maintain"


# ============================================================
# TOPIC SELECTION
# ============================================================

def select_topics(
    skill: str,
    proficiency: float,
) -> List[str]:
    """
    Select topics based on the student's current proficiency.

    Lower proficiency receives more fundamentals.
    Higher proficiency moves faster toward interview preparation.
    """

    topics = SKILL_TOPICS.get(
        skill,
        [
            f"{skill} Fundamentals",
            f"{skill} Practical Usage",
            f"{skill} Problem Solving",
            f"{skill} Interview Practice",
        ],
    )

    if proficiency < 40:
        return topics[:5]

    if proficiency < 60:
        return topics[1:6]

    if proficiency < 75:
        return topics[2:6]

    return topics[-3:]


# ============================================================
# EVIDENCE ANALYSIS
# ============================================================

def build_evidence(
    skill_name: str,
    projects: List[StudentProject],
    certifications: List[StudentCertification],
) -> List[str]:
    """
    Find basic evidence that the student has used a skill.
    """

    evidence: List[str] = []

    skill_lower = skill_name.lower()

    for project in projects:
        technologies = getattr(project, "technologies", None) or ""
        description = getattr(project, "description", None) or ""
        project_text = f"{technologies} {description}".lower()

        if skill_lower in project_text:
            evidence.append(
                f"Project: {project.title}"
            )

    for certification in certifications:
        cert_text = (
            f"{getattr(certification, 'name', '')} "
            f"{getattr(certification, 'issuer', '')}"
        ).lower()

        if skill_lower in cert_text:
            evidence.append(
                f"Certification: {certification.name}"
            )

    return evidence[:5]


# ============================================================
# TRAINING TASK CREATION
# ============================================================

def create_training_task(
    skill: str,
    proficiency: float,
    projects: List[StudentProject],
    certifications: List[StudentCertification],
) -> RoadmapTask:

    priority = get_priority(proficiency)
    duration = get_duration(proficiency)
    mode = get_training_mode(proficiency)

    topics = select_topics(
        skill=skill,
        proficiency=proficiency,
    )

    evidence = build_evidence(
        skill_name=skill,
        projects=projects,
        certifications=certifications,
    )

    if proficiency <= 0:
        reason = (
            f"{skill} is required for the target role but is "
            "not currently present in your profile. Start with "
            "fundamentals and build practical ability."
        )

    elif proficiency < 40:
        reason = (
            f"Your current {skill} proficiency is "
            f"{proficiency:.0f}%. This is a major skill gap, "
            "so fundamentals and guided practice should be prioritized."
        )

    elif proficiency < 60:
        reason = (
            f"Your current {skill} proficiency is "
            f"{proficiency:.0f}%. Strengthen the core concepts "
            "and solve practical problems."
        )

    elif proficiency < 75:
        reason = (
            f"Your current {skill} proficiency is "
            f"{proficiency:.0f}%. Focus on advanced practice, "
            "assessment, and interview questions."
        )

    else:
        reason = (
            f"Your current {skill} proficiency is "
            f"{proficiency:.0f}%. Maintain the skill and focus "
            "on interview-level application."
        )

    if evidence:
        reason += (
            " Existing profile evidence: "
            + ", ".join(evidence)
            + "."
        )

    reason += f" Recommended mode: {mode.replace('_', ' ')}."

    return RoadmapTask(
        skill=skill,
        priority=priority,
        duration_days=duration,
        topics=topics,
        reason=reason,
    )


# ============================================================
# DAILY TRAINING PLAN
# ============================================================

def build_daily_plan(
    tasks: List[RoadmapTask],
) -> List[str]:

    daily_plan: List[str] = []
    day_number = 1

    for task in tasks:

        for topic in task.topics:

            if day_number > sum(
                current.duration_days
                for current in tasks
            ):
                break

            daily_plan.append(
                f"Day {day_number}: "
                f"{task.skill} — {topic}"
            )

            day_number += 1

    return daily_plan


# ============================================================
# RECOMMENDATIONS
# ============================================================

def build_recommendations(
    tasks: List[RoadmapTask],
    projects: List[StudentProject],
    certifications: List[StudentCertification],
    target_company: str | None,
) -> List[str]:

    recommendations: List[str] = []

    critical = [
        task.skill
        for task in tasks
        if task.priority == "critical"
    ]

    high = [
        task.skill
        for task in tasks
        if task.priority == "high"
    ]

    medium = [
        task.skill
        for task in tasks
        if task.priority == "medium"
    ]

    if critical:
        recommendations.append(
            "Your biggest gaps are: "
            + ", ".join(critical[:5])
            + ". Start these before lower-priority skills."
        )

    if high:
        recommendations.append(
            "Next strengthen: "
            + ", ".join(high[:5])
            + " through focused practice and assessments."
        )

    if medium:
        recommendations.append(
            "After the major gaps, strengthen: "
            + ", ".join(medium[:5])
            + "."
        )

    if projects:
        recommendations.append(
            "Use your existing projects as practical evidence "
            "while learning the required skills."
        )
    else:
        recommendations.append(
            "Build at least one practical project demonstrating "
            "your highest-priority skill."
        )

    if certifications:
        recommendations.append(
            "Use relevant certifications as supporting evidence, "
            "but prioritize demonstrated project and assessment ability."
        )

    if target_company:
        recommendations.append(
            f"Align your preparation with the expectations of "
            f"{target_company} and your target role."
        )

    if not recommendations:
        recommendations.append(
            "Continue practicing job-relevant skills and "
            "complete regular assessments."
        )

    return recommendations[:6]


# ============================================================
# ROADMAP GENERATION
# ============================================================

def generate_roadmap(
    db: Session,
    user_id: int,
    job_description: str,
) -> RoadmapResponse:

    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == user_id)
        .first()
    )

    if not profile:
        raise ValueError("Student profile not found")

    skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.profile_id == profile.id)
        .all()
    )

    projects = (
        db.query(StudentProject)
        .filter(StudentProject.profile_id == profile.id)
        .all()
    )

    certifications = (
        db.query(StudentCertification)
        .filter(StudentCertification.profile_id == profile.id)
        .all()
    )

    required_skills = extract_required_skills(
        job_description
    )

    profile_skill_map = {
        skill.name.lower(): skill
        for skill in skills
    }

    tasks: List[RoadmapTask] = []

    for required_skill in required_skills:

        current_skill = profile_skill_map.get(
            required_skill.lower()
        )

        if current_skill:
            proficiency = float(
                current_skill.proficiency or 0
            )
        else:
            proficiency = 0.0

        tasks.append(
            create_training_task(
                skill=required_skill,
                proficiency=proficiency,
                projects=projects,
                certifications=certifications,
            )
        )

    # If the JD contains no supported skills, use the student's
    # weakest profile skills to still provide useful training.
    if not tasks:

        weakest_skills = sorted(
            skills,
            key=lambda skill: float(
                skill.proficiency or 0
            ),
        )

        for skill in weakest_skills[:5]:

            proficiency = float(
                skill.proficiency or 0
            )

            tasks.append(
                create_training_task(
                    skill=skill.name,
                    proficiency=proficiency,
                    projects=projects,
                    certifications=certifications,
                )
            )

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    tasks.sort(
        key=lambda task: priority_order.get(
            task.priority,
            4,
        )
    )

    total_days = sum(
        task.duration_days
        for task in tasks
    )

    if required_skills:

        score_values = []

        for required_skill in required_skills:

            profile_skill = profile_skill_map.get(
                required_skill.lower()
            )

            if profile_skill:
                score_values.append(
                    float(
                        profile_skill.proficiency or 0
                    )
                )
            else:
                score_values.append(0.0)

        overall_score = round(
            sum(score_values)
            / len(score_values),
            2,
        )

    elif skills:

        overall_score = round(
            sum(
                float(skill.proficiency or 0)
                for skill in skills
            )
            / len(skills),
            2,
        )

    else:
        overall_score = 0.0

    target_role = (
        profile.target_role
        if profile.target_role
        else "Software Engineer"
    )

    target_company = (
        profile.target_company
        if profile.target_company
        else None
    )

    daily_plan = build_daily_plan(tasks)

    recommendations = build_recommendations(
        tasks=tasks,
        projects=projects,
        certifications=certifications,
        target_company=target_company,
    )

    return RoadmapResponse(
        target_role=target_role,
        overall_skill_score=overall_score,
        total_days=total_days,
        tasks=tasks,
        daily_plan=daily_plan,
        recommendations=recommendations,
    )
