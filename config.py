"""
===================================================================
  data-check  —  CONFIGURATION FILE
  Edit this file to configure your run. No other file needs to change.
===================================================================

WORKFLOW
--------
  Step 1 — Source files (A): one or more files whose rows produce valid keys.
             Each group of files can have its own extraction rule.

  Step 2 — Keys file (B): a plain-text file where all valid keys are saved
             after extraction. Used as the lookup reference.

  Step 3 — Target file (C): the file to be checked. Each row is assigned
             OK or CANCEL based on whether its key exists in (B).

HOW TO CONFIGURE KEYS
---------------------
  Positional TXT (fixed-width):
    Use FileFormat.POSITIONAL and list KeySlice(start, end) positions.
    Positions are 0-based, end is exclusive — same as Python slicing.

    Example — key = chars 0-2  +  chars 234-245:
      FileRule(
          format=FileFormat.POSITIONAL,
          positional_slices=[KeySlice(0, 2), KeySlice(234, 245)],
      )

  Delimited TXT (e.g. separated by ';'):
    Use FileFormat.DELIMITED and list column_indices (0-based).

    Example — key = column 4  +  column 2:
      FileRule(
          format=FileFormat.DELIMITED,
          delimiter=';',
          column_indices=[4, 2],
      )

  Excel (.xlsx):
    Use FileFormat.EXCEL and list column_indices
    (0-based, no header row assumed).

    Example — key = column B (index 1)  +  column D (index 3):
      FileRule(
          format=FileFormat.EXCEL,
          column_indices=[1, 3],
      )
"""

from pathlib import Path

from app.core.extractor import FileFormat, FileRule, KeySlice

# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────

# Root folder that contains all input files
INPUT_FOLDER = Path('data/input')

# Where the valid-keys file (B) will be saved
KEYS_FILE = Path('data/output/valid_keys.txt')

# Where the processed target file will be saved
OUTPUT_FILE = Path('data/output/result.txt')   # use .xlsx if target is Excel

# Optional log file path (set to None to disable file logging)
LOG_FILE: Path | None = Path('logs/run.log')


# ──────────────────────────────────────────────────────────────────────────────
# SOURCE FILE GROUPS (A)
# Each entry is a tuple: (list_of_filenames, FileRule)
# ──────────────────────────────────────────────────────────────────────────────

SOURCE_FILE_GROUPS: list[tuple[list[str], FileRule]] = [

    # --- Group 1: positional TXT, rule 1 ---
    # Key = chars 0-2  +  chars 234-245
    (
        [
            'r1a_18092025.txt',
            'r1b_18092025.txt',
            'r1c_19082025.TXT',
        ],
        FileRule(
            format=FileFormat.POSITIONAL,
            positional_slices=[KeySlice(0, 2), KeySlice(234, 245)],
            encoding='iso-8859-1',
        ),
    ),

    # --- Group 2: positional TXT, rule 2 ---
    # Key = chars 0-2  +  chars 236-247
    (
        [
            'r2a_20250918.txt',
            'r2b_19092025.txt',
        ],
        FileRule(
            format=FileFormat.POSITIONAL,
            positional_slices=[KeySlice(0, 2), KeySlice(236, 247)],
            encoding='iso-8859-1',
        ),
    ),

    # --- Example: delimited TXT group ---
    # Uncomment and adapt to add a delimited-TXT source
    # (
    #     ['source_delimited.txt'],
    #     FileRule(
    #         format=FileFormat.DELIMITED,
    #         delimiter=';',
    #         column_indices=[4, 2],
    #         encoding='iso-8859-1',
    #     ),
    # ),

    # --- Example: Excel group ---
    # Uncomment and adapt to add an Excel source
    # (
    #     ['source_data.xlsx'],
    #     FileRule(
    #         format=FileFormat.EXCEL,
    #         column_indices=[1, 3],
    #     ),
    # ),
]


# ──────────────────────────────────────────────────────────────────────────────
# TARGET FILE (C)
# The file whose rows will be checked against the valid-keys set.
# ──────────────────────────────────────────────────────────────────────────────

TARGET_FILE = INPUT_FOLDER / 'ACTIVE_RECORDS.txt'

TARGET_RULE = FileRule(
    format=FileFormat.DELIMITED,
    delimiter=';',
    column_indices=[4, 2],          # key = column 4 + column 2
    encoding='iso-8859-1',
)

# Column header label for the status column (Excel output only)
RESULT_COLUMN_NAME = 'STATUS'
