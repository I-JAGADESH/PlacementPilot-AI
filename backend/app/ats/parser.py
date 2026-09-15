from io import BytesIO
import re

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF resume and normalize common
    PDF extraction problems.
    """

    if not file_bytes:
        raise ValueError("The uploaded PDF is empty.")

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError(
            "Unable to read the uploaded PDF."
        ) from exc

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages.append(text)

    extracted_text = "\n".join(pages)

    if not extracted_text.strip():
        raise ValueError(
            "No readable text was found in the PDF. "
            "Please upload a text-based resume PDF."
        )

    return clean_resume_text(extracted_text)


def clean_resume_text(text: str) -> str:
    """
    Normalize resume text extracted from PDFs.

    Handles:
    - character-spaced words
    - URLs
    - email addresses
    - punctuation spacing
    - excessive whitespace
    """

    lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        line = normalize_urls(line)
        line = normalize_email(line)
        line = fix_character_spacing(line)

        line = re.sub(r"\s+", " ", line)

        line = re.sub(r"\s*,\s*", ", ", line)
        line = re.sub(r"\s*\.\s*", ". ", line)
        line = re.sub(r"\s*\|\s*", " | ", line)
        line = re.sub(r"\s*:\s*", ": ", line)

        line = re.sub(r"\s*\+\s*\+\s*", "++", line)
        line = re.sub(r"\s*#\s*", "#", line)

        lines.append(line.strip())

    return "\n".join(lines)


def normalize_urls(line: str) -> str:
    """
    Fix URLs where PDF extraction separates characters.
    """

    line = re.sub(
        r"h\s*t\s*t\s*p\s*s?\s*:\s*/\s*/",
        lambda match: (
            "https://" if "s" in match.group(0).lower() else "http://"
        ),
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"w\s*w\s*w\s*\.\s*",
        "www.",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"g\s*i\s*t\s*h\s*u\s*b\s*\.\s*c\s*o\s*m",
        "github.com",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"l\s*i\s*n\s*k\s*e\s*d\s*i\s*n\s*\.\s*c\s*o\s*m",
        "linkedin.com",
        line,
        flags=re.IGNORECASE,
    )

    return line


def normalize_email(line: str) -> str:
    """
    Fix common character spacing inside email addresses.
    """

    email_pattern = (
        r"([A-Za-z0-9._%+-])\s+"
        r"([A-Za-z0-9._%+-])"
        r"(\s*@\s*)"
        r"([A-Za-z0-9.-])\s*"
        r"(\s*\.\s*)"
        r"([A-Za-z]{2,})"
    )

    previous = None

    while previous != line:
        previous = line

        line = re.sub(
            email_pattern,
            r"\1\2@\4.\6",
            line,
        )

    return line


def fix_character_spacing(line: str) -> str:
    """
    Fix PDF extraction where characters are separated.

    Examples:
        S K I L L S -> SKILLS
        P Y T H O N -> PYTHON
        C + + -> C++
    """

    # Don't join lines containing URLs or emails.
    if (
        "http://" in line.lower()
        or "https://" in line.lower()
        or "github.com" in line.lower()
        or "linkedin.com" in line.lower()
        or "@" in line
    ):
        return line

    words = line.split()

    if len(words) < 3:
        return line

    single_char_count = sum(
        1 for word in words
        if len(word) == 1
    )

    ratio = single_char_count / len(words)

    if ratio >= 0.70:
        return "".join(words)

    return line