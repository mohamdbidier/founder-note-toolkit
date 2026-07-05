"""Tests for CLI registration and commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from fnt.cli import app
from fnt.models import VideoMetadata

runner = CliRunner()


def test_cli_help() -> None:
    """Test calling the CLI with --help displays commands and options."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "clip" in result.stdout
    assert "info" in result.stdout
    assert "transcript" in result.stdout
    assert "convert" in result.stdout
    assert "search" in result.stdout
    assert "viral" in result.stdout
    assert "captions" in result.stdout
    assert "titles" in result.stdout
    assert "metadata" in result.stdout
    assert "config" in result.stdout


def test_cli_config_show() -> None:
    """Test that fnt config show prints the config table."""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "download_folder" in result.stdout
    assert "preferred_codec" in result.stdout
    assert "theme" in result.stdout


def test_cli_metadata(tmp_path: Path) -> None:
    """Test the metadata subcommand with mocked YoutubeService."""
    mock_metadata = VideoMetadata(
        title="Mock Video Title",
        url="https://youtube.com/watch?v=mockid",
        duration=120,
        channel="Mock Channel",
        views=9999,
        upload_date="20260705",
        description="Mock Description",
        thumbnail_url="https://example.com/mock.jpg",
        formats=[],
    )

    with (
        patch("fnt.commands.metadata.YoutubeService") as mock_yt_class,
        patch("fnt.commands.metadata.load_config") as mock_load_config,
    ):
        # Configure config mock to use tmp_path
        mock_config = MagicMock()
        mock_config.download_folder = str(tmp_path)
        mock_load_config.return_value = mock_config

        # Configure YouTube service mock
        mock_yt_inst = MagicMock()
        mock_yt_inst.get_video_metadata.return_value = mock_metadata
        mock_yt_class.return_value = mock_yt_inst

        result = runner.invoke(app, ["metadata", "https://youtube.com/watch?v=mockid"])

        assert result.exit_code == 0
        assert "Mock Video Title" in result.stdout
        assert "saved successfully" in result.stdout

        # Check that the metadata file was saved in the right path
        expected_file = tmp_path / "Mock_Video_Title" / "metadata.json"
        assert expected_file.exists()
