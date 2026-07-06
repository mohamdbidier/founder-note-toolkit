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

    def validate_clip(self, filepath: Path, expected_duration: float, tolerance: float = 2.0) -> tuple[bool, str | None]:
        """Validate the exported clip.

        Checks:
        - Output file exists
        - Size > 0
        - ffprobe can read it
        - Duration matches expected clip (within tolerance)
        - Video stream exists
        - Audio stream exists
        """
        if not filepath.exists():
            return False, f"Output file does not exist: {filepath}"
        
        try:
            size_bytes = filepath.stat().st_size
            if size_bytes == 0:
                return False, f"Output file is empty (0 bytes): {filepath}"
        except Exception as e:
            return False, f"Failed to access file size: {e}"

        # Run ffprobe to get format and stream info
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(filepath),
        ]
        try:
            import json
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
        except Exception as e:
            return False, f"ffprobe failed to read the file: {e}"

        # Check for video and audio streams
        streams = data.get("streams", [])
        has_video = any(s.get("codec_type") == "video" for s in streams)
        has_audio = any(s.get("codec_type") == "audio" for s in streams)

        if not has_video:
            return False, "Validation failed: Video stream is missing."
        if not has_audio:
            return False, "Validation failed: Audio stream is missing."

        # Check duration
        format_info = data.get("format", {})
        duration_str = format_info.get("duration")
        if not duration_str:
            return False, "Validation failed: Could not determine clip duration."

        try:
            actual_duration = float(duration_str)
        except ValueError:
            return False, f"Validation failed: Invalid duration value '{duration_str}'."

        if abs(actual_duration - expected_duration) > tolerance:
            return False, (
                f"Validation failed: Clip duration ({actual_duration:.1f}s) "
                f"does not match expected duration ({expected_duration:.1f}s)."
            )

        return True, None

    def get_clip_info(self, filepath: Path) -> dict[str, str]:
        """Query file metadata (size, duration, resolution) using ffprobe."""
        info = {"size": "Unknown", "duration": "Unknown", "resolution": "Unknown"}
        if not filepath.exists():
            return info

        import json
        
        try:
            # File size formatted
            size_bytes = filepath.stat().st_size
            if size_bytes < 1024 * 1024:
                info["size"] = f"{size_bytes / 1024:.1f} KB"
            else:
                info["size"] = f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception:
            pass

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(filepath),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            
            # Duration
            duration_str = data.get("format", {}).get("duration")
            if duration_str:
                secs = float(duration_str)
                info["duration"] = f"{secs:.1f}s"

            # Resolution
            for s in data.get("streams", []):
                if s.get("codec_type") == "video":
                    w = s.get("width")
                    h = s.get("height")
                    if w and h:
                        info["resolution"] = f"{w}x{h}"
                        break
        except Exception:
            pass

        return info
