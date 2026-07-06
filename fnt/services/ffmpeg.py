"""FFmpeg and FFprobe Shell Command Wrapper Service.

Executes video conversions, format checking, and burning captions.
"""

import subprocess
from pathlib import Path

from fnt.settings import get_logger


class FFmpegService:
    """Manages system-level calls to FFmpeg and FFprobe."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def is_installed(self) -> bool:
        """Verify that ffmpeg and ffprobe are available in the system PATH."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def detect_codecs(self, video_path: Path) -> dict[str, str]:
        """Detect video and audio codecs of a video file using ffprobe.

        Returns:
            Dict containing 'video' and 'audio' keys mapping to codec names.
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        codecs = {"video": "unknown", "audio": "none"}

        # Detect video codec
        cmd_v = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:keyval_1=1",
            str(video_path),
        ]
        try:
            res_v = subprocess.run(cmd_v, capture_output=True, text=True, check=True)
            val = res_v.stdout.strip()
            if val:
                codecs["video"] = val.split("=")[-1]
        except subprocess.SubprocessError as e:
            self.logger.warning("ffprobe failed to read video stream info: %s", e)

        # Detect audio codec
        cmd_a = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:keyval_1=1",
            str(video_path),
        ]
        try:
            res_a = subprocess.run(cmd_a, capture_output=True, text=True, check=True)
            val = res_a.stdout.strip()
            if val:
                codecs["audio"] = val.split("=")[-1]
        except subprocess.SubprocessError as e:
            self.logger.warning("ffprobe failed to read audio stream info: %s", e)

        return codecs

    def convert_to_h264_aac(self, input_path: Path, output_path: Path) -> None:
        """Convert any video file to H.264 (video) and AAC (audio) MP4 format."""
        if not input_path.exists():
            raise FileNotFoundError(f"Input video file not found: {input_path}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "22",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_path),
        ]

        self.logger.info("Converting %s to %s (H264/AAC)", input_path, output_path)
        try:
            subprocess.run(cmd, capture_output=True, check=True, text=True)
        except subprocess.CalledProcessError as e:
            self.logger.error("FFmpeg conversion failed: %s\nStderr: %s", e, e.stderr)
            raise RuntimeError(f"FFmpeg conversion failed: {e.stderr}") from e

    def burn_subtitles(self, video_path: Path, srt_path: Path, output_path: Path) -> None:
        """Burn subtitles (.srt) directly into the video stream using FFmpeg's subtitles filter.

        Note: FFmpeg requires paths to be escaped correctly for the filter, especially on Windows.
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not srt_path.exists():
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        # Escape SRT path for FFmpeg subtitles filter syntax.
        # FFmpeg parses this argument through its filtergraph engine, requiring backslashes
        # to be normalized, colons to be escaped (especially on Windows), and single quotes to be escaped.
        abs_path = str(srt_path.resolve()).replace("\\", "/")
        srt_filter_path = abs_path.replace(":", "\\:").replace("'", "'\\\\''")

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            f"subtitles={srt_filter_path}",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "22",
            "-c:a",
            "copy",  # Copy audio stream to avoid re-encoding audio
            str(output_path),
        ]

        self.logger.info("Burning subtitles %s into %s", srt_path, video_path)
        try:
            subprocess.run(cmd, capture_output=True, check=True, text=True)
        except subprocess.CalledProcessError as e:
            self.logger.error("FFmpeg subtitles burn failed: %s\nStderr: %s", e, e.stderr)
            raise RuntimeError(f"FFmpeg burning subtitles failed: {e.stderr}") from e
