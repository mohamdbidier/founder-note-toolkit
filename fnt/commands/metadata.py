"""FNT Metadata Command.

Downloads metadata for a YouTube video and saves it to a metadata.json file.
"""

from pathlib import Path

import typer
from rich.console import Console

from fnt.config import load_config
from fnt.services.metadata import MetadataService
from fnt.services.storage import StorageService
from fnt.services.youtube import YoutubeService

app = typer.Typer(help="Download and save video metadata.")
console = Console()


@app.callback(invoke_without_command=True)
def metadata(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="YouTube video URL"),
) -> None:
    """Download video metadata and save it to metadata.json in the episode folder."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    yt_service = YoutubeService()
    metadata_service = MetadataService()
    storage_service = StorageService(Path(config.download_folder))

    console.print("[bold purple]📝 Founder Note Toolkit - Metadata Downloader[/bold purple]\n")

    with console.status("[bold green]Downloading video metadata...[/bold green]", spinner="dots"):
        try:
            video_meta = yt_service.get_video_metadata(url)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to download video metadata. {e}")
            raise typer.Exit(code=1)

    # Establish folder and save metadata
    try:
        paths = storage_service.get_file_paths(video_meta.title)
        meta_path = paths["metadata"]

        metadata_service.save_metadata(video_meta, meta_path)

        console.print(f"🎬 [bold]Title:[/bold]          {video_meta.title}")
        console.print(f"👤 [bold]Channel:[/bold]        {video_meta.channel}")
        console.print(f"⏱️  [bold]Duration:[/bold]       {video_meta.duration} seconds")
        console.print(f"📂 [bold]Saving metadata to:[/bold] [cyan]{meta_path}[/cyan]\n")
        console.print("✅ [bold green]Metadata saved successfully![/bold green]\n")
    except Exception as e:
        console.print(f"[bold red]Error saving metadata:[/bold red] {e}")
        raise typer.Exit(code=1)
