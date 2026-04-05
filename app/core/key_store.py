"""
Manages persistence of the valid-keys set (file B in the workflow).

The keys file is a plain UTF-8 text file with one key per line,
sorted alphabetically for human readability and easy diffing.
"""

from pathlib import Path


def save_keys(keys: set[str], path: Path) -> None:
    """Writes *keys* to *path*, one per line, sorted."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        for key in sorted(keys):
            fh.write(key + '\n')


def load_keys(path: Path) -> set[str]:
    """Reads *path* and returns a set of stripped, non-empty key strings."""
    if not path.exists():
        raise FileNotFoundError(f'Keys file not found: {path}')
    with open(path, encoding='utf-8') as fh:
        return {line.strip() for line in fh if line.strip()}
