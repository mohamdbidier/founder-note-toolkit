"""FNT Viral Clips Suggestion Command.

Runs AI or fallback heuristics to identify high-virality segments in long-form transcripts.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from fnt.services.analyzer import AnalyzerService

app = typer.Typer(help="Analyze video transcripts to detect viral clips.")
console = Console()


@app.callback(invoke_without_command=True)
def viral(
    ctx: typer.Context,
    transcript_json: Path = typer.Argument(..., help="Path to the saved transcript JSON file"),
) -> None:
    """Analyze a transcript JSON file to identify viral short-form segments."""
    if ctx.invoked_subcommand is not None:
        return

    if not transcript_json.exists():
        console.print(
            f"[bold red]Error:[/bold red] Transcript JSON file not found: {transcript_json}"
        )
        raise typer.Exit(code=1)

    analyzer = AnalyzerService()

    console.print("\n[bold purple]🧠 Analyzing Transcript for Viral Clips...[/bold purple]")
    console.print(f"📄 [bold]Source file:[/bold] {transcript_json.name}\n")

    with console.status(
        "[bold green]Running AI hooks and speech analytics...[/bold green]", spinner="brain"
    ):
        try:
            segments = analyzer.analyze_saved_transcript(transcript_json)
        except Exception as e:
            console.print(f"[bold red]Error during analysis:[/bold red] {e}")
            raise typer.Exit(code=1)

    if not segments:
        console.print(
            "[bold yellow]No segments could be identified. Ensure the transcript contains segments.[/bold yellow]"
        )
        return

    # Render a beautiful Rich Table
    table = Table(
        title="🔥 Suggested Short-Form Viral Clips", show_header=True, header_style="bold magenta"
    )
    table.add_column("Score", justify="center", style="bold green", width=6)
    table.add_column("Range (Start - End)", style="cyan", width=22)
    table.add_column("Title / Idea", style="bold white", width=25)
    table.add_column("Hook Description", style="italic", width=30)
    table.add_column("Virality Rationale", width=40)

    for seg in segments:
        # Format scores with coloring
        score_color = "green"
        if seg.score < 80:
            score_color = "yellow"
        elif seg.score >= 90:
            score_color = "bold green"

        score_text = f"[{score_color}]{seg.score}%[/{score_color}]"

        table.add_row(
            score_text, f"{seg.start_time} - {seg.end_time}", seg.title, seg.hook, seg.reason
        )

    console.print(table)
    console.print()
    console.print(
        "[dim]💡 Tip: Use `fnt clip` with these timestamps to download these specific moments![/dim]\n"
    )
