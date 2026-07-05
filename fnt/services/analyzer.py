"""Transcript and Video Analysis Coordination Service.

Coordinates reading transcripts from storage and calling AI routines.
"""

from pathlib import Path

from fnt.models import TitleSuggestion, Transcript, ViralSegment
from fnt.services.ai import AIService
from fnt.services.transcript import TranscriptService
from fnt.settings import get_logger


class AnalyzerService:
    """Orchestrates AI analysis by reading stored records and invoking AIService."""

    def __init__(
        self,
        ai_service: AIService | None = None,
        transcript_service: TranscriptService | None = None,
    ) -> None:
        self.ai = ai_service or AIService()
        self.ts_service = transcript_service or TranscriptService()
        self.logger = get_logger()

    def analyze_saved_transcript(self, json_path: Path) -> list[ViralSegment]:
        """Load a JSON transcript and find viral short-form clips."""
        if not json_path.exists():
            raise FileNotFoundError(f"Transcript JSON file not found: {json_path}")

        try:
            with open(json_path, encoding="utf-8") as f:
                import json

                data = json.load(f)

            transcript = Transcript(**data)
            return self.ai.analyze_viral_segments(transcript)
        except Exception as e:
            self.logger.error("Failed to analyze transcript: %s", e)
            raise ValueError(f"Failed to analyze saved transcript: {e}") from e

    def generate_titles_for_segment(
        self, json_path: Path, start_time: str, end_time: str
    ) -> list[TitleSuggestion]:
        """Generate high-converting titles for a specific time range in a transcript."""
        if not json_path.exists():
            raise FileNotFoundError(f"Transcript JSON file not found: {json_path}")

        from fnt.services.utils import parse_timestamp

        start_sec = parse_timestamp(start_time)
        end_sec = parse_timestamp(end_time)

        try:
            with open(json_path, encoding="utf-8") as f:
                import json

                data = json.load(f)

            transcript = Transcript(**data)

            # Extract transcript text in the requested timestamp range
            matching_texts = []
            for seg in transcript.segments:
                if seg.start >= start_sec and (seg.start + seg.duration) <= end_sec:
                    matching_texts.append(seg.text)

            clip_text = " ".join(matching_texts)
            if not clip_text:
                # If no strict range match, grab closest overlap
                for seg in transcript.segments:
                    if not (seg.start + seg.duration < start_sec or seg.start > end_sec):
                        matching_texts.append(seg.text)
                clip_text = " ".join(matching_texts)

            if not clip_text:
                raise ValueError("No transcript text found in the specified timestamp range.")

            return self.ai.generate_viral_titles(clip_text)
        except Exception as e:
            self.logger.error("Failed to generate titles: %s", e)
            raise ValueError(
                f"Failed to generate titles for range {start_time}-{end_time}: {e}"
            ) from e
