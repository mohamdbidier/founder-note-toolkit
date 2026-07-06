"""FNT Title Generation Command.

Generates viral title options using AI models for a specific video section.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from fnt.services.analyzer import AnalyzerService

app = typer.Typer(help="Generate viral short-form titles for a clip.")
console = Console()


@app.callback(invoke_without_command=True)
def titles(
    ctx: typer.Context,
    transcript_json: Path = typer.Argument(..., help="Path to the saved transcript JSON file"),
    start: str = typer.Option("00:00:00", "--start", "-s", help="Start timestamp of the clip"),
    end: str = typer.Option("00:01:00", "--end", "-e", help="End timestamp of the clip"),
) -> None:
    """Generate 5 viral short-form video titles for a specific clip section."""
    if ctx.invoked_subcommand is not None:
        return

    if not transcript_json.exists():
        console.print(
            f"[bold red]Error:[/bold red] Transcript JSON file not found: {transcript_json}"
        )
        raise typer.Exit(code=1)

    import importlib.util
    import os

    from fnt.config import load_config

    config = load_config()
    gemini_key = config.gemini_api_key or os.getenv("GEMINI_API_KEY")
    openai_key = config.openai_api_key or os.getenv("OPENAI_API_KEY")

    gemini_installed = importlib.util.find_spec("google.generativeai") is not None
    openai_installed = importlib.util.find_spec("openai") is not None

    if gemini_key and not gemini_installed:
        console.print(
            "[yellow]Warning: Gemini API key is configured, but 'google-generativeai' is not installed.[/yellow]"
        )
        console.print("To use Gemini, please install AI dependencies: [bold]pip install \"founder-note-toolkit[ai]\"[/bold]\n")
    elif openai_key and not openai_installed:
        console.print(
            "[yellow]Warning: OpenAI API key is configured, but 'openai' is not installed.[/yellow]"
        )
        console.print("To use OpenAI, please install AI dependencies: [bold]pip install \"founder-note-toolkit[ai]\"[/bold]\n")
    elif not gemini_installed and not openai_installed:
        console.print(
            "[yellow]Notice: Optional AI dependencies ('google-generativeai', 'openai') are missing. Using rules-based fallback heuristics.[/yellow]"
        )
        console.print("To enable advanced AI features, run: [bold]pip install \"founder-note-toolkit[ai]\"[/bold]\n")

    analyzer = AnalyzerService()

    console.print(
        f"\n[bold purple]✍️  Generating Title Suggestions for range: [cyan]{start} - {end}[/cyan][/bold purple]"
    )
    console.print(f"📄 [bold]Source file:[/bold] {transcript_json.name}\n")

    with console.status("[bold green]Generating viral hooks...[/bold green]", spinner="dqpb"):
        try:
            suggestions = analyzer.generate_titles_for_segment(transcript_json, start, end)
        except Exception as e:
            console.print(f"[bold red]Error generating titles:[/bold red] {e}")
            raise typer.Exit(code=1)

    if not suggestions:
        console.print(
            "[bold yellow]No titles could be suggested. Ensure the timestamp range contains text.[/bold yellow]"
        )
        return

    # Render suggestions in a nice table
    table = Table(title="💡 Suggested Viral Titles", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan", width=15)
    table.add_column("Suggested Title", style="bold white", width=40)
    table.add_column("Hook Psychology / Description", width=45)

    for _idx, sug in enumerate(suggestions, 1):
        table.add_row(sug.hook_type, sug.title, sug.description)

    console.print(table)
    console.print()
