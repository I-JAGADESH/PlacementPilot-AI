from typing import Dict, List


TRAINING_CONTENT: Dict[str, List[dict]] = {
    "Algorithms": [
        {
            "topic": "Searching",
            "explanation": "Learn how to efficiently locate elements in collections using linear and binary search techniques.",
            "key_points": [
                "Linear Search",
                "Binary Search",
                "Time Complexity",
                "Sorted vs Unsorted Data",
            ],
            "practice_questions": [
                "What is the time complexity of linear search?",
                "When can binary search be used?",
                "Implement binary search for a sorted array.",
            ],
        },
        {
            "topic": "Sorting",
            "explanation": "Understand common sorting algorithms and how their performance differs.",
            "key_points": [
                "Bubble Sort",
                "Selection Sort",
                "Insertion Sort",
                "Merge Sort",
                "Quick Sort",
            ],
            "practice_questions": [
                "Compare merge sort and quick sort.",
                "What is the average time complexity of quick sort?",
                "Implement merge sort.",
            ],
        },
        {
            "topic": "Binary Search",
            "explanation": "Use divide-and-conquer to search sorted data efficiently.",
            "key_points": [
                "Search Space",
                "Midpoint Calculation",
                "Boundary Conditions",
                "O(log n) Complexity",
            ],
            "practice_questions": [
                "Find the first occurrence of a target using binary search.",
                "How do you avoid overflow when calculating mid?",
                "Solve a binary-search-on-answer problem.",
            ],
        },
        {
            "topic": "Greedy Algorithms",
            "explanation": "Learn how to build solutions by making locally optimal choices.",
            "key_points": [
                "Greedy Choice",
                "Optimal Substructure",
                "Activity Selection",
                "Fractional Knapsack",
            ],
            "practice_questions": [
                "What is the greedy-choice property?",
                "Solve the activity selection problem.",
                "When does a greedy solution fail?",
            ],
        },
        {
            "topic": "Dynamic Programming",
            "explanation": "Solve overlapping subproblems efficiently using memoization or tabulation.",
            "key_points": [
                "Overlapping Subproblems",
                "Optimal Substructure",
                "Memoization",
                "Tabulation",
            ],
            "practice_questions": [
                "Explain memoization and tabulation.",
                "Solve the 0/1 knapsack problem.",
                "Find the longest common subsequence.",
            ],
        },
    ],
    "Git": [
        {
            "topic": "Git Basics",
            "explanation": "Learn the fundamental Git workflow for tracking source code changes.",
            "key_points": [
                "git init",
                "git add",
                "git commit",
                "git status",
                "git log",
            ],
            "practice_questions": [
                "What is Git?",
                "What is the difference between git add and git commit?",
                "Create a repository and make your first commit.",
            ],
        },
        {
            "topic": "Branches",
            "explanation": "Use branches to develop features independently without affecting the main codebase.",
            "key_points": [
                "Creating Branches",
                "Switching Branches",
                "Merging",
                "Branch Strategy",
            ],
            "practice_questions": [
                "Why are Git branches useful?",
                "Create and switch to a feature branch.",
                "Merge a feature branch into main.",
            ],
        },
        {
            "topic": "Merge and Rebase",
            "explanation": "Understand two common ways to integrate changes from different branches.",
            "key_points": [
                "git merge",
                "git rebase",
                "Commit History",
                "When to Use Each",
            ],
            "practice_questions": [
                "What is the difference between merge and rebase?",
                "When should you avoid rebasing shared branches?",
                "Rebase a feature branch onto main.",
            ],
        },
        {
            "topic": "Conflict Resolution",
            "explanation": "Learn how to identify and resolve conflicts when Git cannot automatically combine changes.",
            "key_points": [
                "Conflict Markers",
                "Choosing Changes",
                "git add",
                "git commit",
            ],
            "practice_questions": [
                "What causes a Git merge conflict?",
                "How do you resolve a merge conflict?",
                "What should you do after resolving a conflict?",
            ],
        },
        {
            "topic": "Remote Repositories",
            "explanation": "Work with remote repositories to share code and collaborate with other developers.",
            "key_points": [
                "git remote",
                "git clone",
                "git push",
                "git pull",
                "git fetch",
            ],
            "practice_questions": [
                "What is a remote repository?",
                "Explain git fetch vs git pull.",
                "Push a local project to GitHub.",
            ],
        },
    ],
    "GitHub": [
        {
            "topic": "Repositories",
            "explanation": "Understand how GitHub repositories organize and host software projects.",
            "key_points": [
                "Public Repositories",
                "Private Repositories",
                "README",
                "Repository Settings",
            ],
            "practice_questions": [
                "What is a GitHub repository?",
                "What is the purpose of a README?",
                "Create a repository and push a project.",
            ],
        },
        {
            "topic": "README Documentation",
            "explanation": "Create clear project documentation that helps recruiters and developers understand your work.",
            "key_points": [
                "Project Overview",
                "Features",
                "Tech Stack",
                "Installation",
                "Usage",
            ],
            "practice_questions": [
                "What should a good project README contain?",
                "Write a README for one of your projects.",
                "Why is documentation important in software projects?",
            ],
        },
        {
            "topic": "Issues",
            "explanation": "Use GitHub Issues to track bugs, improvements, tasks, and feature requests.",
            "key_points": [
                "Bug Reports",
                "Feature Requests",
                "Labels",
                "Assignments",
            ],
            "practice_questions": [
                "What are GitHub Issues?",
                "Create a bug issue with useful details.",
                "How can labels improve issue management?",
            ],
        },
        {
            "topic": "Pull Requests",
            "explanation": "Learn how developers propose, review, and merge code changes collaboratively.",
            "key_points": [
                "Creating Pull Requests",
                "Code Review",
                "Review Comments",
                "Merge",
            ],
            "practice_questions": [
                "What is a pull request?",
                "Why is code review important?",
                "Create a pull request from a feature branch.",
            ],
        },
        {
            "topic": "GitHub Actions",
            "explanation": "Understand basic CI/CD automation using workflows triggered by repository events.",
            "key_points": [
                "Workflows",
                "Triggers",
                "Jobs",
                "Steps",
                "Automation",
            ],
            "practice_questions": [
                "What is GitHub Actions?",
                "What is a workflow?",
                "Create a simple workflow that runs tests.",
            ],
        },
    ],
    "REST API": [
        {
            "topic": "HTTP Methods",
            "explanation": "Understand how HTTP methods represent operations performed on API resources.",
            "key_points": [
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            ],
            "practice_questions": [
                "When should GET be used?",
                "What is the difference between PUT and PATCH?",
                "Design CRUD endpoints for a student resource.",
            ],
        },
        {
            "topic": "REST Principles",
            "explanation": "Learn the architectural principles behind RESTful web services.",
            "key_points": [
                "Resources",
                "Statelessness",
                "Uniform Interface",
                "Client-Server Architecture",
            ],
            "practice_questions": [
                "What does REST stand for?",
                "What does stateless mean in REST?",
                "Design a REST API for an interview platform.",
            ],
        },
        {
            "topic": "Request and Response",
            "explanation": "Understand how clients send data to APIs and how servers return structured responses.",
            "key_points": [
                "Headers",
                "Query Parameters",
                "Path Parameters",
                "Request Body",
                "JSON",
            ],
            "practice_questions": [
                "What is the purpose of an HTTP header?",
                "Compare path parameters and query parameters.",
                "Create a JSON request body for a user registration API.",
            ],
        },
        {
            "topic": "Status Codes",
            "explanation": "Use HTTP status codes to communicate the result of an API operation.",
            "key_points": [
                "200 OK",
                "201 Created",
                "400 Bad Request",
                "401 Unauthorized",
                "404 Not Found",
                "500 Server Error",
            ],
            "practice_questions": [
                "When should an API return 201?",
                "What is the difference between 401 and 403?",
                "Which status code represents a missing resource?",
            ],
        },
        {
            "topic": "Authentication",
            "explanation": "Learn common techniques for protecting APIs and identifying users.",
            "key_points": [
                "JWT",
                "Bearer Tokens",
                "OAuth",
                "Authentication vs Authorization",
            ],
            "practice_questions": [
                "What is JWT authentication?",
                "Differentiate authentication and authorization.",
                "Explain how a bearer token is sent to an API.",
            ],
        },
    ],
    "Data Structures": [
        {
            "topic": "Strings",
            "explanation": "Practice common string manipulation and pattern-processing techniques.",
            "key_points": [
                "Traversal",
                "Frequency Counting",
                "Two Pointers",
                "Sliding Window",
            ],
            "practice_questions": [
                "Check whether a string is a palindrome.",
                "Find the first non-repeating character.",
                "Solve a sliding-window string problem.",
            ],
        },
        {
            "topic": "Linked Lists",
            "explanation": "Understand dynamically connected nodes and common linked-list operations.",
            "key_points": [
                "Node Structure",
                "Insertion",
                "Deletion",
                "Traversal",
                "Two Pointers",
            ],
            "practice_questions": [
                "Reverse a linked list.",
                "Detect a cycle in a linked list.",
                "Find the middle node.",
            ],
        },
        {
            "topic": "Stacks and Queues",
            "explanation": "Learn LIFO and FIFO data structures and their common applications.",
            "key_points": [
                "Stack",
                "Queue",
                "Deque",
                "LIFO",
                "FIFO",
            ],
            "practice_questions": [
                "Implement a stack using an array.",
                "Implement a queue using two stacks.",
                "Solve the valid-parentheses problem.",
            ],
        },
        {
            "topic": "Trees",
            "explanation": "Understand hierarchical data structures and tree traversal techniques.",
            "key_points": [
                "Binary Trees",
                "BST",
                "DFS",
                "BFS",
                "Tree Traversals",
            ],
            "practice_questions": [
                "Implement inorder traversal.",
                "What is the difference between a binary tree and BST?",
                "Find the height of a binary tree.",
            ],
        },
        {
            "topic": "Graphs",
            "explanation": "Learn how to represent and traverse relationships between connected entities.",
            "key_points": [
                "Adjacency List",
                "Adjacency Matrix",
                "BFS",
                "DFS",
                "Shortest Path",
            ],
            "practice_questions": [
                "Implement BFS for a graph.",
                "Implement DFS for a graph.",
                "When would you use an adjacency list?",
            ],
        },
    ],
    "Python": [
        {
            "topic": "Functions and Modules",
            "explanation": "Organize Python programs using reusable functions and modules.",
            "key_points": [
                "Functions",
                "Parameters",
                "Return Values",
                "Modules",
                "Imports",
            ],
            "practice_questions": [
                "What is the difference between a parameter and argument?",
                "Create a reusable Python module.",
                "Explain Python import statements.",
            ],
        },
        {
            "topic": "OOP",
            "explanation": "Use classes and objects to model reusable software components.",
            "key_points": [
                "Classes",
                "Objects",
                "Inheritance",
                "Encapsulation",
                "Polymorphism",
            ],
            "practice_questions": [
                "Explain inheritance in Python.",
                "Create a class with constructor and methods.",
                "What is polymorphism?",
            ],
        },
        {
            "topic": "Exception Handling",
            "explanation": "Handle runtime errors gracefully using Python's exception-handling mechanisms.",
            "key_points": [
                "try",
                "except",
                "else",
                "finally",
                "raise",
            ],
            "practice_questions": [
                "Why is exception handling important?",
                "Explain try, except, else and finally.",
                "Create a custom exception.",
            ],
        },
        {
            "topic": "Interview Practice",
            "explanation": "Apply Python concepts to common technical interview questions.",
            "key_points": [
                "Lists",
                "Dictionaries",
                "Functions",
                "OOP",
                "Problem Solving",
            ],
            "practice_questions": [
                "Explain list vs tuple.",
                "How does a Python dictionary work conceptually?",
                "Solve a coding problem using Python.",
            ],
        },
    ],
    "SQL": [
        {
            "topic": "Joins",
            "explanation": "Combine related records from multiple database tables.",
            "key_points": [
                "INNER JOIN",
                "LEFT JOIN",
                "RIGHT JOIN",
                "FULL JOIN",
            ],
            "practice_questions": [
                "Explain INNER JOIN vs LEFT JOIN.",
                "Write a query joining students and departments.",
                "When would you use a LEFT JOIN?",
            ],
        },
        {
            "topic": "Aggregate Functions",
            "explanation": "Summarize groups of records using SQL aggregate functions.",
            "key_points": [
                "COUNT",
                "SUM",
                "AVG",
                "MIN",
                "MAX",
                "GROUP BY",
            ],
            "practice_questions": [
                "Find the average salary by department.",
                "Explain GROUP BY.",
                "What is the difference between WHERE and HAVING?",
            ],
        },
        {
            "topic": "Subqueries",
            "explanation": "Use queries inside other queries to solve multi-step database problems.",
            "key_points": [
                "Nested Queries",
                "Scalar Subqueries",
                "IN",
                "EXISTS",
            ],
            "practice_questions": [
                "What is a subquery?",
                "Write a query using EXISTS.",
                "Find employees earning above the average salary.",
            ],
        },
        {
            "topic": "Indexes",
            "explanation": "Understand how indexes can improve database query performance.",
            "key_points": [
                "Index Structure",
                "Query Performance",
                "Primary Key",
                "Trade-offs",
            ],
            "practice_questions": [
                "What is a database index?",
                "Why can too many indexes be harmful?",
                "When should an index be created?",
            ],
        },
    ],
    "React": [
        {
            "topic": "Hooks",
            "explanation": "Use React Hooks to manage state and component behavior in functional components.",
            "key_points": [
                "useState",
                "useEffect",
                "useMemo",
                "useCallback",
            ],
            "practice_questions": [
                "Explain useState.",
                "When does useEffect run?",
                "Build a component using useState and useEffect.",
            ],
        },
        {
            "topic": "Forms",
            "explanation": "Build controlled forms and handle user input in React applications.",
            "key_points": [
                "Controlled Inputs",
                "Form State",
                "Validation",
                "Submit Handling",
            ],
            "practice_questions": [
                "What is a controlled component?",
                "Create a login form in React.",
                "How would you validate form input?",
            ],
        },
        {
            "topic": "API Integration",
            "explanation": "Connect React applications to backend APIs using HTTP clients.",
            "key_points": [
                "Axios",
                "Fetch",
                "Loading State",
                "Error Handling",
            ],
            "practice_questions": [
                "How do you call an API from React?",
                "How should loading and error states be handled?",
                "Connect a React page to a REST API.",
            ],
        },
        {
            "topic": "React Project Practice",
            "explanation": "Apply React concepts by building a complete small application.",
            "key_points": [
                "Components",
                "Routing",
                "State",
                "API Integration",
                "Reusable UI",
            ],
            "practice_questions": [
                "Build a small dashboard using React.",
                "Explain component reusability.",
                "Add routing to a React project.",
            ],
        },
    ],
    "C++": [
        {
            "topic": "Pointers and References",
            "explanation": "Understand memory addresses, pointers, references, and their practical use in C++.",
            "key_points": [
                "Pointers",
                "References",
                "Dereferencing",
                "Memory",
            ],
            "practice_questions": [
                "What is a pointer?",
                "What is the difference between pointer and reference?",
                "Swap two values using references.",
            ],
        },
        {
            "topic": "Problem Solving",
            "explanation": "Apply C++ data structures and algorithms to coding problems.",
            "key_points": [
                "STL",
                "Complexity",
                "Arrays",
                "Strings",
                "Problem Decomposition",
            ],
            "practice_questions": [
                "Solve an array-based coding problem.",
                "Explain time and space complexity.",
                "Use STL to solve a coding problem.",
            ],
        },
        {
            "topic": "Interview Practice",
            "explanation": "Review common C++ concepts frequently discussed in software interviews.",
            "key_points": [
                "OOP",
                "STL",
                "Pointers",
                "Memory",
                "Complexity",
            ],
            "practice_questions": [
                "Explain virtual functions.",
                "What is the STL?",
                "Explain stack vs heap memory.",
            ],
        },
    ],
    "Java": [
        {
            "topic": "Exception Handling",
            "explanation": "Handle exceptional conditions using Java's exception hierarchy and handling mechanisms.",
            "key_points": [
                "try",
                "catch",
                "finally",
                "throw",
                "throws",
            ],
            "practice_questions": [
                "Explain checked vs unchecked exceptions.",
                "What is the difference between throw and throws?",
                "Create a custom exception.",
            ],
        },
        {
            "topic": "Multithreading",
            "explanation": "Understand how Java applications can execute multiple threads concurrently.",
            "key_points": [
                "Thread",
                "Runnable",
                "Synchronization",
                "Concurrency",
            ],
            "practice_questions": [
                "How can a thread be created in Java?",
                "What is synchronization?",
                "Explain race conditions.",
            ],
        },
        {
            "topic": "Interview Practice",
            "explanation": "Review core Java concepts and practice explaining them clearly in interviews.",
            "key_points": [
                "OOP",
                "Collections",
                "Exceptions",
                "Threads",
                "JVM",
            ],
            "practice_questions": [
                "Explain JVM, JRE and JDK.",
                "Compare ArrayList and LinkedList.",
                "Explain Java's object-oriented principles.",
            ],
        },
    ],
}


def get_training_content(skill: str) -> List[dict]:
    """Return training content for a skill."""
    if skill in TRAINING_CONTENT:
        return TRAINING_CONTENT[skill]

    normalized = skill.strip().lower()

    for skill_name, topics in TRAINING_CONTENT.items():
        if skill_name.lower() == normalized:
            return topics

    return []


def build_training_response(
    skill: str,
    completed_topics: List[str],
) -> dict:
    """Build the training response with completion progress."""
    topics = get_training_content(skill)

    completed_set = {
        topic.strip().lower()
        for topic in completed_topics
    }

    completed_count = sum(
        1
        for topic in topics
        if topic["topic"].strip().lower() in completed_set
    )

    total_topics = len(topics)

    progress = (
        round((completed_count / total_topics) * 100, 2)
        if total_topics
        else 0.0
    )

    return {
        "skill": skill,
        "total_topics": total_topics,
        "completed_topics": completed_count,
        "progress_percentage": progress,
        "topics": [
            {
                "skill": skill,
                "topic": topic["topic"],
                "explanation": topic["explanation"],
                "key_points": topic["key_points"],
                "practice_questions": topic["practice_questions"],
            }
            for topic in topics
        ],
    }