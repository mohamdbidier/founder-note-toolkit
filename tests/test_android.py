"""Tests for Android storage, permissions, validation, and doctor command."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from fnt.cli import app
from fnt.services.ffmpeg import FFmpegService
from fnt.services.storage import StorageService

runner = CliRunner()


def test_android_default_paths() -> None:
    """Test that DEFAULT_DOWNLOAD_DIR is defined and has correct class."""
    from fnt.constants import DEFAULT_DOWNLOAD_DIR
    assert isinstance(DEFAULT_DOWNLOAD_DIR, Path)


def test_cleanup_temp_files(tmp_path: Path) -> None:
    """Test that cleanup_temp_files correctly removes temporary pattern matches."""
    storage = StorageService(download_dir=tmp_path)
    episode_dir = tmp_path / "test_episode"
    episode_dir.mkdir()

    # Create files to keep
    keep_file = episode_dir / "clip.mp4"
    keep_file.touch()

    # Create files to clean
    temp_file1 = episode_dir / "clip.temp.mp4"
    temp_file1.touch()

    temp_file2 = episode_dir / "clip.part"
    temp_file2.touch()

    temp_file3 = episode_dir / "sub.vtt"
    temp_file3.touch()

    storage.cleanup_temp_files(episode_dir)

    assert keep_file.exists()
    assert not temp_file1.exists()
    assert not temp_file2.exists()
    assert not temp_file3.exists()


def test_storage_detection() -> None:
    """Test that check_android_storage detects status of Android storage path access."""
    # Non-android path should pass
    storage = StorageService(download_dir=Path("/some/normal/path"))
    ok, err = storage.check_android_storage()
    assert ok
    assert err is None

    # Path inside /storage/emulated should trigger check and fail when mock exists is False
    storage_emulated = StorageService(download_dir=Path("/storage/emulated/0/Download/FounderNote"))
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        ok, err = storage_emulated.check_android_storage()
        assert not ok
        assert "Android storage is not available" in err


def test_doctor_command() -> None:
    """Test doctor command runs and reports dependencies health."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="version info")
        result = runner.invoke(app, ["doctor"])
        assert "Doctor Health Report" in result.stdout
        assert "Python version" in result.stdout


def test_clip_validation(tmp_path: Path) -> None:
    """Test validation of exported video clips."""
    ffmpeg_service = FFmpegService()

    # 1. Non-existent file
    ok, err = ffmpeg_service.validate_clip(tmp_path / "non_existent.mp4", 10.0)
    assert not ok
    assert "does not exist" in err

    # 2. Empty file
    empty_file = tmp_path / "empty.mp4"
    empty_file.touch()
    ok, err = ffmpeg_service.validate_clip(empty_file, 10.0)
    assert not ok
    assert "is empty" in err

    # 3. ffprobe failures and mocking
    valid_file = tmp_path / "valid.mp4"
    valid_file.write_text("dummy content")

    with patch("subprocess.run") as mock_run:
        # Invalid JSON output
        mock_run.return_value = MagicMock(returncode=0, stdout="invalid json")
        ok, err = ffmpeg_service.validate_clip(valid_file, 10.0)
        assert not ok
        assert "ffprobe failed" in err

        # Missing audio stream
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "streams": [{"codec_type": "video"}],
                "format": {"duration": "10.0"}
            })
        )
        ok, err = ffmpeg_service.validate_clip(valid_file, 10.0)
        assert not ok
        assert "Audio stream is missing" in err

        # Success case with video, audio, and matching duration
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "streams": [{"codec_type": "video"}, {"codec_type": "audio"}],
                "format": {"duration": "10.1"}
            })
        )
        ok, err = ffmpeg_service.validate_clip(valid_file, 10.0)
        assert ok
        assert err is None
