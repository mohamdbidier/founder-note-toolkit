"""Helper Utilities for FNT.

Contains string parsing, time calculation, and display helper utilities.
"""

import re


def parse_timestamp(timestamp_str: str) -> float:
    """Parse timestamp string (e.g., '01:02:03', '05:06', or '123') to total seconds.

    Supports formats:
        - hh:mm:ss
        - mm:ss
        - ss
        - hh:mm:ss,ms or hh:mm:ss.ms
    """
    timestamp_str = timestamp_str.strip()
    if not timestamp_str:
        return 0.0

    # If it's a pure number, return it as float
    if re.match(r"^\d+(\.\d+)?$", timestamp_str):
        return float(timestamp_str)

    # Normalize milliseconds separator
    timestamp_str = timestamp_str.replace(",", ".")

    parts = timestamp_str.split(":")
    if len(parts) == 1:
        # Just seconds
        return float(parts[0])
    elif len(parts) == 2:
        # mm:ss
        minutes = float(parts[0])
        seconds = float(parts[1])
        return (minutes * 60) + seconds
    elif len(parts) == 3:
        # hh:mm:ss
        hours = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return (hours * 3600) + (minutes * 60) + seconds
    else:
        raise ValueError(f"Invalid timestamp format: '{timestamp_str}'")


def format_timestamp(seconds: float, include_ms: bool = False) -> str:
    """Convert float seconds to 'hh:mm:ss' format, optionally including milliseconds.

    Formats:
        - include_ms=False: hh:mm:ss
        - include_ms=True: hh:mm:ss,ms
    """
    if seconds < 0:
        seconds = 0.0

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if include_ms:
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def sanitize_filename(name: str) -> str:
    """Sanitize string to be safe for filenames."""
    # Remove emojis, special characters, replace spaces with underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    sanitized = re.sub(r"\s+", "_", sanitized)
    return sanitized.strip("_")
