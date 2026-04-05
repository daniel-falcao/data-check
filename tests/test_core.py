"""
Unit tests for extractor, key_store, and checker modules.
Run with: pytest tests/ -v
"""

from pathlib import Path
import pytest

from app.core.extractor import FileFormat, FileRule, KeySlice, extract_keys
from app.core.key_store import save_keys, load_keys
from app.core.checker import check_file, OK_MARKER, CANCEL_MARKER


# ── Extractor ───────────────────────────────────────────────────────────

def test_extract_positional(tmp_path):
    """Test extracting keys from a fixed-width positional file."""
    f = tmp_path / 'source.txt'
    # line: chars 0-2 = 'AB', chars 5-8 = '123'
    f.write_text('AB  123  \nCD  456  \n', encoding='utf-8')
    rule = FileRule(
        format=FileFormat.POSITIONAL,
        positional_slices=[KeySlice(0, 2), KeySlice(4, 7)],
        encoding='utf-8',
    )
    keys = extract_keys(f, rule)
    assert 'AB123' in keys
    assert 'CD456' in keys


def test_extract_delimited(tmp_path):
    """Test extracting keys from a delimited file."""
    f = tmp_path / 'source.txt'
    f.write_text('X;Y;Z\nA;B;C\n', encoding='utf-8')
    rule = FileRule(
        format=FileFormat.DELIMITED,
        delimiter=';',
        column_indices=[0, 2],
        encoding='utf-8',
    )
    keys = extract_keys(f, rule)
    assert 'XZ' in keys
    assert 'AC' in keys


def test_extract_missing_file():
    """Test that extracting from a non-existent
    file raises FileNotFoundError."""
    rule = FileRule(format=FileFormat.POSITIONAL,
                    positional_slices=[KeySlice(0, 2)])
    with pytest.raises(FileNotFoundError):
        extract_keys(Path('nonexistent.txt'), rule)


def test_extract_with_transform(tmp_path):
    """Test that the transform function is applied to extracted keys."""
    f = tmp_path / 'source.txt'
    f.write_text('ab  cd  \n', encoding='utf-8')
    rule = FileRule(
        format=FileFormat.POSITIONAL,
        positional_slices=[KeySlice(0, 2), KeySlice(4, 6)],
        encoding='utf-8',
        transform=lambda k: k.upper(),
    )
    keys = extract_keys(f, rule)
    assert 'ABCD' in keys


# ── Key store ───────────────────────────────────────────────────────────

def test_save_and_load_keys(tmp_path):
    """Test that keys can be saved to and loaded from a file."""
    keys = {'KEY1', 'KEY2', 'KEY3'}
    path = tmp_path / 'keys.txt'
    save_keys(keys, path)
    loaded = load_keys(path)
    assert loaded == keys


def test_load_keys_missing_file():
    """Test that loading keys from a non-existent
    file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_keys(Path('nonexistent_keys.txt'))


# ── Checker ─────────────────────────────────────────────────────────────

def test_check_delimited(tmp_path):
    """Test checking a delimited file against valid keys."""
    # Target: key = col 0 + col 1
    target = tmp_path / 'target.txt'
    target.write_text('A;B;extra\nC;D;extra\nE;F;extra\n', encoding='utf-8')

    rule = FileRule(
        format=FileFormat.DELIMITED,
        delimiter=';',
        column_indices=[0, 1],
        encoding='utf-8',
    )
    valid_keys = {'AB', 'EF'}   # CD is not valid

    output = tmp_path / 'result.txt'
    result = check_file(target, output, rule, valid_keys)

    assert result.total == 3
    assert result.ok_count == 2
    assert result.cancel_count == 1

    lines = output.read_text(encoding='utf-8').splitlines()
    assert lines[0].endswith(OK_MARKER)
    assert lines[1].endswith(CANCEL_MARKER)
    assert lines[2].endswith(OK_MARKER)


def test_check_summary_percentages(tmp_path):
    """Test that the summary percentages are calculated correctly."""
    target = tmp_path / 't.txt'
    target.write_text('A;B\nC;D\n', encoding='utf-8')
    rule = FileRule(
        format=FileFormat.DELIMITED,
        delimiter=';',
        column_indices=[0, 1],
        encoding='utf-8',
    )
    result = check_file(target, tmp_path / 'out.txt', rule, valid_keys={'AB'})
    assert result.ok_pct == 50.0
    assert result.cancel_pct == 50.0
