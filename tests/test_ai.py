"""Tests for AI and rules-based fallback heuristics."""

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
