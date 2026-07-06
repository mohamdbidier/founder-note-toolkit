"""Main Entry Point for the FNT CLI.

Defines the core Typer application, registers subcommands, and handles global options.
"""

import typer
from rich.console import Console
from rich.table import Table

from fnt.commands.captions import app as captions_app
from fnt.commands.clip import app as clip_app
from fnt.commands.convert import app as convert_app
from fnt.commands.info import app as info_app
from fnt.commands.metadata import app as metadata_app
from fnt.commands.search import app as search_app
from fnt.commands.titles import app as titles_app
from fnt.commands.transcript import app as transcript_app
from fnt.commands.viral import app as viral_app

# Initialize App
app = typer.Typer(
    name="fnt",
    help="Founder Note Toolkit (FNT) - Turn long videos into viral short-form clips.",
    no_args_is_help=True,
)

console = Console()


app.add_typer(clip_app, name="clip")
app.add_typer(info_app, name="info")
app.add_typer(transcript_app, name="transcript")
app.add_typer(convert_app, name="convert")
app.add_typer(search_app, name="search")
app.add_typer(viral_app, name="viral")
app.add_typer(captions_app, name="captions")
app.add_typer(titles_app, name="titles")
app.add_typer(metadata_app, name="metadata")

# Config Command Group
config_app = typer.Typer(help="Manage FNT configuration settings.")
app.add_typer(config_app, name="config")


@config_app.command(name="show")
def config_show() -> None:
    """Display current configuration parameters."""
    from fnt.config import load_config

    config = load_config()

    table = Table(title="⚙️  FNT Configuration", show_header=True, header_style="bold purple")
    table.add_column("Setting Key", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("download_folder", config.download_folder)
    table.add_row("preferred_codec", config.preferred_codec)
    table.add_row("theme", config.theme)
    table.add_row("gemini_api_key", "********" if config.gemini_api_key else "Not set")
    table.add_row("openai_api_key", "********" if config.openai_api_key else "Not set")

    console.print(table)


@config_app.command(name="set")
def config_set(
    key: str = typer.Argument(
        ..., help="Config key to set (e.g. download_folder, preferred_codec, gemini_api_key)"
    ),
    value: str = typer.Argument(..., help="Value to assign to the configuration key"),
) -> None:
    """Update a configuration value."""
    from fnt.config import update_config
    from fnt.models import AppConfig

    # Verify key exists on config model
    import dataclasses
    valid_keys = [f.name for f in dataclasses.fields(AppConfig)]
    if key not in valid_keys:
        console.print(f"[bold red]Error:[/bold red] '{key}' is not a valid configuration key.")
        console.print(f"Valid keys: {', '.join(valid_keys)}")
        raise typer.Exit(code=1)

    try:
        update_config({key: value})
        console.print(
            f"✅ Configuration updated: [bold cyan]{key}[/bold cyan] = [green]{value}[/green]"
        )
    except Exception as e:
        console.print(f"[bold red]Error updating config:[/bold red] {e}")
        raise typer.Exit(code=1)


@config_app.command(name="get")
def config_get(
    key: str = typer.Argument(..., help="Config key to retrieve"),
) -> None:
    """Read a specific configuration value."""
    from fnt.config import load_config

    config = load_config()

    try:
        val = getattr(config, key)
        if val is None:
            console.print("[italic]Not set[/italic]")
        elif key.endswith("api_key") and val:
            console.print("******** (key is masked)")
        else:
            console.print(val)
    except AttributeError:
        console.print(f"[bold red]Error:[/bold red] Key '{key}' does not exist.")
        raise typer.Exit(code=1)


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable debug level outputs in console/files"
    ),
) -> None:
    """Founder Note Toolkit (FNT) - CLI workflow runner to transform videos to shorts."""
    from fnt.settings import setup_logging

    # Configure global logging levels
    setup_logging(verbose=verbose)


if __name__ == "__main__":
    app()
