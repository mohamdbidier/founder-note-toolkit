"""FNT Data Models.

Defines Pydantic models for settings, metadata, and data transfer.
"""

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """FNT Application Configuration Model."""

    download_folder: str = Field(
        default="",
        description="Default directory for saving downloads",
    )
    preferred_codec: str = Field(
        default="avc",
        description="Preferred codec order ('avc', 'hevc', 'vp9', 'av1')",
    )
    theme: str = Field(
        default="dark",
        description="Terminal interface color theme",
    )
    gemini_api_key: str | None = Field(
        default=None,
        description="Google Gemini AI API Key",
    )
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API Key",
    )


class FormatInfo(BaseModel):
    """Individual format metadata from YouTube video."""

    format_id: str
    extension: str
    resolution: str
    codec: str
    filesize_approx: int | None = None


class VideoMetadata(BaseModel):
    """YouTube Video Metadata Model."""

    title: str
    url: str
    duration: int  # in seconds
    channel: str
    views: int
    upload_date: str
    description: str
    thumbnail_url: str
    formats: list[FormatInfo] = []


class ClipRequest(BaseModel):
    """Model representing an interactive video clipping request."""

    url: str
    start_time: str  # Format: hh:mm:ss or mm:ss
    end_time: str  # Format: hh:mm:ss or mm:ss
    output_name: str


class TranscriptItem(BaseModel):
    """Single line/segment of a video transcript."""

    text: str
    start: float  # in seconds
    duration: float  # in seconds


class Transcript(BaseModel):
    """Full transcript package including metadata and segments."""

    video_id: str
    language: str
    is_auto_generated: bool
    segments: list[TranscriptItem]


class ViralSegment(BaseModel):
    """AI suggested viral clip segment."""

    start_time: str  # Format: hh:mm:ss or mm:ss
    end_time: str  # Format: hh:mm:ss or mm:ss
    title: str
    hook: str
    reason: str
    score: int  # 1-100 rating of virality potential


class TitleSuggestion(BaseModel):
    """AI suggested title for a short-form video."""

    title: str
    hook_type: str  # e.g., Curiosity, Question, Contrast, Shock
    description: str
