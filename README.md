# data-check

> Cross-reference records across files using composite key matching — supports fixed-width TXT, delimited TXT, and Excel.

[![CI](https://github.com/YOUR_USERNAME/data-check/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/data-check/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

**data-check** solves a common data reconciliation problem: given one or more reference files and a target file, determine which rows in the target have a matching record in the reference — and which do not.

Each row is identified by a **composite key** built from one or more fields. The tool appends an `OK` or `CANCEL` status to every row in the target file and generates a summary report.

```
Source files (A)  →  valid_keys.txt (B)  →  result file (C)
    [extract keys]       [save lookup]        [mark OK / CANCEL]
```

---

## Features

| Feature | Details |
|---|---|
| Multi-format sources | Fixed-width TXT, delimited TXT (any separator), Excel (.xlsx) |
| Flexible key config | Define key slices (positional) or column indices (delimited/Excel) per file group |
| Mixed source groups | Different rules for different file batches in the same run |
| Key transform hook | Optional `transform` function (e.g. uppercase, strip prefix) applied to every key |
| Summary report | Total rows, OK count, CANCEL count, percentages — logged to console and file |
| Zero-dependency config | All settings in a single `config.py` — no CLI flags needed |
| CI-ready | GitHub Actions workflow + pytest test suite included |

---

## Project Structure

```
data-check/
│
├── app/
│   ├── core/
│   │   ├── extractor.py    # Key extraction (positional, delimited, Excel)
│   │   ├── checker.py      # Row-level OK/CANCEL logic + output writing
│   │   └── key_store.py    # Save and load the valid-keys reference file
│   └── utils/
│       └── logger.py       # Centralised logging (console + file)
│
├── tests/
│   └── test_core.py        # Unit tests (pytest)
│
├── sample_data/            # Example input files for quick testing
│
├── .github/
│   └── workflows/ci.yml    # GitHub Actions CI
│
├── config.py               # ← EDIT THIS to configure your run
├── run_check.py            # Entry point
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/data-check.git
cd data-check
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Place your files in `data/input/`, then edit `config.py` to point to them, and run:

```bash
python run_check.py
```

Results are saved to `data/output/result.txt` (or `.xlsx`) and a summary is printed to the console.

---

## Configuration

Everything is configured in **`config.py`**. No other file needs to change.

### Paths

```python
INPUT_FOLDER = Path("data/input")
KEYS_FILE    = Path("data/output/valid_keys.txt")
OUTPUT_FILE  = Path("data/output/result.txt")
LOG_FILE     = Path("logs/run.log")
```

### Source file groups (A)

Each group pairs a list of filenames with a `FileRule` that defines how to build a key.

**Positional TXT** — key from character positions (0-based, end exclusive):

```python
(
    ["r1a.txt", "r1b.txt"],
    FileRule(
        format=FileFormat.POSITIONAL,
        positional_slices=[KeySlice(0, 2), KeySlice(234, 245)],
        encoding="iso-8859-1",
    ),
)
```

**Delimited TXT** — key from column indices:

```python
(
    ["source.txt"],
    FileRule(
        format=FileFormat.DELIMITED,
        delimiter=";",
        column_indices=[4, 2],
        encoding="iso-8859-1",
    ),
)
```

**Excel** — key from column indices (0-based, no header assumed):

```python
(
    ["source.xlsx"],
    FileRule(
        format=FileFormat.EXCEL,
        column_indices=[1, 3],
    ),
)
```

You can mix formats across groups in the same run.

### Optional key transform

Apply any function to normalise keys before storing or comparing them:

```python
FileRule(
    ...,
    transform=lambda k: k.upper().strip(),
)
```

### Target file (C)

```python
TARGET_FILE = INPUT_FOLDER / "ACTIVE_RECORDS.txt"

TARGET_RULE = FileRule(
    format=FileFormat.DELIMITED,
    delimiter=";",
    column_indices=[4, 2],
    encoding="iso-8859-1",
)
```

---

## Output

The output file is a copy of the target file with one extra column appended:

```
ID;NAME;CODE;DEPT;TYPE;STATUS
001;Alice;123456789;HR;AB;OK
002;Bob;999999999;IT;CD;CANCEL
003;Carol;111222333;FIN;EF;OK
```

A run summary is printed to the console and written to the log file:

```
Total rows : 1200
OK         : 1047 (87.25%)
CANCEL     : 153 (12.75%)
Output     : data/output/result.txt
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Requirements

- Python 3.11+
- pandas
- openpyxl

```bash
pip install -r requirements.txt
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
