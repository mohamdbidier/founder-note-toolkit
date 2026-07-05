"""FNT Captions Burner Command.

Overlay SRT subtitles directly onto video frames using FFmpeg filters.
"""

from pathlib import Path

import typer
from rich.console import Console

from fnt.services.ffmpeg import FFmpegService

app = typer.Typer(help="Burn subtitles into a video file.")
console = Console()


@app.callback(invoke_without_command=True)
def captions(
    ctx: typer.Context,
    video_path: Path = typer.Argument(..., help="Path to the input video (.mp4) file"),
    srt_path: Path = typer.Argument(..., help="Path to the subtitle (.srt) file"),
    output_video: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save the video with burned captions (defaults to video_name_captions.mp4)",
    ),
) -> None:
    """Burn SRT subtitles directly into a video stream for mobile short-form feeds (TikTok, Shorts)."""
    if ctx.invoked_subcommand is not None:
        return

    if not video_path.exists():
        console.print(f"[bold red]Error:[/bold red] Video file not found: {video_path}")
        raise typer.Exit(code=1)

    if not srt_path.exists():
        console.print(f"[bold red]Error:[/bold red] SRT subtitle file not found: {srt_path}")
        raise typer.Exit(code=1)

    if not output_video:
        output_video = video_path.with_name(f"{video_path.stem}_captions.mp4")

    ffmpeg_service = FFmpegService()

    console.print(f"🎬 [bold]Input Video:[/bold]  [yellow]{video_path}[/yellow]")
    console.print(f"📄 [bold]SRT Subtitles:[/bold] [yellow]{srt_path}[/yellow]")
    console.print(f"📁 [bold]Output Video:[/bold]  [green]{output_video}[/green]\n")

    with console.status(
        "[bold green]Burning subtitles into video stream... (this may take a minute)[/bold green]",
        spinner="aesthetic",
    ):
        try:
            ffmpeg_service.burn_subtitles(video_path, srt_path, output_video)
            console.print(
                "\n🎉 [bold green]Subtitles successfully burned into the video![/bold green]\n"
            )
        except Exception as e:
            console.print(f"\n[bold red]Failed to burn captions:[/bold red] {e}")
            raise typer.Exit(code=1)
