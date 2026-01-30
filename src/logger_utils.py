from __future__ import annotations

"""
logger_utils.py
---------------
TASK 4: Logging setup

What it does:
- Writes logs to logs/app.log
- Prints logs in terminal too
- Helps debugging and interview quality
"""

import logging
from pathlib import Path


def setup_logger(name: str = "autodesk") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    Path("logs").mkdir(exist_ok=True)

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # File logging
    fh = logging.FileHandler("logs/app.log", encoding="utf-8")
    fh.setFormatter(fmt)
    fh.setLevel(logging.INFO)

    # Terminal logging
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    sh.setLevel(logging.INFO)

    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger
