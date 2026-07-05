"""Application Settings and Logging Initialization.

Sets up application environment and configures logging.
"""

import logging
import sys
from pathlib import Path

from fnt.constants import LOG_DIR, LOG_FILE


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging to file and optionally stdout.

    Args:
        verbose: If True, set logging level to DEBUG, otherwise INFO.
    """
    log_file_path = LOG_FILE
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Fallback to local project directory if home directory is read-only
        fallback_dir = Path("./.fnt/logs")
        fallback_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = fallback_dir / "fnt.log"

    logger = logging.getLogger("fnt")

    # Reset existing handlers to prevent duplicate logging
    if logger.hasHandlers():
        logger.handlers.clear()

    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    # Formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # File always logs debug details
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If writing to log file fails, we'll log to stderr instead
        print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    # Console Handler (Only errors unless verbose)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING if not verbose else logging.DEBUG)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger() -> logging.Logger:
    """Retrieve the configured fnt logger."""
    return logging.getLogger("fnt")
