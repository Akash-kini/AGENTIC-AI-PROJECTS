"""Input validation, AI-output validation and cross-section consistency checks."""

import json
import re
from pathlib import Path

import config

EXPERIENCE_LEVELS = ("Beginner", "Intermediate", "Advanced")
_LEVEL_ALIASES = {
    "1": "Beginner", "beginner": "Beginner", "b": "Beginner", "fresher": "Beginner",
    "entry": "Beginner", "entry level": "Beginner", "entry-level": "Beginner",
    "novice": "Beginner", "student": "Beginner",
    "2": "Intermediate", "intermediate": "Intermediate", "i": "Intermediate",
    "mid": "Intermediate", "medium": "Intermediate",
    "3": "Advanced", "advanced": "Advanced", "a": "Advanced", "expert": "Advanced",
    "senior": "Advanced",
}
_EMPTY_LIST_WORDS = {"none", "n/a", "na", "nil", "no", "-"}


# --------------------------------------------------------------------------- #
# Student input validation
# --------------------------------------------------------------------------- #
def _clean_text(value):
    return re.sub(r"\s+", " ", re.sub(r"[\x00-\x1f\x7f]", " ", str(value or ""))).strip()


def validate_name(value):
    text = _clean_text(value)
    if not text:
        raise ValueError("Name cannot be empty.")
    if len(text) > config.MAX_NAME_LENGTH:
        raise ValueError(f"Name is too long (maximum {config.MAX_NAME_LENGTH} characters).")
    if not re.search(r"[^\W\d_]", text):
        raise ValueError("Name must contain letters.")
    return text


def validate_text_field(value, label):
    text = _clean_text(value)
    if not text:
        raise ValueError(f"{label} cannot be empty.")
    if len(text) > config.MAX_FIELD_LENGTH:
        raise ValueError(f"{label} is too long (maximum {config.MAX_FIELD_LENGTH} characters).")
    if not re.search(r"[^\W_]", text):
        raise ValueError(f"{label} must contain letters or numbers.")
    return text


def parse_list(value, label, allow_empty=False):
    """Accept a comma/semicolon separated string or a list; return a clean unique list."""
    if isinstance(value, (list, tuple)):
        items = [str(v) for v in value]
    else:
        items = re.split(r"[,;\n]", str(value or ""))
    cleaned, seen = [], set()
    for item in items:
        text = _clean_text(item)
        if not text or text.lower() in _EMPTY_LIST_WORDS:
            continue
        if len(text) > config.MAX_FIELD_LENGTH:
            raise ValueError(f"An item in {label} is too long: '{text[:30]}...'")
        if text.lower() not in seen:
            seen.add(text.lower())
            cleaned.append(text)
    if len(cleaned) > config.MAX_LIST_ITEMS:
        raise ValueError(f"Too many items in {label} (maximum {config.MAX_LIST_ITEMS}).")
    if not cleaned and not allow_empty:
        raise ValueError(f"Please enter at least one item for {label}.")
    return cleaned


def validate_experience_level(value):
    key = _clean_text(value).lower()
    if key in _LEVEL_ALIASES:
        return _LEVEL_ALIASES[key]
    raise ValueError("Experience level must be Beginner, Intermediate or Advanced (or 1, 2, 3).")


def validate_student(data):
    """Validate a full student dictionary (from prompts or a JSON file)."""
    if not isinstance(data, dict):
        raise ValueError("Student data must be a JSON object.")

    def pick(*keys):
        for key in keys:
            if key in data:
                return data[key]
        return None

    return {
        "name": validate_name(pick("name")),
        "degree": validate_text_field(pick("degree"), "Degree"),
        "academic_interests": parse_list(
            pick("academic_interests", "interests"), "academic interests"),
        "technical_skills": parse_list(
            pick("technical_skills", "skills"), "technical skills", allow_empty=True),
        "experience_level": validate_experience_level(
            pick("experience_level", "experience")),
        "career_goal": validate_text_field(pick("career_goal", "goal"), "Career goal"),
    }


def load_student_file(path_str):
    """Load and validate a student JSON file."""
    if not path_str or not str(path_str).strip():
        raise ValueError("No file path was provided.")
    path = Path(str(path_str).strip().strip('"').strip("'")).expanduser()
    if not path.is_file():
        raise ValueError(f"File not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"The file is not valid JSON: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError("The file could not be read. Please save it as UTF-8.") from exc
    return validate_student(data)


# --------------------------------------------------------------------------- #
# AI output helpers
# --------------------------------------------------------------------------- #
def _s(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _str_list(value, limit=50):
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return []
    out, seen = [], set()
    for item in value:
        text = _s(item)
        if text and text.lower() not in seen:
            seen.add(text.lower())
            out.append(text)
        if len(out) >= limit:
            break
    return out


def _dict_list(value):
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _norm_skill(name):
    """Normalise a skill name so 'Python programming' matches 'python'."""
    text = _s(name).lower()
    text = re.sub(r"\b(programming|language|basics|fundamentals|skills?)\b", "", text)
    return re.sub(r"[^a-z0-9+#.]+", " ", text).strip()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


# --------------------------------------------------------------------------- #
# Section validators (each takes raw model JSON and returns a clean section)
# --------------------------------------------------------------------------- #
def validate_core(raw, student):
    """Professional summary + skill gap. Existing skills are forced to match the input."""
    summary = _s(raw.get("professional_summary"))
    _require(summary, "The AI did not return a professional summary.")

    model_existing = {_norm_skill(i.get("skill")): i for i in _dict_list(raw.get("existing_skills"))}
    existing = []
    for skill in student["technical_skills"]:
        item = model_existing.get(_norm_skill(skill), {})
        relevance = _s(item.get("relevance_to_goal")).lower()
        existing.append({
            "skill": skill,  # always the student's own wording
            "relevance_to_goal": relevance if relevance in ("high", "medium", "low") else "medium",
            "note": _s(item.get("note")),
        })

    owned = {_norm_skill(s) for s in student["technical_skills"]}
    missing, seen = [], set()
    for item in _dict_list(raw.get("missing_skills")):
        name = _s(item.get("skill"))
        key = _norm_skill(name)
        if not name or key in owned or key in seen:
            continue
        seen.add(key)
        importance = _s(item.get("importance")).lower().replace(" ", "_")
        missing.append({
            "skill": name,
            "importance": importance if importance in ("critical", "important", "nice_to_have")
            else "important",
            "why_needed": _s(item.get("why_needed")),
        })
    _require(missing, "The AI did not return any missing skills.")

    return {
        "target_role": _s(raw.get("target_role")) or student["career_goal"],
        "professional_summary": summary,
        "existing_skills": existing,
        "missing_skills": missing,
        "readiness_assessment": _s(raw.get("readiness_assessment")),
    }


def validate_learning(raw, student):
    courses = []
    for item in _dict_list(raw.get("recommended_courses")):
        title = _s(item.get("title"))
        if title:
            courses.append({
                "title": title,
                "platform": _s(item.get("platform")) or "Check online platforms",
                "level": _s(item.get("level")),
                "covers_skills": _str_list(item.get("covers_skills")),
                "why": _s(item.get("why")),
            })
    _require(courses, "The AI did not return any course recommendations.")

    topics = []
    for item in _dict_list(raw.get("learning_topics")):
        topic = _s(item.get("topic"))
        if topic:
            topics.append({
                "topic": topic,
                "why": _s(item.get("why")),
                "subtopics": _str_list(item.get("subtopics"), 12),
            })
    _require(topics, "The AI did not return any learning topics.")

    roadmap = []
    for item in _dict_list(raw.get("learning_roadmap")):
        title = _s(item.get("title"))
        if title:
            roadmap.append({
                "phase": len(roadmap) + 1,
                "title": title,
                "duration": _s(item.get("duration")),
                "goals": _str_list(item.get("goals"), 10),
                "topics": _str_list(item.get("topics"), 15),
                "milestone_project": _s(item.get("milestone_project")),
            })
    _require(roadmap, "The AI did not return a learning roadmap.")

    return {"recommended_courses": courses, "learning_topics": topics,
            "learning_roadmap": roadmap}


def validate_interview(raw, student):
    questions = []
    for item in _dict_list(raw.get("technical_questions")):
        question, answer = _s(item.get("question")), _s(item.get("answer"))
        if question and answer:
            difficulty = _s(item.get("difficulty")).capitalize()
            questions.append({
                "question": question,
                "difficulty": difficulty if difficulty in EXPERIENCE_LEVELS else student["experience_level"],
                "topic": _s(item.get("topic")),
                "answer": answer,
            })
    _require(len(questions) >= 3, "The AI returned too few interview questions.")
    return {"technical_interview_questions": questions}


def validate_resume(raw, student, core):
    """Resume content. Skills listed as 'technical skills' are forced to be the student's own."""
    summary = _s(raw.get("summary"))
    _require(summary, "The AI did not return a resume summary.")

    missing_names = [m["skill"] for m in core["missing_skills"]]
    allowed = {_norm_skill(s) for s in student["technical_skills"] + missing_names}

    learning_raw = raw.get("skills_section", {}) if isinstance(raw.get("skills_section"), dict) else {}
    owned = {_norm_skill(s) for s in student["technical_skills"]}
    currently_learning = [s for s in _str_list(learning_raw.get("currently_learning"), 15)
                          if _norm_skill(s) not in owned]

    projects = []
    for item in _dict_list(raw.get("suggested_projects")):
        title = _s(item.get("title"))
        if not title:
            continue
        stack = [t for t in _str_list(item.get("tech_stack"), 10) if _norm_skill(t) in allowed]
        if not stack:
            stack = list(student["technical_skills"][:3])
        projects.append({
            "title": title,
            "description": _s(item.get("description")),
            "tech_stack": stack,
            "resume_bullets": _str_list(item.get("resume_bullets"), 5),
        })

    return {
        "headline": _s(raw.get("headline")) or f"{student['experience_level']} {core['target_role']} Aspirant",
        "summary": summary,
        "skills_section": {
            "technical_skills": list(student["technical_skills"]),
            "currently_learning": currently_learning,
        },
        "education": student["degree"],
        "experience_note": _s(raw.get("experience_note")),
        "suggested_projects": projects,
        "project_disclaimer": (
            "These are SUGGESTED portfolio projects. Add them to a resume only after "
            "you have actually built them."
        ),
    }


# --------------------------------------------------------------------------- #
# Cross-section consistency check
# --------------------------------------------------------------------------- #
_SENIOR_CLAIMS = re.compile(
    r"\b(\d+\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+|industry\s+|work\s+)?experience"
    r"|senior|expert|seasoned|extensive (?:industry )?experience"
    r"|proven track record|worked (?:at|for|as)|interned (?:at|as))\b",
    re.IGNORECASE,
)


def run_consistency_checks(profile, student):
    """Return a list of human-readable check results (also stored in the profile)."""
    report = []
    core, resume = profile["skill_analysis"], profile["resume_content"]

    owned = {_norm_skill(s) for s in student["technical_skills"]}
    listed = {_norm_skill(s["skill"]) for s in core["existing_skills"]}
    report.append({
        "check": "Existing skills match the skills the student entered",
        "passed": listed == owned,
    })

    overlap = owned & {_norm_skill(m["skill"]) for m in core["missing_skills"]}
    report.append({"check": "No skill appears as both existing and missing", "passed": not overlap})

    resume_skills = {_norm_skill(s) for s in resume["skills_section"]["technical_skills"]}
    report.append({"check": "Resume technical skills only list the student's skills",
                   "passed": resume_skills <= owned})

    text_blob = " ".join([
        profile["professional_summary"], resume["headline"], resume["summary"],
        " ".join(b for p in resume["suggested_projects"] for b in p["resume_bullets"]),
    ])
    if student["experience_level"] == "Beginner":
        found = _SENIOR_CLAIMS.search(text_blob)
        report.append({
            "check": "No senior/professional-experience claims for a Beginner",
            "passed": found is None,
            "detail": f"Found phrase: '{found.group(0)}'" if found else "",
        })

    stack_ok = all(
        {_norm_skill(t) for t in p["tech_stack"]} <= owned | {_norm_skill(m["skill"]) for m in core["missing_skills"]}
        for p in resume["suggested_projects"]
    )
    report.append({"check": "Project tech stacks only use existing or roadmap skills", "passed": stack_ok})
    return report
