"""FNT Data Models.

Defines dataclasses for settings, metadata, and data transfer.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


class ModelMixin:
    """Base mixin to provide serialization helper."""

    def model_dump(self) -> dict[str, Any]:
        from typing import cast
        return cast(dict[str, Any], asdict(self))  # type: ignore[call-overload]


@dataclass
class AppConfig(ModelMixin):
    """FNT Application Configuration Model."""

    download_folder: str = ""
    preferred_codec: str = "avc"
    theme: str = "dark"
    gemini_api_key: str | None = None
    openai_api_key: str | None = None


@dataclass
class FormatInfo(ModelMixin):
    """Individual format metadata from YouTube video."""

    format_id: str
    extension: str
    resolution: str
    codec: str
    filesize_approx: int | None = None


@dataclass
class VideoMetadata(ModelMixin):
    """YouTube Video Metadata Model."""

    title: str
    url: str
    duration: int  # in seconds
    channel: str
    views: int
    upload_date: str
    description: str
    thumbnail_url: str
    formats: list[FormatInfo] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.formats:
            parsed = []
            for item in self.formats:
                if isinstance(item, dict):
                    parsed.append(FormatInfo(**item))
                else:
                    parsed.append(item)
            self.formats = parsed


@dataclass
class ClipRequest(ModelMixin):
    """Model representing an interactive video clipping request."""

    url: str
    start_time: str  # Format: hh:mm:ss or mm:ss
    end_time: str  # Format: hh:mm:ss or mm:ss
    output_name: str


@dataclass
class TranscriptItem(ModelMixin):
    """Single line/segment of a video transcript."""

    text: str
    start: float  # in seconds
    duration: float  # in seconds


@dataclass
class Transcript(ModelMixin):
    """Full transcript package including metadata and segments."""

    video_id: str
    language: str
    is_auto_generated: bool
    segments: list[TranscriptItem]

    def __post_init__(self) -> None:
        if self.segments:
            parsed = []
            for item in self.segments:
                if isinstance(item, dict):
                    parsed.append(TranscriptItem(**item))
                else:
                    parsed.append(item)
            self.segments = parsed


@dataclass
class ViralSegment(ModelMixin):
    """AI suggested viral clip segment."""

    start_time: str  # Format: hh:mm:ss or mm:ss
    end_time: str  # Format: hh:mm:ss or mm:ss
    title: str
    hook: str
    reason: str
    score: int  # 1-100 rating of virality potential


@dataclass
class TitleSuggestion(ModelMixin):
    """AI suggested title for a short-form video."""

    title: str
    hook_type: str  # e.g., Curiosity, Question, Contrast, Shock
    description: str
