"""Video Conversion Coordination Service.

Orchestrates codec detection and H264/AAC MP4 encoding operations.
"""

from pathlib import Path

from fnt.services.ffmpeg import FFmpegService
from fnt.settings import get_logger


class ConverterService:
    """High-level video formatting and codec conversion orchestrator."""

    def __init__(self, ffmpeg_service: FFmpegService | None = None) -> None:
        self.ffmpeg = ffmpeg_service or FFmpegService()
        self.logger = get_logger()

    def convert_video(self, input_path: Path, output_path: Path, force: bool = False) -> bool:
        """Convert a video to H264/AAC MP4.

        Checks existing codecs first. If they are already h264 and aac, it skips or copies.
        Otherwise, converts.

        Args:
            input_path: Path to the source file.
            output_path: Path to the target MP4 file.
            force: If True, force re-encoding even if codecs match.

        Returns:
            True if conversion occurred, False if skipped because codecs matched.
        """
        if not self.ffmpeg.is_installed():
            raise RuntimeError(
                "FFmpeg and FFprobe must be installed on your system to run conversion."
            )

        if not input_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {input_path}")

        codecs = self.ffmpeg.detect_codecs(input_path)
        video_codec = codecs.get("video", "unknown")
        audio_codec = codecs.get("audio", "none")

        self.logger.info("Detected codecs - Video: %s, Audio: %s", video_codec, audio_codec)

        # Check if already H264 / AAC and MP4 extension
        is_h264 = video_codec.lower() in ["h264", "avc", "avc1"]
        is_aac = audio_codec.lower() in ["aac"]
        is_mp4 = input_path.suffix.lower() == ".mp4"

        if is_h264 and is_aac and is_mp4 and not force:
            self.logger.info(
                "Video is already H264 video and AAC audio in MP4. Skipping conversion."
            )
            if input_path.resolve() != output_path.resolve():
                output_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil

                shutil.copy2(input_path, output_path)
            return False

        # Perform transcoding
        self.ffmpeg.convert_to_h264_aac(input_path, output_path)
        return True
