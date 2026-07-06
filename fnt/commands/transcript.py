"""FNT Transcript Command.

Downloads YouTube video transcripts and saves them in TXT, JSON, and SRT formats.
"""

from pathlib import Path

import typer
from rich.console import Console

from fnt.config import load_config
from fnt.services.storage import StorageService
from fnt.services.transcript import TranscriptService
from fnt.services.youtube import YoutubeService

app = typer.Typer(help="Download and process video transcripts.")
console = Console()


@app.callback(invoke_without_command=True)
def transcript(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="YouTube video URL"),
    languages: str = typer.Option(
        "en,ar", "--lang", "-l", help="Comma-separated language codes to download (e.g. en,ar)"
    ),
    output_format: str = typer.Option(
        "all", "--format", "-f", help="Output format: txt, json, srt, or all"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Override default output directory path"
    ),
) -> None:
    """Download transcript/subtitles (manual or auto-generated) in English and Arabic and format them."""
    if ctx.invoked_subcommand is not None:
        return

    config = load_config()
    yt_service = YoutubeService()
    transcript_service = TranscriptService()
    storage_service = StorageService(output or Path(config.download_folder))

    langs = [lang.strip() for lang in languages.split(",") if lang.strip()]

    # Fetch metadata first to get clean Title
    metadata = None
    with console.status("[bold green]Loading video metadata...[/bold green]", spinner="dots"):
        try:
            metadata = yt_service.get_video_metadata(url)
        except Exception as e:
            from fnt.commands.clip import get_friendly_ytdl_error
            friendly_err = get_friendly_ytdl_error(e)
            console.print(f"[bold red]Error: {friendly_err}[/bold red]")
            raise typer.Exit(code=1)

    # Establish folder
    try:
        paths = storage_service.get_file_paths(metadata.title)
    except PermissionError as e:
        console.print("[bold red]Error: Storage permission denied[/bold red]")
        console.print(str(e))
        raise typer.Exit(code=1)

    episode_dir = paths["dir"]

    console.print(f"🎬 [bold]Title:[/bold] {metadata.title}")
    console.print(f"📂 [bold]Saving transcripts to:[/bold] [cyan]{episode_dir}[/cyan]\n")

    vtt_paths = []
    with console.status(
        "[bold green]Downloading subtitles from YouTube...[/bold green]", spinner="bouncingBar"
    ):
        try:
            vtt_paths = transcript_service.download_vtt(url, episode_dir, langs)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to download subtitles: {e}")
            raise typer.Exit(code=1)

    if not vtt_paths:
        console.print(
            "[bold red]Error:[/bold red] No subtitles found for the requested languages. Please check the video subtitles options."
        )
        raise typer.Exit(code=1)

    # Parse and format the files
    for vtt_file in vtt_paths:
        # Resolve language from filename (e.g., transcript_en.vtt -> en)
        lang = vtt_file.name.split("_")[-1].split(".")[0]

        with console.status(
            f"[bold green]Parsing subtitle stream [{lang}]...[/bold green]", spinner="arc"
        ):
            try:
                parsed_transcript = transcript_service.parse_vtt(vtt_file, video_id=metadata.title)

                # Setup output file names
                txt_out = episode_dir / f"transcript_{lang}.txt"
                json_out = episode_dir / f"transcript_{lang}.json"
                srt_out = episode_dir / f"transcript_{lang}.srt"

                # Also write the default non-suffixed file if it is the primary language (usually English)
                is_primary = lang == langs[0] or len(langs) == 1
                if is_primary:
                    txt_out_primary = paths["transcript_txt"]
                    json_out_primary = paths["transcript_json"]
                    srt_out_primary = paths["transcript_srt"]
                else:
                    txt_out_primary = None
                    json_out_primary = None
                    srt_out_primary = None

                # Write requested formats
                formats_written = []
                fmt_lower = output_format.lower()

                if fmt_lower in ["txt", "all"]:
                    transcript_service.save_as_txt(parsed_transcript, txt_out)
                    formats_written.append("TXT")
                    if txt_out_primary:
                        transcript_service.save_as_txt(parsed_transcript, txt_out_primary)

                if fmt_lower in ["json", "all"]:
                    transcript_service.save_as_json(parsed_transcript, json_out)
                    formats_written.append("JSON")
                    if json_out_primary:
                        transcript_service.save_as_json(parsed_transcript, json_out_primary)

                if fmt_lower in ["srt", "all"]:
                    transcript_service.save_as_srt(parsed_transcript, srt_out)
                    formats_written.append("SRT")
                    if srt_out_primary:
                        transcript_service.save_as_srt(parsed_transcript, srt_out_primary)

                console.print(
                    f"✅ [bold green]Saved transcript [{lang}][/bold green] formats: {', '.join(formats_written)}"
                )

                # Cleanup raw VTT file to keep directories clean
                if vtt_file.exists():
                    vtt_file.unlink()
            except Exception as e:
                console.print(f"[bold red]Error parsing subtitles [{lang}]:[/bold red] {e}")

    console.print("\n🎉 [bold green]Transcript download and processing complete![/bold green]\n")
