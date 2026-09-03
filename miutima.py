#!/usr/bin/env python3
"""miutima v1.1.0 - Smart YouTube media downloader for Windows, Linux and Termux."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import imageio_ffmpeg
import yt_dlp
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from rich.table import Table

APP_NAME, VERSION, DEVELOPER = "miutima", "1.1.0", "Amir Majd"
BASE_DIR = Path(__file__).resolve().parent
MP4_DIR, MP3_DIR = BASE_DIR / "mp4ytd", BASE_DIR / "mp3ytd"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE, HISTORY_FILE = CONFIG_DIR / "config.json", CONFIG_DIR / "history.json"
DEFAULT_CONFIG = {
    "video_quality": 720,
    "audio_quality": 192,
    "embed_thumbnail": False,
    "embed_metadata": True,
    "subtitle": False,
    "subtitle_language": "en",
}
console = Console()


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def ensure_dirs() -> None:
    MP4_DIR.mkdir(parents=True, exist_ok=True)
    MP3_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_json(CONFIG_FILE, DEFAULT_CONFIG)
    if not HISTORY_FILE.exists():
        save_json(HISTORY_FILE, [])


def cfg() -> dict[str, Any]:
    data = load_json(CONFIG_FILE, {})
    out = DEFAULT_CONFIG.copy()
    if isinstance(data, dict):
        out.update(data)
    return out


def banner() -> None:
    console.print(
        Panel.fit(
            f"[bold cyan]MIUTIMA v{VERSION}[/bold cyan]\n"
            f"[white]Developer: {DEVELOPER}[/white]\n"
            "[white]Windows • Linux • Termux[/white]",
            border_style="cyan",
        )
    )


def is_url(value: str) -> bool:
    return bool(re.match(r"^https?://(?:(?:www\.)?youtube\.com|youtu\.be)/", value.strip(), re.I))


def is_wsl() -> bool:
    if not sys.platform.startswith("linux"):
        return False
    try:
        text = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
        return "microsoft" in text or "wsl" in text
    except OSError:
        return False


def run_clipboard(command: list[str]) -> str:
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=5)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def clipboard_get() -> str:
    """Read text clipboard on Windows, WSL, Linux desktop and Termux."""
    commands: list[list[str]] = []

    if os.name == "nt":
        if shutil.which("powershell"):
            commands.append(["powershell", "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard -Raw"])
        if shutil.which("pwsh"):
            commands.append(["pwsh", "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard -Raw"])

    if is_wsl():
        if shutil.which("powershell.exe"):
            commands.append(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard -Raw"])
        if shutil.which("pwsh.exe"):
            commands.append(["pwsh.exe", "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard -Raw"])

    if os.environ.get("TERMUX_VERSION") or shutil.which("termux-clipboard-get"):
        commands.append(["termux-clipboard-get"])

    if sys.platform.startswith("linux"):
        if shutil.which("wl-paste"):
            commands.append(["wl-paste", "--no-newline"])
        if shutil.which("xclip"):
            commands.append(["xclip", "-selection", "clipboard", "-o"])
        if shutil.which("xsel"):
            commands.append(["xsel", "--clipboard", "--output"])

    for command in commands:
        value = run_clipboard(command)
        if value:
            return value
    return ""


def clipboard_hint() -> str:
    if is_wsl():
        return "WSL clipboard: Windows PowerShell integration was unavailable. Make sure powershell.exe is accessible from WSL."
    if os.environ.get("TERMUX_VERSION"):
        return "Termux clipboard: install Termux:API and run: pkg install termux-api"
    if os.name == "nt":
        return "Windows clipboard: PowerShell Get-Clipboard is unavailable."
    return "Linux clipboard: install wl-clipboard, xclip or xsel depending on your desktop session."


def add_history(url: str, title: str, media_type: str, output: str) -> None:
    items = load_json(HISTORY_FILE, [])
    if not isinstance(items, list):
        items = []
    items.insert(
        0,
        {
            "title": title,
            "url": url,
            "type": media_type.upper(),
            "output": output,
            "date": datetime.now().astimezone().isoformat(timespec="seconds"),
        },
    )
    save_json(HISTORY_FILE, items[:100])


def ffmpeg() -> str:
    return shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def common(proxy: str | None = None) -> dict[str, Any]:
    options: dict[str, Any] = {
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
    if proxy is not None:
        options["proxy"] = proxy
    return options


def extract_with_fallback(url: str, options: dict[str, Any]) -> dict[str, Any]:
    """Try normal environment/network settings, then retry once without proxies."""
    errors: list[Exception] = []
    attempts = [options]
    if "proxy" not in options:
        direct = dict(options)
        direct["proxy"] = ""
        attempts.append(direct)

    for attempt in attempts:
        try:
            with yt_dlp.YoutubeDL(attempt) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as exc:
            errors.append(exc)

    raise RuntimeError(str(errors[-1]) if errors else "Unknown yt-dlp error")


def inspect_url(url: str) -> dict[str, Any] | None:
    options = common()
    options.update(skip_download=True, noplaylist=True)
    try:
        return extract_with_fallback(url, options)
    except Exception as exc:
        console.print(f"[red]✗ Inspect failed:[/red] {exc}")
        return None


def show_info(info: dict[str, Any]) -> None:
    duration = int(info.get("duration") or 0)
    hours, rem = divmod(duration, 3600)
    minutes, seconds = divmod(rem, 60)
    formatted = f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"
    table = Table(title="Video Inspector")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Title", str(info.get("title") or "Unknown"))
    table.add_row("Channel", str(info.get("channel") or info.get("uploader") or "Unknown"))
    table.add_row("Duration", formatted)
    table.add_row("Views", f"{info['view_count']:,}" if info.get("view_count") else "Unknown")
    table.add_row("Upload date", str(info.get("upload_date") or "Unknown"))
    console.print(table)


def estimate(url: str, media: str, height: int | None) -> str:
    options = common()
    options.update(skip_download=True, noplaylist=True)
    options["format"] = (
        "bestaudio/best"
        if media == "mp3"
        else f"bestvideo[height<={height or 720}]+bestaudio/best[height<={height or 720}]"
    )
    try:
        info = extract_with_fallback(url, options)
        size = info.get("filesize") or info.get("filesize_approx")
        if not size:
            return "Unknown"
        number = float(size)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if number < 1024 or unit == "TB":
                return f"{number:.2f} {unit}"
            number /= 1024
    except Exception:
        return "Unknown"
    return "Unknown"


def choose_media() -> str | None:
    table = Table(title="Media Type")
    table.add_column("Option", style="cyan")
    table.add_column("Type", style="green")
    table.add_row("1", "Video (MP4)")
    table.add_row("2", "Audio (MP3)")
    console.print(table)
    return {"1": "mp4", "2": "mp3"}.get(console.input("Select [1-2]: ").strip())


def choose_video_quality() -> int:
    default = int(cfg()["video_quality"])
    console.print("\n[bold]Video quality:[/bold] 2160 1440 1080 720 480 360")
    value = console.input(f"Quality [default {default}]: ").strip()
    try:
        selected = int(value or default)
        return selected if selected in {2160, 1440, 1080, 720, 480, 360} else default
    except ValueError:
        return default


def choose_audio_quality() -> str:
    default = str(cfg()["audio_quality"])
    console.print("\n[bold]Audio bitrate:[/bold] 128 192 256 320")
    value = console.input(f"Bitrate [default {default}]: ").strip()
    return value if value in {"128", "192", "256", "320"} else default


def download(url: str, media: str, height: int | None = None, bitrate: str = "192") -> bool:
    config = cfg()
    output_dir = MP3_DIR if media == "mp3" else MP4_DIR
    progress_task = None

    def hook(data: dict[str, Any]) -> None:
        if progress_task is None:
            return
        total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
        done = data.get("downloaded_bytes", 0)
        progress.update(progress_task, completed=done, total=total)

    options = common()
    options.update(
        outtmpl=str(output_dir / "%(title)s.%(ext)s"),
        progress_hooks=[hook],
        ffmpeg_location=ffmpeg(),
        noplaylist=True,
        writethumbnail=bool(config["embed_thumbnail"]),
        addmetadata=bool(config["embed_metadata"]),
    )
    if config["subtitle"]:
        options.update(
            writesubtitles=True,
            subtitleslangs=[str(config["subtitle_language"])],
            subtitlesformat="srt/vtt/best",
        )
    if media == "mp3":
        options.update(
            format="bestaudio/best",
            postprocessors=[
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate,
                }
            ],
        )
    else:
        selected_height = height or 720
        options.update(
            format=f"bestvideo[height<={selected_height}]+bestaudio/best[height<={selected_height}]",
            merge_output_format="mp4",
        )

    with Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        progress_task = progress.add_task("Downloading", total=0)
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
            title = info.get("title") or "Download"
            add_history(url, title, media, str(output_dir))
            progress.update(progress_task, description="[green]Completed")
            console.print(f"[green]✓ {title}[/green]\n[dim]Saved to: {output_dir}[/dim]")
            return True
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Resume is enabled.[/yellow]")
            return False
        except Exception as exc:
            console.print(f"[red]✗ Download failed:[/red] {exc}")
            return False


def download_url(url: str, media: str | None = None) -> None:
    if not is_url(url):
        console.print("[red]Invalid YouTube URL.[/red]")
        return
    info = inspect_url(url)
    if not info:
        return
    show_info(info)
    media = media or choose_media()
    if not media:
        return
    height = choose_video_quality() if media == "mp4" else None
    bitrate = choose_audio_quality() if media == "mp3" else "192"
    console.print(f"[bold]Estimated size:[/bold] {estimate(url, media, height)}")
    if console.input("Start download? [Y/n]: ").strip().lower() == "n":
        return
    download(url, media, height, bitrate)


def history_menu() -> None:
    items = load_json(HISTORY_FILE, [])
    if not items:
        console.print("[yellow]No history.[/yellow]")
        return
    table = Table(title="Download History")
    for column in ("#", "Title", "Type", "Date"):
        table.add_column(column)
    for number, item in enumerate(items[:20], 1):
        table.add_row(
            str(number),
            str(item.get("title", ""))[:60],
            str(item.get("type", "")),
            str(item.get("date", ""))[:19],
        )
    console.print(table)
    value = console.input("Number to download again (Enter to return): ").strip()
    if value.isdigit() and 1 <= int(value) <= min(20, len(items)):
        item = items[int(value) - 1]
        download_url(str(item.get("url", "")), str(item.get("type", "")).lower())


def search_menu() -> None:
    query = console.input("YouTube search: ").strip()
    if not query:
        return

    options = common()
    options.update(extract_flat=True, skip_download=True)
    try:
        data = extract_with_fallback("ytsearch8:" + query, options)
    except Exception as exc:
        console.print(f"[red]Search failed:[/red] {exc}")
        console.print(f"[dim]{clipboard_hint() if is_wsl() else 'Check your Internet connection and any HTTP/HTTPS proxy settings.'}[/dim]")
        return

    entries = [entry for entry in data.get("entries", []) if entry]
    table = Table(title=f"YouTube Results: {query}")
    table.add_column("#", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Channel")
    for number, item in enumerate(entries, 1):
        table.add_row(
            str(number),
            str(item.get("title", ""))[:65],
            str(item.get("channel") or item.get("uploader") or "")[:30],
        )
    console.print(table)
    value = console.input("Select result (Enter to cancel): ").strip()
    if value.isdigit() and 1 <= int(value) <= len(entries):
        item = entries[int(value) - 1]
        url = item.get("webpage_url") or item.get("url")
        if url and not str(url).startswith("http"):
            url = "https://www.youtube.com/watch?v=" + str(url)
        if url:
            download_url(str(url))


def settings_menu() -> None:
    data = cfg()
    while True:
        table = Table(title="Settings")
        table.add_column("Option", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("1", f"Video quality: {data['video_quality']}p")
        table.add_row("2", f"Audio: {data['audio_quality']} kbps")
        table.add_row("3", f"Metadata: {data['embed_metadata']}")
        table.add_row("4", f"Thumbnail: {data['embed_thumbnail']}")
        table.add_row("5", f"Subtitle: {data['subtitle']} ({data['subtitle_language']})")
        table.add_row("6", "Reset")
        table.add_row("q", "Return")
        console.print(table)
        value = console.input("Select: ").strip().lower()
        if value == "q":
            return
        if value == "1":
            data["video_quality"] = choose_video_quality()
        elif value == "2":
            data["audio_quality"] = int(choose_audio_quality())
        elif value == "3":
            data["embed_metadata"] = not data["embed_metadata"]
        elif value == "4":
            data["embed_thumbnail"] = not data["embed_thumbnail"]
        elif value == "5":
            data["subtitle"] = not data["subtitle"]
            if data["subtitle"]:
                data["subtitle_language"] = console.input("Subtitle language [en]: ").strip() or "en"
        elif value == "6":
            data = DEFAULT_CONFIG.copy()
        save_json(CONFIG_FILE, data)
        console.print("[green]✓ Saved.[/green]")


def main() -> None:
    ensure_dirs()
    console.clear()
    banner()
    while True:
        table = Table(title="Main Menu")
        table.add_column("Option", style="cyan")
        table.add_column("Action", style="green")
        for number, action in (
            ("1", "🔗 Download URL"),
            ("2", "📋 Clipboard"),
            ("3", "🔎 Search YouTube"),
            ("4", "📚 History"),
            ("5", "⚙️ Settings"),
            ("6", "❌ Exit"),
        ):
            table.add_row(number, action)
        console.print(table)
        value = console.input("Select: ").strip()
        if value == "1":
            download_url(console.input("YouTube URL: ").strip())
        elif value == "2":
            url = clipboard_get()
            if url:
                download_url(url)
            else:
                console.print("[yellow]Clipboard unavailable or empty.[/yellow]")
                console.print(f"[dim]{clipboard_hint()}[/dim]")
        elif value == "3":
            search_menu()
        elif value == "4":
            history_menu()
        elif value == "5":
            settings_menu()
        elif value == "6":
            break
        else:
            console.print("[yellow]Invalid selection.[/yellow]")
        console.input("\nPress Enter...")
        console.clear()
        banner()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Exited.[/yellow]")
