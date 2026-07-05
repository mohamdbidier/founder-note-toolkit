"""FNT Global Constants.

Defines default configurations, environment details, and settings.
"""

from pathlib import Path

APP_NAME = "fnt"
CONFIG_DIR = Path.home() / ".fnt"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = CONFIG_DIR / "logs"
LOG_FILE = LOG_DIR / "fnt.log"

DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "FounderNote"

# Codec ordering preferences
CODEC_PREFERENCE = ["avc", "hevc", "vp9", "av1"]

# Terminal styling options
THEME_DEFAULT = "dark"
THEMES = ["dark", "light", "dracula", "nord"]
