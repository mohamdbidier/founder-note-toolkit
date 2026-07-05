"""FNT Info Command.

Displays metadata and available formats for a YouTube video.
"""

import typer
from rich.console import Console
from rich.table import Table

from fnt.services.utils import format_timestamp
from fnt.services.youtube import YoutubeService

app = typer.Typer(help="Display metadata and format options for a YouTube video.")
console = Console()


@app.callback(invoke_without_command=True)
def info(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="YouTube video URL"),
) -> None:
    """Fetch and print video title, duration, channel, views, upload date, thumbnail, and format options."""
    if ctx.invoked_subcommand is not None:
        return

    yt_service = YoutubeService()

    with console.status("[bold green]Fetching video information...[/bold green]", spinner="arc"):
        try:
            metadata = yt_service.get_video_metadata(url)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch video info: {e}")
            raise typer.Exit(code=1)

    # Output detailed information
    console.print("\n[bold purple]ℹ️  Video Information[/bold purple]\n")
    console.print(f"📌 [bold]Title:[/bold]          {metadata.title}")
    console.print(f"👤 [bold]Channel:[/bold]        {metadata.channel}")
    console.print(f"⏱️  [bold]Duration:[/bold]       {format_timestamp(metadata.duration)}")
    console.print(f"📈 [bold]Views:[/bold]          {metadata.views:,}")
    console.print(f"📅 [bold]Upload Date:[/bold]    {metadata.upload_date}")
    console.print(
        f"🖼️  [bold]Thumbnail URL:[/bold]  [link={metadata.thumbnail_url}]{metadata.thumbnail_url}[/link]\n"
    )

    # Format list
    console.print("[bold purple]📊 Video Stream Formats[/bold purple]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Format ID", style="dim", width=10)
    table.add_column("Extension", width=10)
    table.add_column("Resolution", width=12)
    table.add_column("Codec", width=20)
    table.add_column("Estimated Size", justify="right", width=15)

    # Filter unique codec/resolutions to keep display clean and concise
    seen_combinations = set()
    for fmt in metadata.formats:
        combo = (fmt.resolution, fmt.codec)
        if combo in seen_combinations:
            continue
        seen_combinations.add(combo)

        size_str = "Unknown"
        if fmt.filesize_approx:
            size_mb = fmt.filesize_approx / (1024 * 1024)
            size_str = f"{size_mb:.1f} MB"

        table.add_row(fmt.format_id, fmt.extension, fmt.resolution, fmt.codec, size_str)

    console.print(table)
    console.print()
