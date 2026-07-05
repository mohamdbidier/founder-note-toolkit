"""Transcript Download and Parsing Service.

Downloads subtitles from YouTube and converts them to TXT, JSON, and SRT formats.
"""

import json
import re
from pathlib import Path

import yt_dlp

from fnt.models import Transcript, TranscriptItem
from fnt.services.utils import format_timestamp, parse_timestamp
from fnt.settings import get_logger


class TranscriptService:
    """Manages downloading, parsing, and formatting YouTube subtitles."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def download_vtt(
        self, url: str, output_dir: Path, langs: list[str] | None = None
    ) -> list[Path]:
        """Download subtitle files in VTT format using yt-dlp."""
        if not langs:
            langs = ["en", "ar"]

        output_dir.mkdir(parents=True, exist_ok=True)
        # Using a temporary filename pattern for subtitle download
        sub_tmpl = str(output_dir / "sub_temp.%(ext)s")

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": langs,
            "outtmpl": sub_tmpl,
            "quiet": True,
            "no_warnings": True,
        }

        self.logger.info("Downloading subtitles for %s in %s to %s", url, langs, output_dir)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise ValueError("Failed to extract video info for subtitle download")

            # yt-dlp outputs subtitles with suffix like sub_temp.en.vtt or sub_temp.en-US.vtt
            vtt_files = list(output_dir.glob("sub_temp.*.vtt"))

            # Let's clean up name and return the actual downloaded files
            final_files = []
            for f in vtt_files:
                # Find the language code from filename (e.g. sub_temp.en.vtt -> en)
                parts = f.name.split(".")
                lang = parts[-2] if len(parts) >= 3 else "unknown"

                dest = output_dir / f"transcript_{lang}.vtt"
                if dest.exists():
                    dest.unlink()
                f.rename(dest)
                final_files.append(dest)

            return final_files
        except Exception as e:
            self.logger.error("Failed to download subtitles: %s", e)
            raise RuntimeError(f"Subtitle download failed: {e}") from e

    def parse_vtt(self, vtt_path: Path, video_id: str = "unknown") -> Transcript:
        """Parse a WebVTT file and extract clean text and timestamps.

        Args:
            vtt_path: Path to the .vtt subtitle file.
            video_id: Video identifier.
        """
        if not vtt_path.exists():
            raise FileNotFoundError(f"VTT file not found: {vtt_path}")

        # Extract language code from filename
        lang = "en"
        parts = vtt_path.name.split("_")
        if len(parts) > 1:
            lang = parts[1].split(".")[0]

        is_auto = "auto" in vtt_path.name or "auto" in str(vtt_path)

        segments: list[TranscriptItem] = []
        with open(vtt_path, encoding="utf-8") as f:
            content = f.read()

        # Split into blocks separated by blank lines
        blocks = re.split(r"\n\s*\n", content)

        # Pattern to match timestamps: hh:mm:ss.mmm --> hh:mm:ss.mmm
        time_pattern = re.compile(
            r"(\d{2}:\d{2}:\d{2}[.,]\d{3}|\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3}|\d{2}:\d{2}[.,]\d{3})"
        )

        for block in blocks:
            lines = [line.strip() for line in block.split("\n") if line.strip()]
            if not lines:
                continue

            # Look for a line containing the timestamp
            time_match = None
            time_idx = -1
            for idx, line in enumerate(lines):
                time_match = time_pattern.search(line)
                if time_match:
                    time_idx = idx
                    break

            if not time_match or time_idx == -1:
                continue

            # Extract start and end times
            start_str, end_str = time_match.groups()
            start_sec = parse_timestamp(start_str)
            end_sec = parse_timestamp(end_str)
            duration = max(0.0, end_sec - start_sec)

            # Extract text (lines after the timestamp line)
            text_lines = lines[time_idx + 1 :]
            text = " ".join(text_lines)

            # Clean WebVTT formatting tags: <c>, </c>, <00:00:02.100>, etc.
            text = re.sub(r"<[^>]+>", "", text)
            # Clean duplicate whitespaces
            text = re.sub(r"\s+", " ", text).strip()

            if not text:
                continue

            # Check if we can merge adjacent segments that have the exact same text or are very short
            if segments and segments[-1].text == text:
                # Merge with previous if it is duplicate text (common in auto-generated captions)
                prev = segments[-1]
                # Update duration of previous segment
                prev.duration = max(prev.duration, end_sec - prev.start)
            else:
                segments.append(
                    TranscriptItem(
                        text=text,
                        start=start_sec,
                        duration=duration,
                    )
                )

        return Transcript(
            video_id=video_id,
            language=lang,
            is_auto_generated=is_auto,
            segments=segments,
        )

    def save_as_txt(self, transcript: Transcript, output_path: Path) -> None:
        """Save transcript as a clean plain text file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for seg in transcript.segments:
                    f.write(f"[{format_timestamp(seg.start)}] {seg.text}\n")
        except Exception as e:
            raise OSError(f"Failed to save plain text transcript: {e}") from e

    def save_as_json(self, transcript: Transcript, output_path: Path) -> None:
        """Save transcript in structured JSON format."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(transcript.model_dump(), f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise OSError(f"Failed to save JSON transcript: {e}") from e

    def save_as_srt(self, transcript: Transcript, output_path: Path) -> None:
        """Save transcript in SubRip (SRT) format."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for idx, seg in enumerate(transcript.segments, 1):
                    start_str = format_timestamp(seg.start, include_ms=True)
                    end_str = format_timestamp(seg.start + seg.duration, include_ms=True)

                    f.write(f"{idx}\n")
                    f.write(f"{start_str} --> {end_str}\n")
                    f.write(f"{seg.text}\n\n")
        except Exception as e:
            raise OSError(f"Failed to save SRT transcript: {e}") from e
