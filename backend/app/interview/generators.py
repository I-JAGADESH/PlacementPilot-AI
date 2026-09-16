"""
Interview Question Generators and Realistic Company-Style Pattern Bank.

Supports all 11 interview rounds, 11 roles, 16 domains, 4 experience levels,
4 difficulty settings, and dynamic profile-aware question generation.
"""

import random
from typing import List, Dict, Any, Optional
from app.interview.schemas import InterviewQuestion


FRAMING_DISCLAIMER = "realistic company-style interview questions based on role expectations and standard interview patterns"

# Available Configuration Choices
ROLES = [
    "Software Engineer",
    "SDE",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "Data Engineer",
    "AI/ML Engineer",
    "Cloud Engineer",
    "DevOps Engineer",
    "QA Engineer",
]

EXPERIENCE_LEVELS = [
    "Student / Fresher",
    "Entry Level",
    "Intermediate",
    "Advanced",
]

INTERVIEW_ROUNDS = [
    "HR / Behavioral",
    "Aptitude Screening",
    "Technical MCQ",
    "DSA",
    "Core CS",
    "Coding",
    "Project Discussion",
    "Resume Discussion",
    "System Design",
    "Behavioral / Managerial",
    "Final HR",
]

DIFFICULTIES = [
    "Easy",
    "Medium",
    "Hard",
    "Expert",
]

DOMAINS = [
    "DSA",
    "OOP",
    "DBMS",
    "SQL",
    "Operating Systems",
    "Computer Networks",
    "Java",
    "C++",
    "Python",
    "JavaScript",
    "TypeScript",
    "React",
    "Backend/API Design",
    "Cloud",
    "AI/ML",
    "System Design",
]


# Question Templates by Round
QUESTION_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "HR / Behavioral": [
        {
            "question": "Tell me about yourself and why you are interested in this {role} position at {company}.",
            "category": "HR",
            "type": "behavioral",
            "concepts": ["Self Introduction", "Role Alignment", "Career Motivation"],
            "time": "3 mins",
        },
        {
            "question": "What are your primary technical strengths and one area you are actively working to improve?",
            "category": "HR",
            "type": "behavioral",
            "concepts": ["Self Awareness", "Continuous Learning"],
            "time": "3 mins",
        },
        {
            "question": "Where do you see your technical career progressing over the next 3 to 5 years?",
            "category": "HR",
            "type": "behavioral",
            "concepts": ["Career Goals", "Ambition"],
            "time": "2 mins",
        },
        {
            "question": "Describe a scenario where you had to quickly adapt to a sudden change in project priorities.",
            "category": "Behavioral",
            "type": "behavioral",
            "concepts": ["Adaptability", "Agility"],
            "time": "4 mins",
        },
    ],
    "Aptitude Screening": [
        {
            "question": "A team of 5 developers can complete a feature in 12 days. If 1 developer leaves after 4 days, how many total days will it take to finish the feature?",
            "category": "Quantitative",
            "type": "MCQ",
            "options": ["14 days", "16 days", "15 days", "18 days"],
            "expected": "16 days",
            "rubric": "Correct answer requires calculating total worker-days (60 worker-days). 20 done in first 4 days, 40 remaining for 4 developers = 10 more days. Total = 14 days.",
            "concepts": ["Work & Time", "Proportional Reasoning"],
            "time": "2 mins",
        },
        {
            "question": "What is the probability of picking two defective components consecutively from a batch of 10 components containing 3 defective ones without replacement?",
            "category": "Probability",
            "type": "MCQ",
            "options": ["1/15", "1/5", "3/10", "2/15"],
            "expected": "1/15",
            "rubric": "(3/10) * (2/9) = 6/90 = 1/15.",
            "concepts": ["Probability", "Combinatorics"],
            "time": "2 mins",
        },
        {
            "question": "In a code review dataset, 60% of bugs are logic errors and 40% are syntax errors. If 80% of logic errors are caught in unit tests and 90% of syntax errors are caught, what is the overall bug detection rate?",
            "category": "Logical Reasoning",
            "type": "MCQ",
            "options": ["84%", "86%", "88%", "82%"],
            "expected": "84%",
            "rubric": "(0.60 * 0.80) + (0.40 * 0.90) = 0.48 + 0.36 = 0.84 (84%).",
            "concepts": ["Data Interpretation", "Percentages"],
            "time": "2 mins",
        },
    ],
    "Technical MCQ": [
        {
            "question": "Which data structure provides average O(1) time complexity for insertion, deletion, and search operations?",
            "category": "Data Structures",
            "type": "MCQ",
            "options": ["Hash Table", "Binary Search Tree", "Linked List", "Array"],
            "expected": "Hash Table",
            "rubric": "Hash tables use hashing algorithms to map keys directly to buckets, giving average O(1) performance.",
            "concepts": ["Hashing", "Time Complexity"],
            "time": "1 min",
        },
        {
            "question": "In relational databases, which isolation level prevents dirty reads but allows non-repeatable reads?",
            "category": "DBMS",
            "type": "MCQ",
            "options": ["Read Committed", "Read Uncommitted", "Repeatable Read", "Serializable"],
            "expected": "Read Committed",
            "rubric": "Read Committed ensures transactions only read committed data, preventing dirty reads.",
            "concepts": ["ACID Properties", "Transaction Isolation"],
            "time": "1 min",
        },
        {
            "question": "Which HTTP status code signifies that the server successfully processed the request but is not returning any content?",
            "category": "Computer Networks",
            "type": "MCQ",
            "options": ["204 No Content", "200 OK", "201 Created", "304 Not Modified"],
            "expected": "204 No Content",
            "rubric": "204 No Content indicates success without response body.",
            "concepts": ["HTTP Protocols", "REST Architecture"],
            "time": "1 min",
        },
    ],
    "DSA": [
        {
            "question": "Given an unsorted array of integers, design an optimal algorithm to find the length of the longest consecutive elements sequence. Explain time and space complexity.",
            "category": "DSA",
            "type": "long_answer",
            "rubric": "Expected approach uses Hash Set for O(N) time and O(N) space. Candidate should mention starting sequence check (val - 1 not in set).",
            "concepts": ["Hash Map/Set", "Sequence Processing", "Complexity Analysis"],
            "time": "7 mins",
        },
        {
            "question": "Explain how you would detect a cycle in a directed graph vs an undirected graph. What algorithms would you apply?",
            "category": "DSA",
            "type": "long_answer",
            "rubric": "Directed: DFS with recursion stack state (3 colors) or Kahn's algorithm (indegree BFS). Undirected: DFS/BFS tracking parent pointer or Union-Find.",
            "concepts": ["Graph Traversal", "Cycle Detection", "DFS/BFS"],
            "time": "7 mins",
        },
        {
            "question": "Describe how to implement a Least Recently Used (LRU) Cache with O(1) get and put operations.",
            "category": "DSA",
            "type": "long_answer",
            "rubric": "Requires a Doubly Linked List paired with a Hash Map. Explain pointer node manipulation and hash table lookup.",
            "concepts": ["LRU Cache", "Doubly Linked List", "Hash Map"],
            "time": "8 mins",
        },
    ],
    "Core CS": [
        {
            "question": "Explain the key differences between process-level concurrency and thread-level concurrency in Operating Systems, focusing on memory sharing and context switching overhead.",
            "category": "Operating Systems",
            "type": "short_answer",
            "rubric": "Processes have separate virtual address spaces (higher context switch cost, IPC required). Threads share process memory space (cheaper context switch, requires synchronization locks).",
            "concepts": ["Virtual Memory", "Threads vs Processes", "Context Switching"],
            "time": "5 mins",
        },
        {
            "question": "Describe the TCP 3-way handshake process. What happens if the final ACK packet is lost during connection establishment?",
            "category": "Computer Networks",
            "type": "short_answer",
            "rubric": "SYN, SYN-ACK, ACK. If final ACK is lost, server stays in SYN_RECEIVED state and retransmits SYN-ACK until timeout or client sends data packet.",
            "concepts": ["TCP/IP", "Connection Management", "Reliable Transport"],
            "time": "5 mins",
        },
        {
            "question": "Explain Indexing in Relational Databases (B-Trees / B+ Trees). Why are B+ trees preferred over standard Binary Search Trees for disk storage?",
            "category": "DBMS",
            "type": "short_answer",
            "rubric": "B+ Trees have high fan-out, reducing disk I/O operations. Leaf nodes are linked, allowing efficient sequential range scans.",
            "concepts": ["B+ Trees", "Database Indexing", "Disk I/O"],
            "time": "5 mins",
        },
    ],
    "Coding": [
        {
            "question": "Write a clean function to implement String Anagram Check or Two Sum in your preferred programming language. Provide sample test cases and handle edge cases.",
            "category": "Coding",
            "type": "coding",
            "rubric": "Code quality, correct syntax, handling null/empty inputs, correct time/space complexity.",
            "concepts": ["Code Implementation", "Edge Case Handling", "Clean Code"],
            "time": "10 mins",
        },
        {
            "question": "Write a function to flatten a deeply nested array or object structure. Demonstrate recursion or stack-based iteration.",
            "category": "Coding",
            "type": "coding",
            "rubric": "Iterative or recursive implementation, proper array check, handling deep nesting without stack overflow.",
            "concepts": ["Recursion", "Data Transformation"],
            "time": "10 mins",
        },
    ],
    "Project Discussion": [
        {
            "question": "Walk me through the overall technical architecture of your project. What were the core technical challenges and how did you resolve them?",
            "category": "Project",
            "type": "project_discussion",
            "rubric": "Evaluation based on architecture clarity, personal contributions, design justification, and technical depth.",
            "concepts": ["System Architecture", "Problem Solving", "Technical Ownership"],
            "time": "8 mins",
        },
        {
            "question": "In your project, how did you handle data storage, database queries, and caching? What trade-offs did you consider?",
            "category": "Project",
            "type": "project_discussion",
            "rubric": "Database choices, normalization/denormalization trade-offs, caching strategy.",
            "concepts": ["Data Modeling", "Caching Strategies", "Trade-off Analysis"],
            "time": "6 mins",
        },
    ],
    "Resume Discussion": [
        {
            "question": "Your resume highlights expertise in declared technologies. Can you explain a complex problem you solved using these skills?",
            "category": "Resume",
            "type": "resume_discussion",
            "rubric": "Authenticity of experience, practical mastery of claimed technologies, concise communication.",
            "concepts": ["Technology Proof", "Practical Experience"],
            "time": "6 mins",
        },
        {
            "question": "Walk me through a key achievement or feature you delivered that had measurable technical or performance impact.",
            "category": "Resume",
            "type": "resume_discussion",
            "rubric": "Clarity of impact metrics, engineering depth, role accountability.",
            "concepts": ["Impact Measurement", "Engineering Rigor"],
            "time": "6 mins",
        },
    ],
    "System Design": [
        {
            "question": "Design a scalable URL Shortening Service (like TinyURL). Address high throughput read/write requirement, key generation, database storage, and caching strategy.",
            "category": "System Design",
            "type": "system_design",
            "rubric": "Requirements estimation, API design, Base62 encoding / KGS, DB choice (NoSQL vs SQL), Redis caching, load balancing.",
            "concepts": ["Scalability", "API Design", "Distributed Caching", "Database Selection"],
            "time": "12 mins",
        },
        {
            "question": "Design a Real-time Notification System that delivers push notifications, emails, and SMS alerts to millions of users.",
            "category": "System Design",
            "type": "system_design",
            "rubric": "Message queues (Kafka/RabbitMQ), worker pools, rate limiting, retry mechanisms, idempotency.",
            "concepts": ["Message Queues", "Asynchronous Processing", "Idempotency"],
            "time": "12 mins",
        },
    ],
    "Behavioral / Managerial": [
        {
            "question": "Describe a scenario where you had a strong technical disagreement with a team member or senior reviewer. How did you handle it and what was the outcome?",
            "category": "Managerial",
            "type": "behavioral",
            "rubric": "Professionalism, objective data-driven argumentation, active listening, resolution.",
            "concepts": ["Conflict Resolution", "Collaboration", "Professional Maturity"],
            "time": "5 mins",
        },
        {
            "question": "Tell me about a project or deadline where things were behind schedule. How did you prioritize tasks and communicate under pressure?",
            "category": "Managerial",
            "type": "behavioral",
            "rubric": "Prioritization, expectation management, proactive communication, execution under pressure.",
            "concepts": ["Time Management", "Prioritization", "Crisis Management"],
            "time": "5 mins",
        },
    ],
    "Final HR": [
        {
            "question": "What key strengths and work values will you bring to our team at {company}? How do you handle constructive feedback?",
            "category": "Final HR",
            "type": "behavioral",
            "concepts": ["Culture Fit", "Receptiveness to Feedback"],
            "time": "3 mins",
        },
        {
            "question": "Do you have any questions for us regarding the engineering culture, technology roadmap, or team expectations at {company}?",
            "category": "Final HR",
            "type": "behavioral",
            "concepts": ["Engagement", "Company Interest"],
            "time": "3 mins",
        },
    ],
}


def generate_interview_questions(
    round_type: str = "Technical MCQ",
    role: str = "Software Engineer",
    experience_level: str = "Entry Level",
    difficulty: str = "Medium",
    domain: Optional[str] = "DSA",
    company: str = "Generic",
    profile_context: Optional[Dict[str, Any]] = None,
    count: int = 5,
) -> List[InterviewQuestion]:
    """
    Generate realistic company-style interview questions tailored to the round, role,
    experience level, difficulty, domain, and profile context.
    """
    questions: List[InterviewQuestion] = []
    q_id = 1

    profile_context = profile_context or {}
    user_projects = profile_context.get("projects", [])
    user_skills = profile_context.get("skills", [])
    user_certs = profile_context.get("certifications", [])
    user_weaknesses = profile_context.get("weak_topics", [])

    # Special Profile-Aware Generation for Project Discussion
    if round_type == "Project Discussion" and user_projects:
        for p in user_projects[:count]:
            p_title = p.get("title", "Recent Project")
            p_techs = ", ".join(p.get("technologies", [])) or "software stack"
            p_desc = p.get("description", "")
            
            q_text = (
                f"In your project '{p_title}' built with {p_techs}, walk me through the key architectural decisions "
                f"and design trade-offs you made. {(' Specifically: ' + p_desc[:120] + '...') if p_desc else ''}"
            )
            questions.append(
                InterviewQuestion(
                    question_id=q_id,
                    question=q_text,
                    category="Project Discussion",
                    difficulty=difficulty,
                    company=company,
                    round=round_type,
                    role=role,
                    experience_level=experience_level,
                    domain=domain or "Software Architecture",
                    question_type="project_discussion",
                    expected_answer_type="long_answer",
                    rubric=f"Evaluate project depth, architectural decisions, and mastery of technologies ({p_techs}).",
                    concepts_tested=["System Architecture", "Design Trade-offs", "Tech Stack Mastery"],
                    estimated_time="8 mins",
                    profile_relevance={"project_title": p_title, "technologies": p_techs},
                    disclaimer=FRAMING_DISCLAIMER,
                )
            )
            q_id += 1

    # Special Profile-Aware Generation for Resume Discussion
    elif round_type == "Resume Discussion" and (user_skills or user_certs):
        skills_str = ", ".join([s["name"] for s in user_skills[:4]]) if user_skills else "declared skills"
        certs_str = ", ".join([c["name"] for c in user_certs[:2]]) if user_certs else ""
        
        q_text = (
            f"Your resume indicates proficiency in {skills_str}. "
            f"Explain a complex scenario where you applied these skills to optimize performance or resolve a production issue."
            f"{(' Also touch upon your certification: ' + certs_str + '.') if certs_str else ''}"
        )
        questions.append(
            InterviewQuestion(
                question_id=q_id,
                question=q_text,
                category="Resume Discussion",
                difficulty=difficulty,
                company=company,
                round=round_type,
                role=role,
                experience_level=experience_level,
                domain=domain or "Technical Expertise",
                question_type="resume_discussion",
                expected_answer_type="long_answer",
                rubric=f"Evaluate candidate's mastery of listed skills ({skills_str}) and problem solving.",
                concepts_tested=["Resume Claims Defense", "Skill Mastery", "Practical Application"],
                estimated_time="6 mins",
                profile_relevance={"skills": skills_str, "certifications": certs_str},
                disclaimer=FRAMING_DISCLAIMER,
            )
        )
        q_id += 1

    # Weakness Targeting Question Injection if present
    if user_weaknesses and len(questions) < count:
        target_weakness = user_weaknesses[0]
        q_text = (
            f"[Focus Area: {target_weakness}] Based on past assessment performance, "
            f"explain the fundamental concepts of {target_weakness} and how you would solve common edge-case challenges in it."
        )
        questions.append(
            InterviewQuestion(
                question_id=q_id,
                question=q_text,
                category=target_weakness,
                difficulty=difficulty,
                company=company,
                round=round_type,
                role=role,
                experience_level=experience_level,
                domain=target_weakness,
                question_type="short_answer",
                expected_answer_type="short_answer",
                rubric=f"Verify candidate has overcome weakness in {target_weakness}.",
                concepts_tested=[target_weakness, "Targeted Remediation"],
                estimated_time="5 mins",
                profile_relevance={"weakness_target": target_weakness},
                disclaimer=FRAMING_DISCLAIMER,
            )
        )
        q_id += 1

    # Fill remaining required question slots from pattern templates
    round_templates = QUESTION_TEMPLATES.get(round_type, QUESTION_TEMPLATES["Technical MCQ"])
    
    while len(questions) < count:
        tmpl = round_templates[(len(questions)) % len(round_templates)]
        raw_q = tmpl["question"].format(role=role, company=company)
        
        q_obj = InterviewQuestion(
            question_id=q_id,
            question=raw_q,
            category=tmpl.get("category", domain or "General"),
            difficulty=difficulty,
            company=company,
            round=round_type,
            role=role,
            experience_level=experience_level,
            domain=domain or tmpl.get("category", "General"),
            question_type=tmpl.get("type", "short_answer"),
            options=tmpl.get("options"),
            expected_answer_type=tmpl.get("expected"),
            rubric=tmpl.get("rubric", "Evaluate technical clarity, accuracy, and depth."),
            concepts_tested=tmpl.get("concepts", ["Core Knowledge"]),
            estimated_time=tmpl.get("time", "5 mins"),
            disclaimer=FRAMING_DISCLAIMER,
        )
        questions.append(q_obj)
        q_id += 1

    return questions
