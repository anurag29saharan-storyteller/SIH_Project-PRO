"""
Production-grade rotating logger with console and file handlers.
Logs all API requests, fallback events, errors, and audit events to logs/sif_app.log.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "sif_app.log"

_LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

root_logger = logging.getLogger("sif_platform")
root_logger.setLevel(logging.INFO)

if not root_logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Rotating file handler (10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def get_logger(name: str = "sif_platform") -> logging.Logger:
    """Returns a child logger instance for a given module."""
    return logging.getLogger(f"sif_platform.{name}")
