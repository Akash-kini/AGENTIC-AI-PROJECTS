# M1-P1: AI-Based Personalized Career Content Generator

A terminal application that collects a student's profile and uses the **Google Gemini API** to generate a personalised career profile: professional summary, skill-gap report, course and topic recommendations, a learning roadmap, technical interview Q&A, and resume-ready content.

## Features

- Collects **name, degree, academic interests, technical skills, experience level and career goal** through terminal prompts (or from a JSON file with `--file`)
- Customised **professional summary**
- **Skill-gap report** (existing vs. missing skills with importance)
- Recommended **courses and learning topics**
- Phase-by-phase **learning roadmap** with milestone projects
- **10 technical interview questions with answers**, matched to the experience level
- **Resume-ready content** (headline, summary, skills, education, suggested portfolio projects)
- **Consistency across sections**: the profile is built in 4 AI steps that all share the same decided "core" (target role, existing skills, missing skills). Code then enforces that existing skills equal the skills the student entered, that no skill is both existing and missing, that resume skills are only the student's, and that a Beginner is not described as experienced. A *Consistency Checks* section is included in the output.
- No invented employers, certifications or finished projects: resume projects are labelled **suggested** portfolio projects
- Saves the profile as **JSON** and **Markdown** in `output/`
- Input validation, retry with back-off, model fallback and friendly error messages

## Technologies used

Python 3, Google Gen AI SDK (`google-genai`), Gemini API (JSON output mode), `python-dotenv`, and the Python standard library (`argparse`, `json`, `re`, `pathlib`). No database, Docker or web frontend is needed.

## Installation (Windows 10/11, VS Code terminal)

Requires Python 3.10 or newer. Open the VS Code terminal (**Command Prompt** profile recommended) and run:

```bat
cd AI_College_Projects\Career_Content_Generator
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

## Getting and configuring a Gemini API key

1. Open <https://aistudio.google.com/apikey> and sign in with a Google account.
2. Click **Create API key** (choose or create a project) and copy the key.
3. In this project folder, copy `.env.example` to `.env` (the `copy` command above does this).
4. Open `.env` in Notepad and replace the placeholder:

```
GEMINI_API_KEY=AIza...your-real-key...
```

5. Save the file. The key is read with `python-dotenv`; it is never written in the code. Never share or commit your `.env` file.

The default model is set in `config.py` (`MODEL_NAME`). To use a different Gemini model, add `GEMINI_MODEL=<model-name>` to `.env`. If the chosen model is unavailable, overloaded or out of quota, the app automatically tries the models listed in `FALLBACK_MODELS` in `config.py`.

## How to run

```bat
REM 1) Answer the questions in the terminal
python main.py

REM 2) Or use the included sample student (no questions asked)
python main.py --file samples\sample_student.json
```

Generation makes 4 Gemini calls and typically takes 30-90 seconds. Results are saved to `output/` as `career_profile_<name>_<timestamp>.json` and `.md`.

## Sample input

Terminal prompts (separate multiple items with commas):

```
Full name: Aarav Sharma
Degree / program: B.Tech in Computer Science and Engineering
Academic interests: Artificial Intelligence, Machine Learning
Technical skills: Python, NumPy, SQL
Experience level - 1) Beginner  2) Intermediate  3) Advanced: 1
Career goal: AI Engineer
```

Or `samples/sample_student.json`:

```json
{
  "name": "Aarav Sharma",
  "degree": "B.Tech in Computer Science and Engineering",
  "academic_interests": ["Artificial Intelligence", "Machine Learning"],
  "technical_skills": ["Python", "NumPy", "SQL"],
  "experience_level": "Beginner",
  "career_goal": "AI Engineer"
}
```

## Sample output

> **Note:** `samples/example_output.json` and `samples/example_output.md` were produced by running this project's real validation and formatting code on a *simulated* model response (the file says `SIMULATED-EXAMPLE`), to show the exact format. Your own runs call the live Gemini API, and the content will differ.

Excerpt of `example_output.md`:

```markdown
# Career Profile: Aarav Sharma

*Generated 2026-11-06T10:05:48 using SIMULATED-EXAMPLE (offline stub, not a live Gemini call)*

## Student Overview

- **Degree:** B.Tech in Computer Science and Engineering
- **Academic interests:** Artificial Intelligence, Machine Learning
- **Technical skills:** Python, NumPy, SQL
- **Experience level:** Beginner
- **Career goal:** AI Engineer

## Professional Summary

Computer Science and Engineering student pursuing a B.Tech with a strong interest in Artificial Intelligence and Machine Learning. Has a foundation in Python, NumPy and SQL and is building toward an entry-level AI Engineer role. Currently at a beginner level and focused on learning core machine learning and deep learning fundamentals through structured study and hands-on projects.

## Skill-Gap Report

**Target role:** AI Engineer

The student has useful programming and data foundations but is at the start of the machine learning path. With consistent study over roughly six months, an entry-level AI Engineer profile is realistic.

### Existing Skills

| Skill | Relevance to goal | Note |
|---|---|---|
| Python | high | Primary language for ML and AI development. |
| NumPy | high | Core library for numerical computing and array operations used in ML. |
| SQL | medium | Useful for querying and preparing data for models. |

### Missing Skills

| Skill | Importance | Why it is needed |
|---|---|---|
| Pandas and Data Wrangling | critical | Real-world datasets must be cleaned and explored before modelling. |
| Statistics and Probability | critical | Underpins model evaluation and ML theory. |
| Linear Algebra and Calculus Basics | important | Needed to understand how models learn. |
| Machine Learning with scikit-learn | critical | Standard toolkit for classical ML models. |
| Deep Learning with PyTorch | critical | Most AI Engineer roles build and fine-tune neural networks. |
| Git and GitHub | important | Version control is expected in every engineering team. |
...
```

The JSON file contains: `student`, `professional_summary`, `skill_analysis`, `learning_recommendations`, `learning_roadmap`, `interview_preparation`, `resume_content` and `consistency_report`.

## Project folder structure

```
Career_Content_Generator/
|-- main.py                  # terminal app / entry point
|-- config.py                # model name, retries, limits, paths
|-- requirements.txt
|-- .env.example             # placeholder API key (copy to .env)
|-- README.md
|-- src/
|   |-- __init__.py
|   |-- ai_processor.py      # Gemini calls, retries, JSON parsing
|   |-- profile_generator.py # prompts, 4-step generation, Markdown/JSON saving
|   `-- validators.py        # input validation, output validation, consistency checks
|-- samples/
|   |-- sample_student.json
|   |-- example_output.json  # simulated example (see note)
|   `-- example_output.md
`-- output/                  # generated profiles are saved here
```

> Course recommendations come from the AI model. Please verify that a course exists and check its current details before enrolling.

## Troubleshooting (Windows)

| Problem | Fix |
|---|---|
| `python` is not recognised | Install Python 3.10+ from python.org and tick **Add python.exe to PATH**, or use `py` instead of `python`. |
| PowerShell blocks `venv\Scripts\Activate.ps1` | Use **Command Prompt** (cmd) instead, or run `Set-ExecutionPolicy -Scope Process Bypass` first. |
| `GEMINI_API_KEY is missing` | Make sure the file is named exactly `.env` (not `.env.txt`) and contains your real key. In Notepad choose *Save as -> All files*. |
| HTTP 429 / quota errors | Free-tier rate limit. The app retries automatically; wait a minute and run again. |
| `Model not found` | Set `GEMINI_MODEL` in `.env` to a model your key can use (see <https://ai.google.dev/gemini-api/docs/models>). |
