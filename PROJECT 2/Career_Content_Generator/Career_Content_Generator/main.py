

import argparse
import sys

import config
from src import ai_processor, profile_generator, validators


def _setup_console():
    """Avoid Unicode crashes in the Windows console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _ask(prompt, validator):
    """Keep asking until the validator accepts the answer."""
    while True:
        try:
            answer = input(prompt)
        except EOFError:
            raise SystemExit("\nInput ended before all questions were answered.")
        try:
            return validator(answer)
        except ValueError as exc:
            print(f"  [!] {exc} Please try again.")


def collect_student_interactively():
    print("\n=== Student Information ===")
    print("(Separate multiple items with commas.)\n")
    name = _ask("Full name: ", validators.validate_name)
    degree = _ask("Degree / program (e.g. B.Tech Computer Science): ",
                  lambda v: validators.validate_text_field(v, "Degree"))
    interests = _ask("Academic interests (e.g. Artificial Intelligence, Machine Learning): ",
                     lambda v: validators.parse_list(v, "academic interests"))
    skills = _ask("Technical skills (e.g. Python, NumPy, SQL; type 'none' if none): ",
                  lambda v: validators.parse_list(v, "technical skills", allow_empty=True))
    level = _ask("Experience level - 1) Beginner  2) Intermediate  3) Advanced: ",
                 validators.validate_experience_level)
    goal = _ask("Career goal (e.g. AI Engineer): ",
                lambda v: validators.validate_text_field(v, "Career goal"))
    return validators.validate_student({
        "name": name, "degree": degree, "academic_interests": interests,
        "technical_skills": skills, "experience_level": level, "career_goal": goal,
    })


def run(args):
    ai_processor.ensure_api_key()  # fail early, before asking any questions

    if args.file:
        student = validators.load_student_file(args.file)
        print(f"Loaded student data for {student['name']} from {args.file}")
    else:
        student = collect_student_interactively()

    print(f"\nGenerating career profile for {student['name']} "
          "(4 AI steps - this can take up to a minute)...\n")
    profile = profile_generator.generate_profile(student, progress=print)
    markdown = profile_generator.build_markdown(profile)

    print("\n" + "=" * 78)
    print(markdown)
    print("=" * 78)

    json_path, md_path = profile_generator.save_profile(profile, markdown, config.OUTPUT_DIR)
    print("\nCareer profile saved:")
    print(f"  JSON    : {json_path}")
    print(f"  Markdown: {md_path}")


def main():
    _setup_console()
    parser = argparse.ArgumentParser(description="AI-Based Personalized Career Content Generator")
    parser.add_argument("-f", "--file", help="Path to a student JSON file (skips the prompts)")
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
