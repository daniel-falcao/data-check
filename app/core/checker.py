"""
Checker module — reads the target file (C), builds a key per row,
looks it up in the valid-keys set, and writes the result column.

Supported target formats: positional TXT, delimited TXT, Excel.
Result values: OK_MARKER or CANCEL_MARKER appended to each row.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import pandas as pd

from app.core.extractor import FileFormat, FileRule, KeySlice

OK_MARKER = 'OK'
CANCEL_MARKER = 'CANCEL'


@dataclass
class CheckResult:
    """Contains summary information about the check
    results, including counts and percentages."""
    output_path: Path
    total: int
    ok_count: int
    cancel_count: int

    @property
    def ok_pct(self) -> float:
        """Function to calculate the percentage of OK rows."""
        return round(
            (self.ok_count / self.total) * 100, 2) if self.total else 0.0

    @property
    def cancel_pct(self) -> float:
        """Function to calculate the percentage of CANCEL rows."""
        return round(
            (self.cancel_count / self.total) * 100, 2) if self.total else 0.0

    def summary(self) -> str:
        """Function to generate a summary string of the check results."""
        return (
            f'Total rows : {self.total}\n'
            f'OK         : {self.ok_count} ({self.ok_pct}%)\n'
            f'CANCEL     : {self.cancel_count} ({self.cancel_pct}%)\n'
            f'Output     : {self.output_path}'
        )


def check_file(input_path: Path, output_path: Path,
               rule: FileRule, valid_keys: set[str],
               result_column_name: str = 'STATUS',) -> CheckResult:
    """
    Reads *input_path* using *rule*, appends a status column (OK / CANCEL),
    and writes the result to *output_path*.

    Output format follows the input format:
      - TXT (positional or delimited) → delimited TXT with the same delimiter
      - Excel → Excel (.xlsx)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if rule.format == FileFormat.EXCEL:
        return _check_excel(input_path, output_path,
                            rule, valid_keys, result_column_name)
    else:
        return _check_text(input_path, output_path, rule, valid_keys)


# ── Internal helpers ────────────────────────────────────────────────────

def _build_key_from_cols(cols: list[str], indices: list[int],
                         transform: Callable | None) -> str:
    try:
        parts = [cols[i].strip() for i in indices]
    except IndexError:
        return ''
    key = ''.join(parts).strip()
    return transform(key) if transform else key


def _build_key_from_line(line: str, slices: list[KeySlice],
                         transform: Callable | None) -> str:
    parts = [line[s.start:s.end] for s in slices]
    key = ''.join(parts).strip()
    return transform(key) if transform else key


def _check_text(input_path: Path, output_path: Path,
                rule: FileRule, valid_keys: set[str],) -> CheckResult:
    total = ok_count = cancel_count = 0

    with (
        open(input_path, encoding=rule.encoding, errors='ignore') as fin,
        open(output_path, 'w', encoding=rule.encoding) as fout,
    ):
        for raw_line in fin:
            line = raw_line.rstrip('\n')

            if rule.format == FileFormat.POSITIONAL:
                key = _build_key_from_line(line, rule.positional_slices,
                                           rule.transform)
            else:
                cols = line.split(rule.delimiter)
                key = _build_key_from_cols(cols, rule.column_indices,
                                           rule.transform)

            if not key:
                continue

            total += 1
            marker = OK_MARKER if key in valid_keys else CANCEL_MARKER
            if marker == OK_MARKER:
                ok_count += 1
            else:
                cancel_count += 1

            sep = (rule.delimiter
                   if rule.format == FileFormat.DELIMITED else ';')
            fout.write(f'{line}{sep}{marker}\n')

    return CheckResult(output_path, total, ok_count, cancel_count)


def _check_excel(input_path: Path, output_path: Path,
                 rule: FileRule, valid_keys: set[str],
                 result_column_name: str,) -> CheckResult:
    df = pd.read_excel(input_path, sheet_name=rule.sheet_name, dtype=str)
    df = df.fillna('')

    statuses = []
    ok_count = cancel_count = 0

    for _, row in df.iterrows():
        cols = row.tolist()
        key = _build_key_from_cols([str(c) for c in cols],
                                   rule.column_indices, rule.transform)
        marker = OK_MARKER if key in valid_keys else CANCEL_MARKER
        statuses.append(marker)
        if marker == OK_MARKER:
            ok_count += 1
        else:
            cancel_count += 1

    df[result_column_name] = statuses
    df.to_excel(output_path, index=False)

    return CheckResult(output_path, len(df), ok_count, cancel_count)
