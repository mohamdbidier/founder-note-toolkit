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
