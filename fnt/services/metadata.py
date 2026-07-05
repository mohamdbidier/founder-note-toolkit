"""Metadata Saving and Formatting Service.

Handles serialization and storage of YouTube video metadata records.
"""

import json
from pathlib import Path

from fnt.models import VideoMetadata
from fnt.settings import get_logger


class MetadataService:
    """Manages reading and writing of metadata.json files."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def save_metadata(self, metadata: VideoMetadata, output_path: Path) -> None:
        """Save video metadata to a JSON file.

        Args:
            metadata: The VideoMetadata object to save.
            output_path: Path to target json file.
        """
        try:
            self.logger.info("Saving metadata record to %s", output_path)

            # Extract fields requested by requirements: Title, URL, Duration, Channel, Views, Upload date, Description
            data = {
                "title": metadata.title,
                "url": metadata.url,
                "duration": metadata.duration,
                "channel": metadata.channel,
                "views": metadata.views,
                "upload_date": metadata.upload_date,
                "description": metadata.description,
            }

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error("Failed to save metadata file: %s", e)
            raise OSError(f"Failed to write metadata JSON: {e}") from e

    def load_metadata(self, file_path: Path) -> VideoMetadata:
        """Load and parse metadata from JSON file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            # Default empty list for formats to satisfy VideoMetadata model
            if "formats" not in data:
                data["formats"] = []
            if "thumbnail_url" not in data:
                data["thumbnail_url"] = ""
            return VideoMetadata(**data)
        except Exception as e:
            self.logger.error("Failed to parse metadata file: %s", e)
            raise ValueError(f"Failed to parse metadata: {e}") from e
