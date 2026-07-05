"""FNT Convert Command.

Transcodes video files to standardized H264/AAC MP4 formats.
"""

from pathlib import Path

import typer
from rich.console import Console

from fnt.services.converter import ConverterService

app = typer.Typer(help="Convert video files into compatible H264/AAC MP4 streams.")
console = Console()


@app.callback(invoke_without_command=True)
def convert(
    ctx: typer.Context,
    input_video: Path = typer.Argument(..., help="Path to input video file"),
    output_video: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to output video file (defaults to input_name_converted.mp4)",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force transcode even if file is already H264/AAC MP4"
    ),
) -> None:
    """Convert any input video file to highly compatible H264 (video) and AAC (audio) MP4 format."""
    if ctx.invoked_subcommand is not None:
        return

    if not input_video.exists():
        console.print(f"[bold red]Error:[/bold red] Input video file not found: {input_video}")
        raise typer.Exit(code=1)

    if not output_video:
        output_video = input_video.with_name(f"{input_video.stem}_converted.mp4")

    converter = ConverterService()

    console.print(f"🎬 [bold]Input file:[/bold]  [yellow]{input_video}[/yellow]")
    console.print(f"📁 [bold]Output file:[/bold] [green]{output_video}[/green]\n")

    with console.status(
        "[bold green]Analyzing and converting video format...[/bold green]", spinner="bouncingBar"
    ):
        try:
            converted = converter.convert_video(input_video, output_video, force=force)
            if converted:
                console.print(
                    "\n🎉 [bold green]Video successfully converted and saved![/bold green]\n"
                )
            else:
                console.print(
                    "\n✨ [bold green]No action needed. Stream copy complete![/bold green]\n"
                )
        except Exception as e:
            console.print(f"\n[bold red]Conversion failed:[/bold red] {e}")
            raise typer.Exit(code=1)
