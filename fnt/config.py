"""Configuration Management for FNT.

Manages loading, updating, and saving user configuration files.
"""

import json
from typing import Any

from fnt.constants import CONFIG_DIR, CONFIG_FILE, DEFAULT_DOWNLOAD_DIR
from fnt.models import AppConfig


def get_default_config() -> AppConfig:
    """Get the default configuration."""
    return AppConfig(download_folder=str(DEFAULT_DOWNLOAD_DIR), preferred_codec="avc", theme="dark")


def load_config() -> AppConfig:
    """Load configuration from the config file, creating defaults if missing."""
    if not CONFIG_FILE.exists():
        config = get_default_config()
        save_config(config)
        return config

    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            data = json.load(f)

        # Ensure default values for missing keys by loading defaults first
        defaults = get_default_config().model_dump()
        defaults.update(data)
        return AppConfig(**defaults)
    except Exception:
        # If parsing fails, return default configuration
        return get_default_config()


def save_config(config: AppConfig) -> None:
    """Save configuration to the config file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, indent=4)
    except Exception as e:
        # In a real app, logging would occur here; we raise or fail silently
        raise RuntimeError(f"Failed to save config: {e}") from e


def update_config(updates: dict[str, Any]) -> AppConfig:
    """Update configuration with the given fields."""
    config = load_config()
    current_data = config.model_dump()
    current_data.update(updates)

    updated_config = AppConfig(**current_data)
    save_config(updated_config)
    return updated_config
