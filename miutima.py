#!/usr/bin/env python3
"""miutima v1.1.0 - Smart YouTube media downloader for Windows, Linux and Termux."""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, time
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
MP4_DIR, MP3_DIR = BASE_DIR/"mp4ytd", BASE_DIR/"mp3ytd"
CONFIG_DIR = Path.home()/".config"/APP_NAME
CONFIG_FILE, HISTORY_FILE = CONFIG_DIR/"config.json", CONFIG_DIR/"history.json"
DEFAULT_CONFIG = {"video_quality":720,"audio_quality":192,"embed_thumbnail":False,"embed_metadata":True,"subtitle":False,"subtitle_language":"en"}
console = Console()

def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def load_json(path: Path, default: Any) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return default

def ensure_dirs() -> None:
    MP4_DIR.mkdir(exist_ok=True); MP3_DIR.mkdir(exist_ok=True); CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists(): save_json(CONFIG_FILE, DEFAULT_CONFIG)
    if not HISTORY_FILE.exists(): save_json(HISTORY_FILE, [])

def cfg() -> dict[str, Any]:
    data = load_json(CONFIG_FILE, {})
    out = DEFAULT_CONFIG.copy()
    if isinstance(data, dict): out.update(data)
    return out

def banner() -> None:
    console.print(Panel.fit(f"[bold cyan]MIUTIMA v{VERSION}[/bold cyan]\n[white]Developer: {DEVELOPER}[/white]\n[white]Windows • Linux • Termux[/white]", border_style="cyan"))

def is_url(value: str) -> bool:
    return bool(re.match(r"^https?://(?:(?:www\.)?youtube\.com|youtu\.be)/", value.strip(), re.I))

def clipboard_get() -> str:
    """Read text clipboard using native tools on Windows, Linux and Termux."""
    candidates = []
    if os.name == "nt":
        candidates = [["powershell","-NoProfile","-Command","Get-Clipboard -Raw"], ["cmd","/c","powershell -NoProfile -Command Get-Clipboard -Raw"]]
    elif os.environ.get("TERMUX_VERSION") or shutil.which("termux-clipboard-get"):
        candidates = [["termux-clipboard-get"]]
    if sys.platform.startswith("linux"):
        candidates += [["wl-paste","--no-newline"],["xclip","-selection","clipboard","-o"],["xsel","--clipboard","--output"]]
    for command in candidates:
        if not shutil.which(command[0]): continue
        try:
            p = subprocess.run(command, capture_output=True, text=True, timeout=5)
            if p.returncode == 0 and p.stdout.strip(): return p.stdout.strip()
        except (OSError, subprocess.SubprocessError): pass
    return ""

def add_history(url: str, title: str, media_type: str, output: str) -> None:
    items = load_json(HISTORY_FILE, [])
    if not isinstance(items, list): items = []
    items.insert(0, {"title":title,"url":url,"type":media_type.upper(),"output":output,"date":datetime.now().astimezone().isoformat(timespec="seconds")})
    save_json(HISTORY_FILE, items[:100])

def ffmpeg() -> str:
    return shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()

def common() -> dict[str, Any]:
    return {"socket_timeout":60,"retries":10,"fragment_retries":10,"file_access_retries":10,"continuedl":True,"overwrites":False,"concurrent_fragment_downloads":1,"quiet":True,"no_warnings":True,"noprogress":True}

def inspect_url(url: str) -> dict[str, Any] | None:
    opts = common(); opts.update(skip_download=True,noplaylist=True)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: return ydl.extract_info(url, download=False)
    except Exception as e:
        console.print(f"[red]✗ Inspect failed:[/red] {e}"); return None

def show_info(info: dict[str, Any]) -> None:
    d = int(info.get("duration") or 0); h, rem = divmod(d,3600); m,s = divmod(rem,60)
    duration = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
    t = Table(title="Video Inspector"); t.add_column("Field",style="cyan"); t.add_column("Value",style="green")
    t.add_row("Title",str(info.get("title") or "Unknown")); t.add_row("Channel",str(info.get("channel") or info.get("uploader") or "Unknown")); t.add_row("Duration",duration); t.add_row("Views",f"{info['view_count']:,}" if info.get("view_count") else "Unknown"); t.add_row("Upload date",str(info.get("upload_date") or "Unknown")); console.print(t)

def estimate(url: str, media: str, height: int|None) -> str:
    opts=common(); opts.update(skip_download=True,noplaylist=True); opts["format"]="bestaudio/best" if media=="mp3" else f"bestvideo[height<={height or 720}]+bestaudio/best[height<={height or 720}]"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: i=ydl.extract_info(url,download=False)
        size=i.get("filesize") or i.get("filesize_approx")
        if not size: return "Unknown"
        n=float(size)
        for u in ("B","KB","MB","GB","TB"):
            if n<1024 or u=="TB": return f"{n:.2f} {u}"
            n/=1024
    except Exception: pass
    return "Unknown"

def choose_media() -> str|None:
    t=Table(title="Media Type"); t.add_column("Option",style="cyan"); t.add_column("Type",style="green"); t.add_row("1","Video (MP4)"); t.add_row("2","Audio (MP3)"); console.print(t)
    return {"1":"mp4","2":"mp3"}.get(console.input("Select [1-2]: ").strip())

def choose_video_quality() -> int:
    default=int(cfg()["video_quality"]); console.print("\n[bold]Video quality:[/bold] 2160 1440 1080 720 480 360"); v=console.input(f"Quality [default {default}]: ").strip()
    try: v=int(v or default); return v if v in {2160,1440,1080,720,480,360} else default
    except ValueError: return default

def choose_audio_quality() -> str:
    default=str(cfg()["audio_quality"]); console.print("\n[bold]Audio bitrate:[/bold] 128 192 256 320"); v=console.input(f"Bitrate [default {default}]: ").strip(); return v if v in {"128","192","256","320"} else default

def download(url: str, media: str, height: int|None=None, bitrate: str="192") -> bool:
    c=cfg(); out=MP3_DIR if media=="mp3" else MP4_DIR; task=None
    def hook(d: dict[str,Any]) -> None:
        if task is None: return
        total=d.get("total_bytes") or d.get("total_bytes_estimate") or 0; done=d.get("downloaded_bytes",0); progress.update(task,completed=done,total=total)
    opts=common(); opts.update(outtmpl=str(out/"%(title)s.%(ext)s"),progress_hooks=[hook],ffmpeg_location=ffmpeg(),noplaylist=True,writethumbnail=bool(c["embed_thumbnail"]),addmetadata=bool(c["embed_metadata"]))
    if c["subtitle"]: opts.update(writesubtitles=True,subtitleslangs=[str(c["subtitle_language"])],subtitlesformat="srt/vtt/best")
    if media=="mp3": opts.update(format="bestaudio/best",postprocessors=[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":bitrate}])
    else:
        h=height or 720; opts.update(format=f"bestvideo[height<={h}]+bestaudio/best[height<={h}]",merge_output_format="mp4")
    with Progress(TextColumn("[bold cyan]{task.description}"),BarColumn(),DownloadColumn(),TransferSpeedColumn(),TimeRemainingColumn(),console=console) as progress:
        task=progress.add_task("Downloading",total=0)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl: info=ydl.extract_info(url,download=True)
            title=info.get("title") or "Download"; add_history(url,title,media,str(out)); progress.update(task,description="[green]Completed"); console.print(f"[green]✓ {title}[/green]\n[dim]Saved to: {out}[/dim]"); return True
        except KeyboardInterrupt: console.print("\n[yellow]Interrupted. Resume is enabled.[/yellow]"); return False
        except Exception as e: console.print(f"[red]✗ Download failed:[/red] {e}"); return False

def download_url(url: str, media: str|None=None) -> None:
    if not is_url(url): console.print("[red]Invalid YouTube URL.[/red]"); return
    info=inspect_url(url)
    if not info: return
    show_info(info); media=media or choose_media()
    if not media: return
    h=choose_video_quality() if media=="mp4" else None; b=choose_audio_quality() if media=="mp3" else "192"; console.print(f"[bold]Estimated size:[/bold] {estimate(url,media,h)}")
    if console.input("Start download? [Y/n]: ").strip().lower()=="n": return
    download(url,media,h,b)

def history_menu() -> None:
    items=load_json(HISTORY_FILE,[])
    if not items: console.print("[yellow]No history.[/yellow]"); return
    t=Table(title="Download History"); [t.add_column(x) for x in ("#","Title","Type","Date")]
    for n,i in enumerate(items[:20],1): t.add_row(str(n),str(i.get("title",""))[:60],str(i.get("type","")),str(i.get("date",""))[:19])
    console.print(t); v=console.input("Number to download again (Enter to return): ").strip()
    if v.isdigit() and 1<=int(v)<=min(20,len(items)): i=items[int(v)-1]; download_url(str(i.get("url","")),str(i.get("type","")).lower())

def search_menu() -> None:
    q=console.input("YouTube search: ").strip()
    if not q: return
    o=common(); o.update(extract_flat=True,skip_download=True)
    try:
        with yt_dlp.YoutubeDL(o) as ydl: data=ydl.extract_info("ytsearch8:"+q,download=False)
    except Exception as e: console.print(f"[red]Search failed:[/red] {e}"); return
    entries=[x for x in data.get("entries",[]) if x]; t=Table(title=f"Results: {q}"); t.add_column("#",style="cyan"); t.add_column("Title",style="green"); t.add_column("Channel")
    for n,i in enumerate(entries,1): t.add_row(str(n),str(i.get("title",""))[:65],str(i.get("channel") or i.get("uploader") or "")[:30])
    console.print(t); v=console.input("Select result (Enter to cancel): ").strip()
    if v.isdigit() and 1<=int(v)<=len(entries):
        i=entries[int(v)-1]; u=i.get("webpage_url") or i.get("url"); u=("https://www.youtube.com/watch?v="+str(u)) if u and not str(u).startswith("http") else u; download_url(str(u))

def settings_menu() -> None:
    d=cfg()
    while True:
        t=Table(title="Settings"); t.add_column("Option",style="cyan"); t.add_column("Value",style="green"); t.add_row("1",f"Video quality: {d['video_quality']}p"); t.add_row("2",f"Audio: {d['audio_quality']} kbps"); t.add_row("3",f"Metadata: {d['embed_metadata']}"); t.add_row("4",f"Thumbnail: {d['embed_thumbnail']}"); t.add_row("5",f"Subtitle: {d['subtitle']} ({d['subtitle_language']})"); t.add_row("6","Reset"); t.add_row("q","Return"); console.print(t)
        v=console.input("Select: ").strip().lower()
        if v=="q": return
        if v=="1": d["video_quality"]=choose_video_quality()
        elif v=="2": d["audio_quality"]=int(choose_audio_quality())
        elif v=="3": d["embed_metadata"]=not d["embed_metadata"]
        elif v=="4": d["embed_thumbnail"]=not d["embed_thumbnail"]
        elif v=="5": d["subtitle"]=not d["subtitle"]; d["subtitle_language"]=console.input("Subtitle language [en]: ").strip() or "en" if d["subtitle"] else d["subtitle_language"]
        elif v=="6": d=DEFAULT_CONFIG.copy()
        save_json(CONFIG_FILE,d); console.print("[green]✓ Saved.[/green]")

def main() -> None:
    ensure_dirs(); console.clear(); banner()
    while True:
        t=Table(title="Main Menu"); t.add_column("Option",style="cyan"); t.add_column("Action",style="green")
        for n,a in [("1","🔗 Download URL"),("2","📋 Clipboard"),("3","🔎 Search YouTube"),("4","📚 History"),("5","⚙️ Settings"),("6","❌ Exit")]: t.add_row(n,a)
        console.print(t); v=console.input("Select: ").strip()
        if v=="1": download_url(console.input("YouTube URL: ").strip())
        elif v=="2":
            u=clipboard_get(); download_url(u) if u else console.print("[yellow]Clipboard unavailable/empty.[/yellow]")
        elif v=="3": search_menu()
        elif v=="4": history_menu()
        elif v=="5": settings_menu()
        elif v=="6": break
        else: console.print("[yellow]Invalid selection.[/yellow]")
        console.input("\nPress Enter..."); console.clear(); banner()

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: console.print("\n[yellow]Exited.[/yellow]")
