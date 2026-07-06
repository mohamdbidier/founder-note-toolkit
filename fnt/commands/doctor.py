"""FNT Doctor Command.

Performs health checks on dependencies, storage permissions, and system environment.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

from fnt.config import load_config
from fnt.constants import is_android
from fnt.services.ffmpeg import FFmpegService
from fnt.services.storage import StorageService

app = typer.Typer(help="Verify FNT dependencies and system environment.")
console = Console()


@app.callback(invoke_without_command=True)
def doctor(ctx: typer.Context) -> None:
    """Run diagnostic checks on system dependencies and environment."""
    if ctx.invoked_subcommand is not None:
        return

    console.print("[bold purple]🩺 Founder Note Toolkit (FNT) - Doctor Health Report[/bold purple]\n")

    config = load_config()
    storage_service = StorageService(Path(config.download_folder))
    ffmpeg_service = FFmpegService()

    all_passed = True

    # 1. Verify ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        console.print("✓ [bold green]ffmpeg:[/bold green] Installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        console.print("✗ [bold red]ffmpeg:[/bold red] Missing or broken")
        console.print("  [yellow]Recommendation:[/yellow] Install by running: [bold]pkg install ffmpeg[/bold]")
        all_passed = False

    # 2. Verify ffprobe
    try:
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
        console.print("✓ [bold green]ffprobe:[/bold green] Installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        console.print("✗ [bold red]ffprobe:[/bold red] Missing or broken")
        console.print("  [yellow]Recommendation:[/yellow] Install by running: [bold]pkg install ffmpeg[/bold]")
        all_passed = False

    # 3. Verify yt-dlp
    try:
        import yt_dlp
        console.print("✓ [bold green]yt-dlp:[/bold green] Installed")
    except ImportError:
        console.print("✗ [bold red]yt-dlp:[/bold red] Missing")
        console.print("  [yellow]Recommendation:[/yellow] Install by running: [bold]pip install yt-dlp[/bold]")
        all_passed = False

    # 4. Verify Android Storage / Storage Permission
    if is_android():
        android_storage_ok, err_msg = storage_service.check_android_storage()
        if android_storage_ok:
            console.print("✓ [bold green]Android storage:[/bold green] Available")
        else:
            console.print("✗ [bold red]Android storage:[/bold red] Not available")
            if err_msg:
                console.print(f"  [yellow]Details:[/yellow]\n  " + err_msg.replace("\n", "\n  "))
            all_passed = False
    else:
        console.print("✓ [bold green]Android storage:[/bold green] Not applicable (non-Android platform)")

    # 5. Verify Write Permission
    # Test writing to download folder
    download_dir = Path(config.download_folder)
    try:
        # Create download folder if it doesn't exist
        download_dir.mkdir(parents=True, exist_ok=True)
        # Try to write a temp file
        test_file = download_dir / ".fnt_doctor_write_test"
        test_file.touch()
        test_file.unlink()
        console.print("✓ [bold green]write permission:[/bold green] Writable")
    except Exception as e:
        console.print(f"✗ [bold red]write permission:[/bold red] Not writable ({e})")
        all_passed = False

    # 6. Verify Python Version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        console.print(f"✓ [bold green]Python version:[/bold green] {py_version} (Supported)")
    else:
        console.print(f"✗ [bold red]Python version:[/bold red] {py_version} (Unsupported - requires Python >= 3.10)")
        all_passed = False

    # 7. Available Disk Space
    try:
        total, used, free = shutil.disk_usage(download_dir)
        free_gb = free / (1024 * 1024 * 1024)
        if free_gb < 1.0:
            console.print(f"⚠️  [bold yellow]available disk space:[/bold yellow] {free_gb:.2f} GB free (Low space!)")
        else:
            console.print(f"✓ [bold green]available disk space:[/bold green] {free_gb:.2f} GB free")
    except Exception as e:
        console.print(f"✗ [bold red]available disk space:[/bold red] Could not verify ({e})")
        all_passed = False

    console.print()
    if all_passed:
        console.print("[bold green]🎉 Your FNT system is healthy and ready to go![/bold green]\n")
    else:
        console.print("[bold red]⚠️  Some checks failed. Please address recommendations above.[/bold red]\n")
        raise typer.Exit(code=1)
