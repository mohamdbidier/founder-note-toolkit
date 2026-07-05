"""YouTube Download and Metadata Extraction Service.

Uses yt-dlp to interface with YouTube videos, extracting metadata and downloading clips.
"""

import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yt_dlp

from fnt.models import FormatInfo, VideoMetadata
from fnt.services.utils import parse_timestamp
from fnt.settings import get_logger


class YoutubeService:
    """Manages YouTube communications, downloads, and formatting options."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def get_video_metadata(self, url: str) -> VideoMetadata:
        """Extract all metadata for a given YouTube URL.

        Args:
            url: The YouTube video URL.
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }

        self.logger.info("Extracting metadata for URL: %s", url)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise ValueError("Could not extract info from URL")

                formats: list[FormatInfo] = []
                for fmt in info.get("formats", []):
                    # We want video formats with resolution and codec info
                    vcodec = fmt.get("vcodec", "none")
                    fmt.get("acodec", "none")
                    if vcodec != "none":
                        formats.append(
                            FormatInfo(
                                format_id=fmt.get("format_id", ""),
                                extension=fmt.get("ext", ""),
                                resolution=f"{fmt.get('width', 0)}x{fmt.get('height', 0)}",
                                codec=vcodec,
                                filesize_approx=fmt.get("filesize_approx") or fmt.get("filesize"),
                            )
                        )

                return VideoMetadata(
                    title=info.get("title", "Unknown Title"),
                    url=url,
                    duration=int(info.get("duration", 0)),
                    channel=info.get("uploader", "Unknown Channel"),
                    views=int(info.get("view_count", 0)),
                    upload_date=info.get("upload_date", "Unknown Date"),
                    description=info.get("description", "No description"),
                    thumbnail_url=info.get("thumbnail", ""),
                    formats=formats,
                )
        except Exception as e:
            self.logger.error("Failed to extract metadata: %s", e)
            raise ValueError(f"Failed to fetch video metadata: {e}") from e

    def download_thumbnail(self, url: str, output_path: Path) -> None:
        """Download thumbnail image from URL."""
        try:
            self.logger.info("Downloading thumbnail to %s", output_path)
            urllib.request.urlretrieve(url, str(output_path))
        except Exception as e:
            self.logger.error("Failed to download thumbnail: %s", e)
            raise OSError(f"Failed to download thumbnail: {e}") from e

    def build_format_string(self, preferred_codec: str) -> str:
        """Build format selector based on codec preferences.

        Prefer:
            1. AVC (H264)
            2. HEVC (H265)
            3. VP9
            4. AV1
        """
        codec_mapping = {
            "avc": "bestvideo[vcodec*=avc1]/bestvideo[vcodec*=h264]",
            "hevc": "bestvideo[vcodec*=hev1]/bestvideo[vcodec*=hvc1]",
            "vp9": "bestvideo[vcodec*=vp09]/bestvideo[vcodec*=vp9]",
            "av1": "bestvideo[vcodec*=av01]",
        }

        # Build codec order based on preference
        order = [preferred_codec]
        for c in ["avc", "hevc", "vp9", "av1"]:
            if c not in order:
                order.append(c)

        format_parts = [codec_mapping[c] for c in order if c in codec_mapping]
        # Append best audio, or best format fallback
        format_selector = "/".join(format_parts)
        return f"({format_selector})+bestaudio/best"

    def download_clip(
        self,
        url: str,
        start_time: str,
        end_time: str,
        preferred_codec: str,
        output_path: Path,
        progress_hook: Callable[[dict[str, Any]], None] | None = None,
    ) -> str:
        """Download a specific segment/section of a YouTube video.

        Args:
            url: YouTube video URL.
            start_time: Start timestamp (e.g. 00:01:23).
            end_time: End timestamp (e.g. 00:01:45).
            preferred_codec: Target codec preference.
            output_path: Destination path for mp4 file.
            progress_hook: Callback function for progress updates.

        Returns:
            The downloaded format's codec name (to check if it was AV1).
        """
        start_sec = parse_timestamp(start_time)
        end_sec = parse_timestamp(end_time)

        if start_sec >= end_sec:
            raise ValueError("Start time must be less than end time")

        # Configure yt-dlp format selection
        format_str = self.build_format_string(preferred_codec)
        self.logger.info("Using format selector: %s", format_str)

        # Temporary output pattern
        temp_out = str(output_path.with_suffix(".temp.%(ext)s"))

        ydl_opts = {
            "format": format_str,
            "outtmpl": temp_out,
            "quiet": True,
            "no_warnings": True,
            # Download sections natively using ffmpeg
            "download_ranges": lambda info_dict, ytdl: [
                {"start_time": start_sec, "end_time": end_sec, "title": "clip"}
            ],
            "force_keyframes_at_cuts": True,
            "merge_output_format": "mp4",
        }

        if progress_hook:
            ydl_opts["progress_hooks"] = [progress_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract and download
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise ValueError("Download failed, could not extract info")

                # Reconstruct path that yt-dlp actually output
                # Since we forced mp4 merge output, final merged output is .temp.mp4
                output_path.with_suffix(".temp.mp4")

                # Wait, if only one stream was downloaded, yt-dlp might not run merger,
                # let's look for whatever matches temp_out base
                downloaded_files = list(output_path.parent.glob(f"{output_path.stem}.temp.*"))
                if not downloaded_files:
                    raise FileNotFoundError("Could not find downloaded temporary file")

                temp_file = downloaded_files[0]

                # Check actual downloaded video codec
                # info gets populated. We want to check 'requested_formats' or 'vcodec'
                vcodec = "unknown"
                req_formats = info.get("requested_formats")
                if req_formats:
                    vcodec = req_formats[0].get("vcodec", "unknown")
                else:
                    vcodec = info.get("vcodec", "unknown")

                # Rename temp_file to output_path if no conversion is needed
                # (Or if conversion is needed, we will do it in ffmpeg service)
                if temp_file.exists():
                    if temp_file != output_path:
                        if output_path.exists():
                            output_path.unlink()
                        temp_file.rename(output_path)

                return str(vcodec)
        except Exception as e:
            self.logger.error("Download failed: %s", e)
            raise RuntimeError(f"Error during video download: {e}") from e
