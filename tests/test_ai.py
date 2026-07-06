from pathlib import Path
from typing import Any

from fnt.models import Transcript, TranscriptItem
from fnt.services.ai import AIService


def test_fallback_analyze_viral() -> None:
    """Test fallback rules engine segment extractor when keys are absent."""
    service = AIService()

    # Construct a transcript
    segments = [
        TranscriptItem(text="Welcome to my video.", start=0.0, duration=2.0),
        TranscriptItem(
            text="Today we are talking about the secret algorithm.", start=2.0, duration=4.0
        ),
        TranscriptItem(text="The algorithm has three parts.", start=6.0, duration=3.0),
        TranscriptItem(text="This failed miserably in the beginning.", start=9.0, duration=4.0),
        TranscriptItem(text="But we learned a huge lesson.", start=13.0, duration=4.0),
        TranscriptItem(text="Why does this matter? Here is why.", start=17.0, duration=5.0),
        TranscriptItem(text="Let me tell you a story about it.", start=22.0, duration=5.0),
        TranscriptItem(text="In the end, it was a massive success.", start=27.0, duration=5.0),
    ]

    transcript = Transcript(
        video_id="test_video", language="en", is_auto_generated=True, segments=segments
    )

    viral_clips = service.analyze_viral_segments(transcript)

    # We should get 3 recommended segments
    assert len(viral_clips) >= 1
    assert viral_clips[0].score > 0
    assert len(viral_clips[0].start_time) == 8  # hh:mm:ss format


def test_fallback_generate_titles() -> None:
    """Test fallback titles generator."""
    service = AIService()

    titles = service.generate_viral_titles("This is a short clip about Replit and python coding.")

    assert len(titles) == 5
    assert titles[0].title.startswith("The Truth About")
    assert titles[0].hook_type == "Curiosity"


def test_graceful_failure_when_ai_missing(capsys: Any) -> None:
    """Verify AIService doesn't crash when AI libraries are missing and key is set."""
    import builtins
    from unittest.mock import patch

    original_import = builtins.__import__

    def fail_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name in ["google.generativeai", "openai"]:
            raise ImportError(f"Mocked import failure for {name}")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fail_import):
        service = AIService()
        # Set dummy keys to trigger client initialization attempt
        service.gemini_key = "dummy-key"
        service.openai_key = "dummy-key"

        # These client getters should return None instead of throwing ImportError
        assert service._get_gemini_client() is None
        assert service._get_openai_client() is None

        captured = capsys.readouterr()
        assert "AI features are not installed." in captured.out
        assert "pip install 'founder-note-toolkit[ai]'" in captured.out


def test_cli_viral_command_notice_when_ai_missing(tmp_path: Path) -> None:
    """Verify that fnt viral command prints a friendly message when AI deps are missing."""
    import json
    from unittest.mock import patch

    from typer.testing import CliRunner

    from fnt.cli import app

    transcript_file = tmp_path / "dummy_transcript.json"
    dummy_data = {
        "video_id": "test_video",
        "language": "en",
        "is_auto_generated": True,
        "segments": [
            {"text": "Welcome to my video.", "start": 0.0, "duration": 2.0},
            {"text": "Today we talk about secrets.", "start": 2.0, "duration": 3.0}
        ]
    }
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f)

    runner = CliRunner()
    
    import importlib.util
    original_find_spec = importlib.util.find_spec

    def mock_find_spec(name: str, package: str | None = None) -> Any:
        if name in ["google.generativeai", "openai"]:
            return None
        return original_find_spec(name, package)

    with patch("importlib.util.find_spec", side_effect=mock_find_spec):
        result = runner.invoke(app, ["viral", str(transcript_file)])
        
        assert result.exit_code == 0
        assert "Optional AI dependencies ('google-generativeai', 'openai') are missing" in result.stdout
        assert "Suggested Short-Form Viral Clips" in result.stdout


def test_cli_titles_command_notice_when_ai_missing(tmp_path: Path) -> None:
    """Verify that fnt titles command prints a friendly message when AI deps are missing."""
    import json
    from unittest.mock import patch

    from typer.testing import CliRunner

    from fnt.cli import app

    transcript_file = tmp_path / "dummy_transcript.json"
    dummy_data = {
        "video_id": "test_video",
        "language": "en",
        "is_auto_generated": True,
        "segments": [
            {"text": "Welcome to my video.", "start": 0.0, "duration": 2.0},
            {"text": "Today we talk about secrets.", "start": 2.0, "duration": 3.0}
        ]
    }
    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f)

    runner = CliRunner()
    
    import importlib.util
    original_find_spec = importlib.util.find_spec

    def mock_find_spec(name: str, package: str | None = None) -> Any:
        if name in ["google.generativeai", "openai"]:
            return None
        return original_find_spec(name, package)

    with patch("importlib.util.find_spec", side_effect=mock_find_spec):
        result = runner.invoke(app, ["titles", "--start", "00:00:00", "--end", "00:00:05", str(transcript_file)])
        
        assert result.exit_code == 0
        assert "Optional AI dependencies ('google-generativeai', 'openai') are missing" in result.stdout
        assert "Suggested Viral Titles" in result.stdout
