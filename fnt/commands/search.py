"""FNT Search Command.

Searches local transcript files for keywords and returns timestamp references.
"""

import json
import re
from pathlib import Path

import typer
from rich.console import Console

from fnt.services.utils import format_timestamp, parse_timestamp

app = typer.Typer(help="Search keywords inside saved transcripts.")
console = Console()


def search_json(file_path: Path, query: str) -> list[tuple[str, str]]:
    """Search for query in JSON transcript file."""
    matches = []
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])
    for seg in segments:
        text = seg.get("text", "")
        if query.lower() in text.lower():
            start_sec = seg.get("start", 0.0)
            matches.append((format_timestamp(start_sec), text))
    return matches


def search_srt(file_path: Path, query: str) -> list[tuple[str, str]]:
    """Search for query in SRT subtitle file."""
    matches = []
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content)
    time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->")

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if len(lines) < 3:
            continue

        # line 0: index
        # line 1: timestamp
        # lines 2+: text
        time_match = time_pattern.search(lines[1])
        if not time_match:
            continue

        start_str = time_match.group(1).replace(",", ".")
        text = " ".join(lines[2:])

        if query.lower() in text.lower():
            # Format time to hh:mm:ss
            sec = parse_timestamp(start_str)
            matches.append((format_timestamp(sec), text))

    return matches


def search_txt(file_path: Path, query: str) -> list[tuple[str, str]]:
    """Search for query in formatted TXT transcript file."""
    matches = []
    # Pattern: [00:03:59] text
    pattern = re.compile(r"^\[(\d{2}:\d{2}:\d{2})\]\s*(.*)$")

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                time_str = match.group(1)
                text = match.group(2)
                if query.lower() in text.lower():
                    matches.append((time_str, text))
    return matches


@app.callback(invoke_without_command=True)
def search(
    ctx: typer.Context,
    file_path: Path = typer.Argument(..., help="Path to the transcript file (JSON, SRT, or TXT)"),
    query: str = typer.Argument(..., help="Keyword or phrase to search for"),
) -> None:
    """Search for a keyword inside a transcript and output timestamps."""
    if ctx.invoked_subcommand is not None:
        return

    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        raise typer.Exit(code=1)

    suffix = file_path.suffix.lower()
    matches: list[tuple[str, str]] = []

    try:
        if suffix == ".json":
            matches = search_json(file_path, query)
        elif suffix == ".srt":
            matches = search_srt(file_path, query)
        elif suffix in [".txt", ".log"]:
            matches = search_txt(file_path, query)
        else:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Unknown file format '{suffix}'. Trying line-by-line search."
            )
            matches = search_txt(file_path, query)
    except Exception as e:
        console.print(f"[bold red]Error processing file:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not matches:
        console.print(f"🔍 No matches found for keyword: '[bold yellow]{query}[/bold yellow]'.")
        return

    console.print(
        f"\n🔍 Matches for '[bold cyan]{query}[/bold cyan]' in [dim]{file_path.name}[/dim] ↓\n"
    )
    for timestamp, text in matches:
        # Display the timestamp with a little down arrow and a snippet of the line
        console.print(f"[bold green]{timestamp}[/bold green] [dim]↓[/dim]")
        console.print(f'  [italic]"{text}"[/italic]\n')

    console.print(f"[bold magenta]Total matches:[/bold magenta] {len(matches)}\n")
