"""Centralised logger — writes to console and optionally to a log file."""

import logging
import os
from pathlib import Path


def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
    """Function to get a logger with the specified
    name and optional log file."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        '[%(asctime)s] %(levelname)s — %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    target = log_file or os.getenv('LOG_FILE')
    if target:
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(target, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
