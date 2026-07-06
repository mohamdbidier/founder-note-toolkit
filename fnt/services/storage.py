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

    def check_android_storage(self) -> tuple[bool, str | None]:
        """Check if Android storage is initialized and writable."""
        import os
        path_str = str(self.base_dir.absolute())
        # Check if the path targets Android storage
        if path_str.startswith("/storage/emulated") or path_str.startswith("/sdcard"):
            base_storage = Path("/storage/emulated/0")
            if not base_storage.exists():
                return False, (
                    "Android storage is not available.\n"
                    "Run:\n"
                    "termux-setup-storage\n"
                    "then grant permission."
                )
            try:
                os.listdir(base_storage)
            except (PermissionError, FileNotFoundError):
                return False, (
                    "Android storage is not available.\n"
                    "Run:\n"
                    "termux-setup-storage\n"
                    "then grant permission."
                )
            
            # Check write permission to base_dir or nearest existing parent
            curr = self.base_dir
            while curr != curr.parent:
                if curr.exists():
                    try:
                        # Try to write a temp file
                        test_file = curr / ".fnt_perm_test"
                        test_file.touch()
                        test_file.unlink()
                        break
                    except Exception:
                        return False, (
                            "Android storage is not available.\n"
                            "Run:\n"
                            "termux-setup-storage\n"
                            "then grant permission."
                        )
                curr = curr.parent
        return True, None

    def get_episode_dir(self, title: str) -> Path:
        """Resolve and create the directory path for an episode.

        Args:
            title: The title of the YouTube video.
        """
        is_ok, err_msg = self.check_android_storage()
        if not is_ok and err_msg:
            raise PermissionError(err_msg)

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

    def cleanup_temp_files(self, episode_dir: Path) -> None:
        """Remove any temporary or cache files left behind."""
        if not episode_dir.exists():
            return
        patterns = ["*.part", "*_temp.*", "*.temp", "*.temp.*", "*.ytdl", "*.part.*", "*.vtt"]
        for pattern in patterns:
            for file_path in episode_dir.glob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                except Exception:
                    pass
