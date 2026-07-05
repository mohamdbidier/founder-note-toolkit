"""FNT Clip Command.

Handles interactive downloading of specific sections of a YouTube video.
"""

from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from fnt.config import load_config
from fnt.services.ffmpeg import FFmpegService
from fnt.services.metadata import MetadataService
from fnt.services.storage import StorageService
from fnt.services.utils import format_timestamp, parse_timestamp
from fnt.services.youtube import YoutubeService

app = typer.Typer(help="Interactive video downloader and clipper.")
console = Console()


@app.callback(invoke_without_command=True)
def clip(
    ctx: typer.Context,
    url: str | None = typer.Option(None, "--url", "-u", help="YouTube video URL"),
    start: str | None = typer.Option(None, "--start", "-s", help="Start timestamp (e.g. 00:01:30)"),
    end: str | None = typer.Option(None, "--end", "-e", help="End timestamp (e.g. 00:02:15)"),
    name: str | None = typer.Option(
        None, "--name", "-n", help="Output filename (without extension)"
    ),
) -> None:
    """Download a specific part of a YouTube video with rich progress indicators."""
    # Ensure subcommand wasn't invoked
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    yt_service = YoutubeService()
    ffmpeg_service = FFmpegService()
    metadata_service = MetadataService()
    storage_service = StorageService(Path(config.download_folder))

    console.print("[bold purple]🎥 Founder Note Toolkit - Interactive Clipper[/bold purple]\n")

    # Prompt for URL if not provided
    if not url:
        url = typer.prompt("🔗 Enter YouTube Video URL").strip()

    # Step 1: Extract Video Metadata (Show Spinner)
    metadata = None
    with console.status(
        "[bold green]Analyzing video and fetching format options...[/bold green]", spinner="dots"
    ):
        try:
            metadata = yt_service.get_video_metadata(url)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to load video metadata. {e}")
            raise typer.Exit(code=1)

    console.print(f"🎬 [bold]Title:[/bold] {metadata.title}")
    console.print(f"👤 [bold]Channel:[/bold] {metadata.channel}")
    console.print(f"⏱️  [bold]Duration:[/bold] {format_timestamp(metadata.duration)}")
    console.print(f"📈 [bold]Views:[/bold] {metadata.views:,}\n")

    # Prompt for timestamps
    if not start:
        start = typer.prompt(
            "⏱️  Enter start timestamp (e.g. 00:00:00, 01:30, or seconds)", default="00:00:00"
        ).strip()

    if not end:
        end = typer.prompt(
            "⏱️  Enter end timestamp (e.g. 00:01:00, 02:45, or seconds)",
            default=format_timestamp(metadata.duration),
        ).strip()

    if not name:
        name = typer.prompt("📝 Enter output clip name (e.g. viral_clip)", default="clip").strip()

    # Validate range
    try:
        start_sec = parse_timestamp(start)
        end_sec = parse_timestamp(end)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    if start_sec >= end_sec:
        console.print("[bold red]Error:[/bold red] Start timestamp must be before end timestamp.")
        raise typer.Exit(code=1)

    if end_sec > metadata.duration:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] End timestamp ({end}) exceeds video duration ({format_timestamp(metadata.duration)}). Clipping to end of video."
        )
        end_sec = float(metadata.duration)
        end = format_timestamp(end_sec)

    # Set up Folder Structure
    # Downloads/FounderNote/Episode Name/
    paths = storage_service.get_file_paths(metadata.title)
    episode_dir = paths["dir"]
    clip_output_path = episode_dir / f"{name}.mp4"

    console.print(f"\n📂 Saving assets to: [cyan]{episode_dir}[/cyan]")

    # Download Metadata & Thumbnail
    try:
        metadata_service.save_metadata(metadata, paths["metadata"])
        if metadata.thumbnail_url:
            yt_service.download_thumbnail(metadata.thumbnail_url, paths["thumbnail"])
    except Exception as e:
        console.print(f"[bold yellow]Warning:[/bold yellow] Could not save metadata/thumbnail: {e}")

    # Prepare Progress Bar
    download_progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    )

    task_id = download_progress.add_task("Downloading Section", total=100, visible=False)

    def yt_dlp_progress_hook(d: dict[str, Any]) -> None:
        if d["status"] == "downloading":
            download_progress.update(task_id, visible=True)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total:
                percent = (downloaded / total) * 100
                download_progress.update(task_id, completed=percent)
        elif d["status"] == "finished":
            download_progress.update(task_id, completed=100)

    # Download Clip
    vcodec = "unknown"
    with download_progress:
        try:
            vcodec = yt_service.download_clip(
                url=url,
                start_time=start,
                end_time=end,
                preferred_codec=config.preferred_codec,
                output_path=clip_output_path,
                progress_hook=yt_dlp_progress_hook,
            )
        except Exception as e:
            console.print(f"\n[bold red]Error during download:[/bold red] {e}")
            raise typer.Exit(code=1)

    console.print("\n✨ [bold green]Download complete![/bold green]")

    # Post-Process: Codec check & Conversion if AV1
    is_av1 = "av01" in vcodec.lower() or "av1" in vcodec.lower()

    # Also double check with ffprobe just in case
    if not is_av1 and clip_output_path.exists():
        try:
            detected = ffmpeg_service.detect_codecs(clip_output_path)
            if (
                "av1" in detected.get("video", "").lower()
                or "av01" in detected.get("video", "").lower()
            ):
                is_av1 = True
        except Exception:
            pass

    if is_av1:
        console.print(
            "⚠️  [bold yellow]AV1 codec detected.[/bold yellow] Automatically converting to H264 AAC MP4 for compatibility..."
        )
        temp_av1_path = clip_output_path.with_suffix(".av1.temp.mp4")

        with console.status(
            "[bold green]Transcoding video to H264/AAC...[/bold green]", spinner="bouncingBar"
        ):
            try:
                # Rename current output to temp input
                if clip_output_path.exists():
                    clip_output_path.rename(temp_av1_path)

                # Perform conversion
                ffmpeg_service.convert_to_h264_aac(temp_av1_path, clip_output_path)

                # Cleanup temp file
                if temp_av1_path.exists():
                    temp_av1_path.unlink()

                console.print("🎉 [bold green]Successfully converted to H264 AAC MP4![/bold green]")
            except Exception as e:
                console.print(f"[bold red]Transcoding failed:[/bold red] {e}")
                # Restore original if conversion failed
                if temp_av1_path.exists() and not clip_output_path.exists():
                    temp_av1_path.rename(clip_output_path)

    console.print(f"\n🎥 Clip saved at: [bold green]{clip_output_path}[/bold green]\n")
