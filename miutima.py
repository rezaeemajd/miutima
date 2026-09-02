#!/usr/bin/env python3
"""
miutima v1.0.0
A lightweight interactive YouTube media downloader for Termux and Linux.

Developer: Amir Majd
License: MIT
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import imageio_ffmpeg
import yt_dlp
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from rich.table import Table

APP_NAME = "miutima"
VERSION = "1.0.0"
DEVELOPER = "Amir Majd"
BASE_DIR = Path(__file__).resolve().parent
MP4_DIR = BASE_DIR / "mp4ytd"
MP3_DIR = BASE_DIR / "mp3ytd"

console = Console()


def banner() -> None:
    console.print(
        Panel.fit(
            f"[bold cyan]WELCOME TO MIUTIMA v1[/bold cyan]\n"
            f"[white]Developer : {DEVELOPER}[/white]\n"
            f"[white]Project   : {APP_NAME} v1[/white]",
            border_style="cyan",
        )
    )


def ensure_directories() -> None:
    MP4_DIR.mkdir(parents=True, exist_ok=True)
    MP3_DIR.mkdir(parents=True, exist_ok=True)


def is_supported_url(url: str) -> bool:
    pattern = re.compile(r"^https?://(?:(?:www\.)?youtube\.com|youtu\.be)/", re.I)
    return bool(pattern.match(url.strip()))


def get_ffmpeg() -> str:
    """Return a bundled/available FFmpeg executable path."""
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def common_options() -> dict[str, Any]:
    return {
        "socket_timeout": 60,
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 10,
        "continuedl": True,
        "overwrites": False,
        "concurrent_fragment_downloads": 1,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }


def format_bytes(value: float | int | None) -> str:
    if not value:
        return "Unknown"
    size = float(value)
    units = ("B", "KB", "MB", "GB", "TB")
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return "Unknown"


def estimate_size(url: str, media_type: str, height: int | None = None) -> tuple[str, str]:
    options = common_options()
    options.update({"skip_download": True, "noplaylist": False})
    if media_type == "mp3":
        options["format"] = "bestaudio/best"
    else:
        selected = height or 720
        options["format"] = f"bestvideo[height<={selected}]+bestaudio/best[height<={selected}]"

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info.get("entries") if info else None
        if entries:
            entries = [entry for entry in entries if entry]
            if not entries:
                return "Unknown", "Unknown"
            total = sum((entry.get("filesize") or entry.get("filesize_approx") or 0) for entry in entries)
            title = info.get("title") or "Playlist"
            return format_bytes(total), title
        size = info.get("filesize") or info.get("filesize_approx")
        return format_bytes(size), info.get("title") or "Untitled"
    except Exception:
        return "Unknown", "Unknown"


def download_media(url: str, media_type: str, height: int | None = None) -> bool:
    output_dir = MP3_DIR if media_type == "mp3" else MP4_DIR
    ffmpeg = get_ffmpeg()
    progress_task = None

    def hook(data: dict[str, Any]) -> None:
        nonlocal progress_task
        status = data.get("status")
        if status == "downloading" and progress_task is not None:
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            if total:
                progress.update(progress_task, total=total, completed=downloaded)
            else:
                progress.update(progress_task, completed=downloaded)
        elif status == "finished" and progress_task is not None:
            total = data.get("total_bytes") or data.get("downloaded_bytes")
            if total:
                progress.update(progress_task, total=total, completed=total)

    options = common_options()
    options.update({
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "progress_hooks": [hook],
        "ffmpeg_location": ffmpeg,
        "noplaylist": False,
    })

    if media_type == "mp3":
        options.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        selected_height = height or 720
        options.update({
            "format": (
                f"bestvideo[height<={selected_height}]+bestaudio/"
                f"best[height<={selected_height}]"
            ),
            "merge_output_format": "mp4",
        })

    title = "Download"
    with Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        progress_task = progress.add_task("Downloading", total=None)
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title") or title
            progress.update(progress_task, description="[green]Completed", refresh=True)
            return True
        except KeyboardInterrupt:
            console.print("\n[yellow]Download interrupted. A partial file may be resumable.[/yellow]")
            return False
        except Exception as exc:
            console.print(f"[red]✗ Download failed:[/red] {exc}")
            return False


def choose_media_type() -> str | None:
    table = Table(title="Media Type", show_header=True)
    table.add_column("Option", style="cyan", justify="center")
    table.add_column("Type", style="green")
    table.add_row("1", "Video (MP4)")
    table.add_row("2", "Audio (MP3)")
    console.print(table)
    choice = console.input("[bold]Select option [1-2] (q to quit): [/bold]").strip().lower()
    if choice == "q":
        return None
    if choice == "1":
        return "mp4"
    if choice == "2":
        return "mp3"
    console.print("[yellow]Invalid selection.[/yellow]")
    return "invalid"


def choose_quality() -> int | None:
    console.print("\n[bold]Select video quality:[/bold]")
    for value, label in ((2160, "2160p (4K)"), (1440, "1440p"), (1080, "1080p"), (720, "720p"), (480, "480p"), (360, "360p")):
        console.print(f"  [cyan]{value}[/cyan] - {label}")
    choice = console.input("[bold]Quality [default 720]: [/bold]").strip()
    if not choice:
        return 720
    try:
        value = int(choice)
        if value in {2160, 1440, 1080, 720, 480, 360}:
            return value
    except ValueError:
        pass
    console.print("[yellow]Invalid quality; using 720p.[/yellow]")
    return 720


def process_download() -> None:
    media_type = choose_media_type()
    if media_type is None:
        return
    if media_type == "invalid":
        return

    height = choose_quality() if media_type == "mp4" else None
    url = console.input("\n[bold]YouTube URL: [/bold]").strip()
    if not is_supported_url(url):
        console.print("[red]Please enter a valid YouTube URL (youtube.com or youtu.be).[/red]")
        return

    console.print("\n[cyan]Analyzing media...[/cyan]")
    size, title = estimate_size(url, media_type, height)
    console.print(f"[bold]Title:[/bold] {title}\n[bold]Estimated size:[/bold] {size}")

    started = time.monotonic()
    success = download_media(url, media_type, height)
    elapsed = time.monotonic() - started
    if success:
        console.print(f"[green]✓ Downloaded successfully[/green] in {elapsed:.1f}s")
        console.print(f"[dim]Saved to: {MP4_DIR if media_type == 'mp4' else MP3_DIR}[/dim]")


def main() -> None:
    ensure_directories()
    banner()
    console.print("[dim]Termux/Linux friendly • Retry & resume enabled • FFmpeg supported[/dim]\n")

    while True:
        process_download()
        console.print("\n[cyan]Returning to miutima v1 main menu...[/cyan]\n")
        again = console.input("[bold]Press Enter to continue, or q to quit: [/bold]").strip().lower()
        if again == "q":
            console.print("[cyan]Goodbye.[/cyan]")
            break
        console.clear()
        banner()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Exited by user.[/yellow]")
        sys.exit(0)
