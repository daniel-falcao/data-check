"""
Key extraction logic for positional (fixed-width) and delimited (CSV/Excel) files.

Each FileRule defines how to build a composite key from a source file:
  - For positional TXT: specify character slice positions
  - For delimited TXT (;) or Excel: specify column indices (0-based)
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

import pandas as pd


class FileFormat(str, Enum):
    """Functional file formats supported for key extraction and checking."""
    POSITIONAL = 'positional'   # fixed-width .txt
    DELIMITED = 'delimited'     # .txt separated by a delimiter (e.g. ;)
    EXCEL = 'excel'             # .xlsx / .xls


@dataclass
class KeySlice:
    """Defines one segment of a composite key for positional files."""
    start: int          # inclusive, 0-based character position
    end: int            # exclusive


@dataclass
class FileRule:
    """
    Configuration for extracting a composite key from a source file.

    Positional example (two slices concatenated):
        FileRule(
            format=FileFormat.POSITIONAL,
            positional_slices=[KeySlice(0, 2), KeySlice(234, 245)],
        )

    Delimited example (columns 4 and 2 concatenated):
        FileRule(
            format=FileFormat.DELIMITED,
            delimiter=';',
            column_indices=[4, 2],
        )

    Excel example (columns B and D, 0-based → indices 1 and 3):
        FileRule(
            format=FileFormat.EXCEL,
            column_indices=[1, 3],
        )
    """
    format: FileFormat

    # --- Positional-only ---
    positional_slices: list[KeySlice] = field(default_factory=list)
    encoding: str = 'iso-8859-1'

    # --- Delimited / Excel ---
    delimiter: str = ';'
    column_indices: list[int] = field(default_factory=list)
    sheet_name: int | str = 0

    # --- Optional post-processing ---
    transform: Callable[[str], str] | None = None   # e.g. lambda k: k.upper()


def extract_keys(path: Path, rule: FileRule) -> set[str]:
    """
    Reads *path* according to *rule* and
    returns a set of composite key strings.

    Raises:
        ValueError: if the file format is unsupported
        or slices/columns are misconfigured.
        FileNotFoundError: if *path* does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f'Source file not found: {path}')

    if rule.format == FileFormat.POSITIONAL:
        return _extract_positional(path, rule)
    elif rule.format == FileFormat.DELIMITED:
        return _extract_delimited(path, rule)
    elif rule.format == FileFormat.EXCEL:
        return _extract_excel(path, rule)
    else:
        raise ValueError(f'Unsupported file format: {rule.format}')


# ── Internal helpers ────────────────────────────────────────────────────

def _build_key(parts: list[str],
               transform: Callable[[str], str] | None) -> str:
    key = ''.join(parts).strip()
    if transform:
        key = transform(key)
    return key


def _extract_positional(path: Path, rule: FileRule) -> set[str]:
    if not rule.positional_slices:
        raise ValueError(
            'positional_slices must be set for POSITIONAL format.')
    keys: set[str] = set()
    with open(path, encoding=rule.encoding, errors='ignore') as fh:
        for line in fh:
            parts = [line[s.start:s.end] for s in rule.positional_slices]
            keys.add(_build_key(parts, rule.transform))
    return keys


def _extract_delimited(path: Path, rule: FileRule) -> set[str]:
    if not rule.column_indices:
        raise ValueError('column_indices must be set for DELIMITED format.')
    keys: set[str] = set()
    with open(path, encoding=rule.encoding, errors='ignore') as fh:
        for line in fh:
            cols = line.rstrip('\n').split(rule.delimiter)
            try:
                parts = [cols[i].strip() for i in rule.column_indices]
            except IndexError:
                continue
            keys.add(_build_key(parts, rule.transform))
    return keys


def _extract_excel(path: Path, rule: FileRule) -> set[str]:
    if not rule.column_indices:
        raise ValueError('column_indices must be set for EXCEL format.')
    df = pd.read_excel(path, sheet_name=rule.sheet_name,
                       header=None, dtype=str)
    df = df.fillna('')
    keys: set[str] = set()
    for _, row in df.iterrows():
        try:
            parts = [str(row.iloc[i]).strip() for i in rule.column_indices]
        except IndexError:
            continue
        keys.add(_build_key(parts, rule.transform))
    return keys
