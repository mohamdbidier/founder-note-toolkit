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
    storage_service = StorageService()
    
    all_passed = True
    android_env = is_android()

    # 1. Verify ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        console.print("✓ [bold green]ffmpeg installed:[/bold green] Yes")
    except (subprocess.SubprocessError, FileNotFoundError):
        console.print("✗ [bold red]ffmpeg installed:[/bold red] No")
        console.print("  [yellow]Recommendation:[/yellow] Install by running: [bold]pkg install ffmpeg[/bold]")
        all_passed = False

    # 2. Verify ffprobe
    try:
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
        console.print("✓ [bold green]ffprobe installed:[/bold green] Yes")
    except (subprocess.SubprocessError, FileNotFoundError):
        console.print("✗ [bold red]ffprobe installed:[/bold red] No")
        console.print("  [yellow]Recommendation:[/yellow] Install by running: [bold]pkg install ffmpeg[/bold]")
        all_passed = False

    # 3. Verify yt-dlp
    try:
        import yt_dlp
        console.print("✓ [bold green]yt-dlp installed:[/bold green] Yes")
    except ImportError:
        console.print("✗ [bold red]yt-dlp installed:[/bold red] No")
        console.print("  [yellow]Recommendation:[/yellow] Install by running: [bold]pip install yt-dlp[/bold]")
        all_passed = False

    # 4. Termux detected
    if android_env:
        if "TERMUX_VERSION" in os.environ:
            console.print(f"✓ [bold green]Termux detected:[/bold green] Yes (version {os.environ.get('TERMUX_VERSION', 'unknown')})")
        else:
            console.print("✓ [bold green]Termux detected:[/bold green] Yes (Android environment)")
    else:
        console.print("- [bold cyan]Termux detected:[/bold cyan] No (Running on non-Android platform)")

    # 5. Android shared storage available
    if android_env:
        base_storage = Path("/storage/emulated/0")
        if base_storage.exists():
            console.print("✓ [bold green]Android shared storage available:[/bold green] Yes")
        else:
            console.print("✗ [bold red]Android shared storage available:[/bold red] No")
            console.print("  [yellow]Recommendation:[/yellow] Ensure Android shared storage mount is configured.")
            all_passed = False
    else:
        console.print("- [bold cyan]Android shared storage available:[/bold cyan] Not applicable")

    # 6. Storage permission granted
    if android_env:
        base_storage = Path("/storage/emulated/0")
        permission_granted = False
        if base_storage.exists():
            try:
                os.listdir(base_storage)
                permission_granted = True
            except (PermissionError, FileNotFoundError):
                pass
        
        if permission_granted:
            console.print("✓ [bold green]Storage permission granted:[/bold green] Yes")
        else:
            console.print("✗ [bold red]Storage permission granted:[/bold red] No")
            console.print("  [yellow]Recommendation:[/yellow] Please run: [bold]termux-setup-storage[/bold] and grant permission.")
            all_passed = False
    else:
        console.print("- [bold cyan]Storage permission granted:[/bold cyan] Not applicable")

    # 7. Write permission to /storage/emulated/0/Download/FounderNote/ (or configured dir on desktop)
    target_write_dir = Path("/storage/emulated/0/Download/FounderNote") if android_env else storage_service.base_dir
    try:
        target_write_dir.mkdir(parents=True, exist_ok=True)
        test_file = target_write_dir / ".fnt_doctor_write_test"
        test_file.touch()
        test_file.unlink()
        console.print(f"✓ [bold green]write permission to {target_write_dir}/:[/bold green] Writable")
    except Exception as e:
        console.print(f"✗ [bold red]write permission to {target_write_dir}/:[/bold red] Not writable ({e})")
        if android_env:
            console.print("  [yellow]Recommendation:[/yellow] Run [bold]termux-setup-storage[/bold] to grant write permissions.")
        all_passed = False

    # 8. Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        console.print(f"✓ [bold green]Python version:[/bold green] {py_version} (Supported)")
    else:
        console.print(f"✗ [bold red]Python version:[/bold red] {py_version} (Unsupported - requires Python >= 3.10)")
        all_passed = False

    # 9. Available Disk Space
    try:
        total, used, free = shutil.disk_usage(target_write_dir)
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
