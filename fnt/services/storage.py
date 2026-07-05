"""Storage Management Service for FNT.

Manages folder creation, structured outputs, and filepath resolution.
"""

from pathlib import Path

from fnt.config import load_config
from fnt.services.utils import sanitize_filename


class StorageService:
    """Manages directory layout and content writing for FNT projects."""

    def __init__(self, download_dir: Path | None = None):
        if download_dir:
            self.base_dir = download_dir
        else:
            config = load_config()
            self.base_dir = Path(config.download_folder)

    def get_episode_dir(self, title: str) -> Path:
        """Resolve and create the directory path for an episode.

        Args:
            title: The title of the YouTube video.
        """
        sanitized = sanitize_filename(title)
        episode_dir = self.base_dir / sanitized
        episode_dir.mkdir(parents=True, exist_ok=True)
        return episode_dir

    def get_file_paths(self, title: str) -> dict[str, Path]:
        """Get the dictionary of target output file paths for an episode."""
        ep_dir = self.get_episode_dir(title)
        return {
            "dir": ep_dir,
            "clip": ep_dir / "clip.mp4",
            "transcript_txt": ep_dir / "transcript.txt",
            "transcript_srt": ep_dir / "transcript.srt",
            "transcript_json": ep_dir / "transcript.json",
            "metadata": ep_dir / "metadata.json",
            "thumbnail": ep_dir / "thumbnail.jpg",
        }
