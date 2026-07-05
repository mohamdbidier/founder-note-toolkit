"""Tests for storage path mapping and directory resolution."""

from pathlib import Path

from fnt.services.storage import StorageService


def test_storage_service_paths(tmp_path: Path) -> None:
    """Test storage service directory creation and path resolutions."""
    storage = StorageService(download_dir=tmp_path)

    episode_title = "My Cool Episode! :)"
    ep_dir = storage.get_episode_dir(episode_title)

    # Path should be sanitized
    assert ep_dir.name == "My_Cool_Episode!_)"
    assert ep_dir.exists()

    paths = storage.get_file_paths(episode_title)
    assert paths["clip"] == ep_dir / "clip.mp4"
    assert paths["metadata"] == ep_dir / "metadata.json"
    assert paths["thumbnail"] == ep_dir / "thumbnail.jpg"
