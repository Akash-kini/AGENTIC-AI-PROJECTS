
import re
from pathlib import Path

import config

_EMPTY_VALUES = {
    "", "none", "null", "n/a", "na", "unassigned", "unknown", "tbd", "tba",
    "not specified", "not assigned", "not mentioned", "unspecified", "no one",
    "nobody", "-",
}
_STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "will", "have", "has", "from",
    "about", "need", "needs", "should", "would", "could", "task", "work",
    "into", "their", "them", "they", "who", "what", "when", "which", "been",
}


# --------------------------------------------------------------------------- #
# Input validation
# --------------------------------------------------------------------------- #
def validate_transcript(text):
    """Return a cleaned transcript or raise ValueError with a friendly message."""
    if text is None:
        raise ValueError("No transcript was provided.")
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "").strip()
    if not cleaned:
        raise ValueError("The transcript is empty. Please provide the meeting text.")
    if len(cleaned) < config.MIN_TRANSCRIPT_CHARS:
        raise ValueError(
            f"The transcript is too short (minimum {config.MIN_TRANSCRIPT_CHARS} "
            "characters). Please provide more meeting content."
        )
    if len(cleaned) > config.MAX_TRANSCRIPT_CHARS:
        raise ValueError(
            f"The transcript is too long ({len(cleaned):,} characters; maximum "
            f"{config.MAX_TRANSCRIPT_CHARS:,}). Please split it into smaller parts."
        )
    if not re.search(r"[A-Za-z\u00C0-\u024F\u0900-\u097F]", cleaned):
        raise ValueError("The transcript does not appear to contain readable text.")
    return cleaned


def read_transcript_file(path_str):
    """Read a .txt transcript file, trying common encodings."""
    if not path_str or not str(path_str).strip():
        raise ValueError("No file path was provided.")
    path = Path(str(path_str).strip().strip('"').strip("'")).expanduser()
    if not path.exists():
        raise ValueError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    if path.suffix.lower() != ".txt":
        raise ValueError("Only .txt transcript files are supported.")
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        encodings = ("utf-16", "utf-8-sig", "cp1252")
    else:
        encodings = ("utf-8-sig", "cp1252", "latin-1")
    for encoding in encodings:
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError("Could not decode the file. Please save it as UTF-8 text.")


# --------------------------------------------------------------------------- #
# Output validation
# --------------------------------------------------------------------------- #
def _tokens(text):
    return re.findall(r"[a-z0-9\u0900-\u097F]+", str(text).lower())


def _keywords(text):
    return {t for t in _tokens(text) if len(t) >= 4 and t not in _STOPWORDS}


def _in_transcript(token, transcript_lower):
    pattern = r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])"
    return re.search(pattern, transcript_lower) is not None


def _clean_str(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _clean_list(value):
    """Convert to a de-duplicated list of non-empty strings."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return []
    seen, out = set(), []
    for item in value:
        if isinstance(item, dict):
            item = item.get("text") or item.get("decision") or item.get("action") \
                or item.get("question") or ""
        text = _clean_str(item)
        if text and text.lower() not in seen:
            seen.add(text.lower())
            out.append(text)
    return out


def _ground_owner(owner, transcript_lower):
    """Keep only owner names that actually appear in the transcript."""
    text = _clean_str(owner)
    if text.lower() in _EMPTY_VALUES:
        return None
    parts = [p.strip() for p in re.split(r",|&|/|\band\b|\+", text, flags=re.IGNORECASE)]
    kept = []
    for part in parts:
        if part.lower() in _EMPTY_VALUES:
            continue
        tokens = _tokens(part)
        if tokens and all(_in_transcript(tok, transcript_lower) for tok in tokens):
            kept.append(part)
    return ", ".join(kept) if kept else None


def _ground_deadline(deadline, transcript_lower):
    """Keep a deadline only if its words appear in the transcript."""
    text = _clean_str(deadline)
    if text.lower() in _EMPTY_VALUES:
        return None
    tokens = [t for t in _tokens(text) if len(t) >= 3 or t.isdigit()]
    if tokens and all(_in_transcript(tok, transcript_lower) for tok in tokens):
        return text
    return None


def _question_covers(questions, task_text, kind):
    """True if an existing clarification question already covers this gap."""
    keys = _keywords(task_text)
    needed = max(1, len(keys) // 2)
    owner_words = {"who", "whom", "responsible", "owner", "assign", "assigned",
                   "handle", "lead", "own"}
    date_words = {"when", "deadline", "due", "date", "timeline", "timeframe"}
    wanted = owner_words if kind == "owner" else date_words
    for question in questions:
        q_tokens = set(_tokens(question))
        if q_tokens & wanted and len(keys & _keywords(question)) >= needed:
            return True
    return False


def normalize_result(data, transcript):
    """Validate the model's JSON, enforce the schema, and strip anything ungrounded.

    Owners and deadlines that do not appear in the transcript are removed, and a
    clarification question is generated for every missing piece of information.
    Raises ValueError if the data is unusable.
    """
    if not isinstance(data, dict):
        raise ValueError("The AI response was not a JSON object.")

    transcript_lower = transcript.lower()
    summary = _clean_str(data.get("summary")) or "No summary could be generated."
    decisions = _clean_list(data.get("decisions"))
    follow_ups = _clean_list(data.get("follow_up_actions"))
    questions = _clean_list(data.get("clarification_questions"))

    raw_tasks = data.get("tasks")
    if not isinstance(raw_tasks, list):
        raw_tasks = []

    tasks, auto_questions = [], []
    for raw in raw_tasks:
        if isinstance(raw, str):
            raw = {"task": raw}
        if not isinstance(raw, dict):
            continue
        task_text = _clean_str(raw.get("task") or raw.get("description"))
        if not task_text:
            continue

        owner = _ground_owner(raw.get("owner"), transcript_lower)
        deadline = _ground_deadline(raw.get("deadline"), transcript_lower)
        ambiguity = _clean_str(raw.get("ambiguity_note"))
        if ambiguity.lower() in _EMPTY_VALUES:
            ambiguity = ""

        issues = []
        if owner is None:
            issues.append("No responsible person identified in the transcript")
            if not _question_covers(questions, task_text, "owner"):
                auto_questions.append(f"Who will be responsible for: {task_text}?")
        if deadline is None:
            issues.append("No deadline mentioned in the transcript")
            if not _question_covers(questions, task_text, "deadline"):
                if owner:
                    auto_questions.append(
                        f"What is the deadline for {owner}'s task: {task_text}?")
                else:
                    auto_questions.append(f"What is the deadline for: {task_text}?")
        if ambiguity:
            issues.append(f"Ambiguous: {ambiguity}")

        tasks.append({
            "id": len(tasks) + 1,
            "task": task_text,
            "owner": owner,
            "deadline": deadline,
            "status": "incomplete" if issues else "complete",
            "issues": issues,
        })

    existing = {q.lower() for q in questions}
    for question in auto_questions:
        if question.lower() not in existing:
            questions.append(question)
            existing.add(question.lower())

    questions = [q if q.endswith("?") else q.rstrip(".") + "?" for q in questions]

    incomplete = [
        {"task_id": t["id"], "task": t["task"], "issues": t["issues"]}
        for t in tasks if t["status"] == "incomplete"
    ]

    return {
        "summary": summary,
        "decisions": decisions,
        "tasks": tasks,
        "incomplete_action_items": incomplete,
        "follow_up_actions": follow_ups,
        "clarification_questions": questions,
    }
