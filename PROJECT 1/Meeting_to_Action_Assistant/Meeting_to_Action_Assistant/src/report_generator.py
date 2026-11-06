
import json
import textwrap
from datetime import datetime
from pathlib import Path

WIDTH = 78
LINE = "=" * WIDTH
THIN = "-" * WIDTH


def _wrap(text, indent=0, bullet=""):
    prefix = " " * indent + bullet
    return textwrap.fill(
        str(text), width=WIDTH, initial_indent=prefix,
        subsequent_indent=" " * len(prefix), break_on_hyphens=False,
    )


def _section(title):
    return ["", THIN, title, THIN]


def build_report(result, source_name, model_name):
    lines = [LINE, "MEETING-TO-ACTION REPORT".center(WIDTH), LINE]
    lines.append(f"Source    : {source_name}")
    lines.append(f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Model     : {model_name}")

    lines += _section("SUMMARY")
    lines.append(_wrap(result["summary"]))

    lines += _section("DECISIONS")
    if result["decisions"]:
        lines += [_wrap(d, bullet=f"{i}. ") for i, d in enumerate(result["decisions"], 1)]
    else:
        lines.append("No decisions were recorded in the transcript.")

    lines += _section("TASKS")
    if result["tasks"]:
        for task in result["tasks"]:
            lines.append(_wrap(task["task"], bullet=f"{task['id']}. "))
            lines.append(f"     Owner    : {task['owner'] or 'UNASSIGNED'}")
            lines.append(f"     Deadline : {task['deadline'] or 'NOT SPECIFIED'}")
            lines.append(f"     Status   : {task['status'].upper()}")
    else:
        lines.append("No tasks were identified in the transcript.")

    lines += _section("INCOMPLETE OR AMBIGUOUS ACTION ITEMS")
    if result["incomplete_action_items"]:
        for item in result["incomplete_action_items"]:
            lines.append(_wrap(item["task"], bullet="* "))
            for issue in item["issues"]:
                lines.append(_wrap(issue, indent=4, bullet="- "))
    else:
        lines.append("All identified tasks have an owner and a deadline.")

    lines += _section("FOLLOW-UP ACTIONS")
    if result["follow_up_actions"]:
        lines += [_wrap(a, bullet=f"{i}. ") for i, a in enumerate(result["follow_up_actions"], 1)]
    else:
        lines.append("No follow-up actions.")

    lines += _section("CLARIFICATION QUESTIONS")
    if result["clarification_questions"]:
        lines += [_wrap(q, bullet=f"{i}. ") for i, q in enumerate(result["clarification_questions"], 1)]
    else:
        lines.append("No clarification needed.")

    lines += ["", LINE]
    return "\n".join(lines)


def save_reports(result, report_text, source_name, model_name, output_dir):
    """Save the JSON and TXT reports. Returns (json_path, txt_path)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"meeting_report_{stamp}.json"
    txt_path = output_dir / f"meeting_report_{stamp}.txt"

    payload = {
        "meta": {
            "source": source_name,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "model": model_name,
        },
        **result,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    txt_path.write_text(report_text + "\n", encoding="utf-8")
    return json_path, txt_path
