"""
data-check — main entry point

Run:
    python run_check.py

All configuration is in config.py. No CLI arguments are needed.
"""

import sys
from pathlib import Path

import config
from app.core.extractor import extract_keys
from app.core.key_store import save_keys
from app.core.checker import check_file
from app.utils.logger import get_logger

LOG_FILE = str(config.LOG_FILE) if config.LOG_FILE else None
logger = get_logger('data-check', log_file=LOG_FILE)


def main() -> None:
    """FUnction to run the data check process."""
    logger.info('=== data-check started ===')

    # ── Step 1: extract valid keys from all source file groups (A) ──────
    valid_keys: set[str] = set()

    for file_list, rule in config.SOURCE_FILE_GROUPS:
        for filename in file_list:
            path = config.INPUT_FOLDER / filename
            try:
                keys = extract_keys(path, rule)
                valid_keys.update(keys)
                logger.info('  %s → %d keys extracted', filename, len(keys))
            except FileNotFoundError as exc:
                logger.error(str(exc))
                sys.exit(1)
            except Exception as exc:
                logger.error('Failed to extract keys from %s: %s',
                             filename, exc)
                sys.exit(1)

    logger.info('Total unique valid keys: %d', len(valid_keys))

    # ── Step 2: save valid keys to reference file (B) ───────────────────
    save_keys(valid_keys, config.KEYS_FILE)
    logger.info('Valid keys saved → %s', config.KEYS_FILE)

    # ── Step 3: check target file (C) against valid keys ────────────────
    if not config.TARGET_FILE.exists():
        logger.error('Target file not found: %s', config.TARGET_FILE)
        sys.exit(1)

    try:
        result = check_file(
            input_path=config.TARGET_FILE,
            output_path=config.OUTPUT_FILE,
            rule=config.TARGET_RULE,
            valid_keys=valid_keys,
            result_column_name=config.RESULT_COLUMN_NAME,
        )
    except Exception as exc:
        logger.error('Failed to check target file: %s', exc)
        sys.exit(1)

    logger.info('=== Run complete ===')
    logger.info(result.summary())
    print('\n' + result.summary())


if __name__ == '__main__':
    main()
