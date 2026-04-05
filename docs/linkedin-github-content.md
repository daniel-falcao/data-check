# LinkedIn & GitHub Content — data-check

---

## 1. GITHUB REPOSITORY DESCRIPTION (one line, shown under the repo name)

File reconciliation tool that cross-references records across fixed-width TXT, delimited TXT, and Excel files using configurable composite key matching.

---

## 2. GITHUB REPOSITORY TOPICS (tags)

python, data-engineering, file-processing, reconciliation, automation, pandas, fixed-width, csv, excel, backend, etl, data-quality

---

## 3. LINKEDIN PROJECT ENTRY

Title:
data-check — File Reconciliation Tool

Description:
Built a Python tool that automates record cross-referencing between files — a task that typically requires manual effort in data operations and back-office workflows.

The tool reads one or more source files (A), extracts a composite key per row based on configurable field positions or column indices, stores those keys in a reference file (B), then reads a target file (C) and marks each row as OK or CANCEL depending on whether its key exists in the reference set.

Key technical decisions:
• Designed a flexible FileRule abstraction supporting three input formats in the same pipeline: fixed-width positional TXT, delimiter-separated TXT, and Excel (.xlsx)
• Used a dataclass-based configuration model (KeySlice, FileRule) so key extraction rules are declarative and readable rather than hardcoded slice literals
• Centralised all user-facing configuration in a single config.py with inline documentation — no CLI flags, no hidden magic
• Separated concerns into extractor, checker, and key_store modules for independent testability
• Added an optional transform hook on FileRule so key normalisation (e.g. uppercase, strip prefix) is applied consistently without touching business logic

Stack: Python · pandas · openpyxl · pytest · GitHub Actions

---

## 4. LINKEDIN FEATURED SECTION CAPTION

A recurring challenge in data operations: two systems produce files in completely different formats, and you need to know which records appear in both — and which don't.

This tool handles that reconciliation automatically. You configure the key fields once (character positions for fixed-width files, column indices for CSV or Excel), point it at your files, and it outputs the target file annotated with OK or CANCEL on every row, plus a summary with match rates.

It was originally a single-purpose script. I refactored it into a structured project with a clean configuration model that supports three file formats interchangeably.

→ GitHub: github.com/YOUR_USERNAME/data-check

---

## 5. UPDATED GITHUB PROFILE README

Replace the projects section in your profile README with this expanded version:

```markdown
## Hi, I'm [Your Name]

Python developer focused on backend engineering and data automation.
Transitioning into tech — bringing analytical thinking and operational
experience from a previous career into software that solves real business problems.

**What I build**
- Data processing pipelines that handle TXT, CSV, and Excel at scale
- REST APIs with FastAPI and clean layered architecture
- Automation tools that replace error-prone manual workflows

**Tech I work with**
Python · FastAPI · Docker · PostgreSQL · pandas · sentence-transformers · Railway · GitHub Actions

**Projects**

| Project | What it does | Stack |
|---|---|---|
| [semantic-data-matcher](https://github.com/YOUR_USERNAME/semantic-data-matcher) | Matches free-text descriptions to a reference domain using multilingual NLP. Live REST API on Railway. | Python · FastAPI · sentence-transformers · Docker |
| [data-check](https://github.com/YOUR_USERNAME/data-check) | Cross-references records across fixed-width TXT, delimited TXT, and Excel files using composite key matching. | Python · pandas · openpyxl |

**Currently learning**
Async Python · PostgreSQL query optimisation · System design fundamentals

Open to backend and data engineering roles — remote preferred.

📫 [linkedin.com/in/YOUR_PROFILE](https://linkedin.com/in/YOUR_PROFILE)
```
