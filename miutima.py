#!/usr/bin/env python3
"""
miutima v1.1.0
A smart interactive YouTube media downloader for Termux and Linux.

Developer: Amir Majd
License: MIT
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import imageio_ffmpeg
import yt_dlp
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from rich.table import Table

APP_NAME = "miutima"
VERSION = "1.1.0"
DEVELOPER = "Amir Majd"
BASE_DIR = Path(__file__).resolve().parent
MP4_DIR = BASE_DIR / "mp4ytd"
MP3_DIR = BASE_DIR / "mp3ytd"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "video_quality": 720,
    "audio_quality": 192,
    "embed_thumbnail": False,
    "embed_metadata": True,
    "subtitle": False,
    "subtitle_language": "en",
}

console = Console()


def banner() -> None:
    console.print(
        Panel.fit(
            f"[bold cyan]WELCOME TO MIUTIMA v1.1[/bold cyan]\n"
            f"[white]Developer : {DEVELOPER}[/white]\n"
            f"[white]Smart Downloader • Clipboard • Inspector • History[/white]",
            border_style="cyan",
        )
    )


def ensure_directories() -> None:
    MP4_DIR.mkdir(parents=True, exist_ok=True)
    MP3_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_json(CONFIG_FILE, DEFAULT_CONFIG)
    if not HISTORY_FILE.exists():
        save_json(HISTORY_FILE, [])


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def config() -> dict[str, Any]:
    data = load_json(CONFIG_FILE, {})
    merged = DEFAULT_CONFIG.copy()
    if isinstance(data, dict):
        merged.update(data)
    return merged


def add_history(url: str, title: str, media_type: str, output: str) -> None:
    items = load_json(HISTORY_FILE, [])
    if not isinstance(items, list):
        items = []
    items.insert(0, {
        "title": title,
        "url": url,
        "type": media_type.upper(),
        "output": output,
        "date": datetime.now().astimezone().isoformat(timespec="seconds"),
    })
    save_json(HISTORY_FILE, items[:100])


def is_supported_url(url: str) -> bool:
    pattern = re.compile(r"^https?://(?:(?:www\.)?youtube\.com|youtu\.be)/", re.I)
    return bool(pattern.match(url.strip()))


def get_ffmpeg() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    return system_ffmpeg or imageio_ffmpeg.get_ffmpeg_exe()


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
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024
    return "Unknown"


def get_info(url: str, flat: bool = False) -> dict[str, Any] | None:
    options = common_options()
    options.update({"skip_download": True, "noplaylist": True, "extract_flat": flat})
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as exc:
        console.print(f"[red]✗ Could not inspect URL:[/red] {exc}")
        return None


def show_info(url: str) -> dict[str, Any] | None:
    info = get_info(url)
    if not info:
        return None
    table = Table(title="Video Inspector", show_header=True)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    duration = int(info.get("duration") or 0)
    mins, secs = divmod(duration, 60)
    hours, mins = divmod(mins, 60)
    duration_text = f"{hours}:{mins:02d}:{secs:02d}" if hours else f"{mins}:{secs:02d}"
    table.add_row("Title", str(info.get("title") or "Unknown"))
    table.add_row("Channel", str(info.get("uploader") or info.get("channel") or "Unknown"))
    table.add_row("Duration", duration_text)
    table.add_row("Views", f"{info.get('view_count'):,}" if info.get("view_count") else "Unknown")
    table.add_row("Uploader", str(info.get("upload_date") or "Unknown"))
    console.print(table)
    return info


def clipboard_url() -> str:
    for command in (("termux-clipboard-get",), ("pbpaste",), ("xclip", "-selection", "clipboard")):
        if shutil.which(command[0]):
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=3)
                value = result.stdout.strip()
                if value:
                    return value
            except (OSError, subprocess.SubprocessError):
                pass
    return ""


def choose_quality() -> int:
    default = int(config().get("video_quality", 720))
    console.print("\n[bold]Video quality:[/bold] 2160, 1440, 1080, 720, 480, 360")
    choice = console.input(f"[bold]Quality [default {default}]: [/bold]").strip()
    if not choice:
        return default
    try:
        value = int(choice)
        if value in {2160, 1440, 1080, 720, 480, 360}:
            return value
    except ValueError:
        pass
    console.print("[yellow]Invalid quality; using default.[/yellow]")
    return default


def choose_audio_quality() -> str:
    default = str(config().get("audio_quality", 192))
    console.print("\n[bold]Audio quality:[/bold] 128, 192, 256, 320 kbps")
    choice = console.input(f"[bold]Bitrate [default {default}]: [/bold]").strip()
    return choice if choice in {"128", "192", "256", "320"} else default


def estimate_size(url: str, media_type: str, height: int | None = None) -> tuple[str, str]:
    options = common_options()
    options.update({"skip_download": True, "noplaylist": True})
    if media_type == "mp3":
        options["format"] = "bestaudio/best"
    else:
        selected = height or 720
        options["format"] = f"bestvideo[height<={selected}]+bestaudio/best[height<={selected}]"
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        size = info.get("filesize") or info.get("filesize_approx")
        return format_bytes(size), info.get("title") or "Untitled"
    except Exception:
        return "Unknown", "Unknown"


def download_media(url: str, media_type: str, height: int | None = None, audio_quality: str = "192") -> tuple[bool, str, str]:
    output_dir = MP3_DIR if media_type == "mp3" else MP4_DIR
    ffmpeg = get_ffmpeg()
    app_config = config()
    progress_task = None
    title = "Download"

    def hook(data: dict[str, Any]) -> None:
        nonlocal progress_task
        if progress_task is None:
            return
        status = data.get("status")
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        downloaded = data.get("downloaded_bytes", 0)
        if status == "downloading":
            progress.update(progress_task, completed=downloaded, total=total or 0)
        elif status == "finished" and total:
            progress.update(progress_task, completed=total, total=total)

    options = common_options()
    options.update({
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "progress_hooks": [hook],
        "ffmpeg_location": ffmpeg,
        "noplaylist": True,
        "writethumbnail": bool(app_config.get("embed_thumbnail")),
        "addmetadata": bool(app_config.get("embed_metadata", True)),
    })
    if app_config.get("subtitle"):
        options.update({
            "writesubtitles": True,
            "subtitleslangs": [str(app_config.get("subtitle_language", "en"))],
            "subtitlesformat": "srt/vtt/best",
        })

    if media_type == "mp3":
        options.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": audio_quality,
            }],
        })
    else:
        selected_height = height or 720
        options.update({
            "format": f"bestvideo[height<={selected_height}]+bestaudio/best[height<={selected_height}]",
            "merge_output_format": "mp4",
        })

    with Progress(
        TextColumn("[bold cyan]{task.description}"), BarColumn(), DownloadColumn(),
        TransferSpeedColumn(), TimeRemainingColumn(), console=console,
    ) as progress:
        progress_task = progress.add_task("Downloading", total=0)
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title") or title
            progress.update(progress_task, description="[green]Completed", refresh=True)
            output = str(output_dir)
            add_history(url, title, media_type, output)
            return True, title, output
        except KeyboardInterrupt:
            console.print("\n[yellow]Download interrupted. Partial files can usually be resumed.[/yellow]")
            return False, title, str(output_dir)
        except Exception as exc:
            console.print(f"[red]✗ Download failed:[/red] {exc}")
            return False, title, str(output_dir)


def download_one(url: str, media_type: str | None = None) -> None:
    if not is_supported_url(url):
        console.print("[red]Invalid YouTube URL.[/red]")
        return
    info = show_info(url)
    if not info:
        return
    if media_type not in {"mp3", "mp4"}:
        media_type = choose_media_type()
        if media_type is None:
            return
    height = choose_quality() if media_type == "mp4" else None
    bitrate = choose_audio_quality() if media_type == "mp3" else "192"
    size, title = estimate_size(url, media_type, height)
    console.print(f"\n[bold]Title:[/bold] {title}\n[bold]Estimated size:[/bold] {size}")
    confirm = console.input("[bold]Start download? [Y/n]: [/bold]").strip().lower()
    if confirm == "n":
        return
    started = time.monotonic()
    success, final_title, output = download_media(url, media_type, height, bitrate)
    if success:
        console.print(f"[green]✓ Downloaded:[/green] {final_title}")
        console.print(f"[dim]Saved to: {output} • {time.monotonic() - started:.1f}s[/dim]")


def choose_media_type() -> str | None:
    table = Table(title="Media Type", show_header=True)
    table.add_column("Option", justify="center", style="cyan")
    table.add_column("Type", style="green")
    table.add_row("1", "Video (MP4)")
    table.add_row("2", "Audio (MP3)")
    console.print(table)
    choice = console.input("[bold]Select [1-2] (q to cancel): [/bold]").strip().lower()
    return {"1": "mp4", "2": "mp3"}.get(choice)


def history_menu() -> None:
    items = load_json(HISTORY_FILE, [])
    if not items:
        console.print("[yellow]No download history yet.[/yellow]")
        return
    table = Table(title="Download History")
    table.add_column("#", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Type")
    table.add_column("Date")
    for i, item in enumerate(items[:20], 1):
        table.add_row(str(i), str(item.get("title", "Unknown"))[:55], str(item.get("type", "")), str(item.get("date", ""))[:19])
    console.print(table)
    choice = console.input("[bold]Enter number to download again, or Enter to return: [/bold]").strip()
    if choice.isdigit() and 1 <= int(choice) <= min(20, len(items)):
        item = items[int(choice) - 1]
        download_one(str(item.get("url", "")), str(item.get("type", "")).lower())


def search_youtube() -> None:
    query = console.input("[bold]YouTube search: [/bold]").strip()
    if not query:
        return
    options = common_options()
    options.update({"extract_flat": True, "skip_download": True})
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(f"ytsearch8:{query}", download=False)
    except Exception as exc:
        console.print(f"[red]Search failed:[/red] {exc}")
        return
    entries = [x for x in info.get("entries", []) if x]
    if not entries:
        console.print("[yellow]No results.[/yellow]")
        return
    table = Table(title=f"YouTube Results: {query}")
    table.add_column("#", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Channel")
    for i, item in enumerate(entries, 1):
        table.add_row(str(i), str(item.get("title", "Unknown"))[:65], str(item.get("channel") or item.get("uploader") or "Unknown")[:30])
    console.print(table)
    choice = console.input("[bold]Select result (Enter to cancel): [/bold]").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(entries):
        item = entries[int(choice) - 1]
        url = item.get("webpage_url") or item.get("url")
        if url and not str(url).startswith("http"):
            url = f"https://www.youtube.com/watch?v={url}"
        download_one(str(url))


def clipboard_mode() -> None:
    value = clipboard_url()
    if not value:
        console.print("[yellow]Clipboard is empty or Termux:API clipboard access is unavailable.[/yellow]")
        console.print("[dim]On Termux, install: pkg install termux-api[/dim]")
        return
    console.print(f"[green]📋 Link detected:[/green] {value}")
    download_one(value)


def settings_menu() -> None:
    data = config()
    while True:
        table = Table(title="Settings")
        table.add_column("Option", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("1", f"Video quality: {data['video_quality']}p")
        table.add_row("2", f"Audio quality: {data['audio_quality']} kbps")
        table.add_row("3", f"Embed metadata: {data['embed_metadata']}")
        table.add_row("4", f"Embed thumbnail: {data['embed_thumbnail']}")
        table.add_row("5", f"Subtitle: {data['subtitle']} ({data['subtitle_language']})")
        table.add_row("6", "Reset settings")
        table.add_row("q", "Return")
        console.print(table)
        choice = console.input("[bold]Select: [/bold]").strip().lower()
        if choice == "q":
            return
        if choice == "1":
            data["video_quality"] = choose_quality()
        elif choice == "2":
            data["audio_quality"] = int(choose_audio_quality())
        elif choice == "3":
            data["embed_metadata"] = not bool(data["embed_metadata"])
        elif choice == "4":
            data["embed_thumbnail"] = not bool(data["embed_thumbnail"])
        elif choice == "5":
            data["subtitle"] = not bool(data["subtitle"])
            if data["subtitle"]:
                lang = console.input("[bold]Subtitle language [en]: [/bold]").strip()
                if lang:
                    data["subtitle_language"] = lang
        elif choice == "6":
            data = DEFAULT_CONFIG.copy()
        save_json(CONFIG_FILE, data)
        console.print("[green]✓ Settings saved.[/green]\n")


def main() -> None:
    ensure_directories()
    console.clear()
    banner()
    while True:
        table = Table(title="Main Menu")
        table.add_column("Option", style="cyan", justify="center")
        table.add_column("Action", style="green")
        table.add_row("1", "🔗 Download URL")
        table.add_row("2", "📋 Clipboard")
        table.add_row("3", "🔎 Search YouTube")
        table.add_row("4", "📚 Download History")
        table.add_row("5", "⚙️ Settings")
        table.add_row("6", "❌ Exit")
        console.print(table)
        choice = console.input("[bold]Select option: [/bold]").strip()
        if choice == "1":
            url = console.input("[bold]YouTube URL: [/bold]").strip()
            download_one(url)
        elif choice == "2":
            clipboard_mode()
        elif choice == "3":
            search_youtube()
        elif choice == "4":
            history_menu()
        elif choice == "5":
            settings_menu()
        elif choice == "6":
            console.print("[cyan]Goodbye.[/cyan]")
            break
        else:
            console.print("[yellow]Invalid selection.[/yellow]")
        console.input("\n[dim]Press Enter to return to the main menu...[/dim]")
        console.clear()
        banner()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Exited by user.[/yellow]")
        sys.exit(0)
