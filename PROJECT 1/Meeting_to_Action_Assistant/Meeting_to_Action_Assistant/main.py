

import argparse
import json
import sys

import config
from src import ai_processor, report_generator, validators


def _setup_console():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _read_pasted_transcript():
    print("\nPaste or type the meeting transcript below.")
    print("When finished, type END on a new line and press Enter")
    print("(or press Ctrl+Z then Enter on Windows).\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines), "terminal input"


def _read_interactively():
    while True:
        print("\nHow would you like to provide the meeting transcript?")
        print("  1) Type / paste it in the terminal")
        print("  2) Load it from a .txt file")
        print("  3) Quit")
        try:
            choice = input("Enter 1, 2 or 3: ").strip()
        except EOFError:
            raise SystemExit(0)
        if choice == "1":
            return _read_pasted_transcript()
        if choice == "2":
            path = input("Path to the .txt file (e.g. samples\\sample_meeting.txt): ")
            try:
                return validators.read_transcript_file(path), path.strip().strip('"')
            except ValueError as exc:
                print(f"\n[!] {exc}")
                continue
        if choice == "3":
            raise SystemExit(0)
        print("[!] Please enter 1, 2 or 3.")


def _get_transcript(args):
    if args.file:
        return validators.read_transcript_file(args.file), args.file
    if args.text is not None:
        return args.text, "command-line text"
    return _read_interactively()


def run(args):
    ai_processor.ensure_api_key()  # fail early, before asking for any input
    raw_text, source = _get_transcript(args)
    transcript = validators.validate_transcript(raw_text)

    print(f"\nAnalyzing transcript ({len(transcript):,} characters) with Gemini...")
    raw_result, model_used = ai_processor.analyze_meeting(transcript)
    result = validators.normalize_result(raw_result, transcript)

    report_text = report_generator.build_report(result, source, model_used)
    print("\n" + report_text)

    print("\n--- JSON OUTPUT ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    json_path, txt_path = report_generator.save_reports(
        result, report_text, source, model_used, config.OUTPUT_DIR)
    print("\nReports saved:")
    print(f"  JSON: {json_path}")
    print(f"  TXT : {txt_path}")


def main():
    _setup_console()
    parser = argparse.ArgumentParser(description="AI-Powered Meeting-to-Action Assistant")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--file", help="Path to a .txt meeting transcript")
    group.add_argument("-t", "--text", help="Meeting transcript text")
    args = parser.parse_args()

    try:
        run(args)
    except ValueError as exc:
        print(f"\n[Input error] {exc}")
        return 2
    except ai_processor.AIProcessingError as exc:
        print(f"\n[AI error] {exc}")
        return 3
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 130
    except OSError as exc:
        print(f"\n[File error] {exc}")
        return 4
    except Exception as exc:  # noqa: BLE001 - last-resort safety net
        print(f"\n[Unexpected error] {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
