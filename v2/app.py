#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

HOST = "127.0.0.1"
PORT = int(os.environ.get("MIUTIMA_PORT", "8765"))
ROOT = Path(__file__).resolve().parent
DATA = Path.home() / ".miutima-v2"
PRIVATE_DOWNLOADS = DATA / "downloads"
SHARED_DOWNLOADS = Path.home() / "storage" / "downloads" / "miutima-v2"
HISTORY = DATA / "history.json"
SETTINGS = DATA / "settings.json"
INDEX = ROOT / "web" / "index.html"
MAX_HISTORY = 100
DEFAULT_SETTINGS = {"video_quality": 720, "audio_bitrate": 192}
state = {"running": False, "phase": "idle", "percent": 0, "speed": "", "eta": "", "title": "", "error": "", "started": None, "path": ""}
lock = threading.Lock()


def writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".miutima-write-test"
        probe.write_bytes(b"ok")
        probe.unlink(missing_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def ensure():
    DATA.mkdir(parents=True, exist_ok=True)
    PRIVATE_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    if not HISTORY.exists(): HISTORY.write_text("[]", encoding="utf-8")
    if not SETTINGS.exists(): SETTINGS.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding="utf-8")


def download_dir() -> tuple[Path, str]:
    # Android/Termux shared storage can occasionally reject temporary .part files.
    # Test it first; otherwise use Termux-private storage, which is always writable.
    if writable_dir(SHARED_DOWNLOADS):
        return SHARED_DOWNLOADS, "shared"
    PRIVATE_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    return PRIVATE_DOWNLOADS, "private"


def read_json(path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return default


def valid_url(url):
    return bool(re.match(r"^https?://(?:(?:www\.)?youtube\.com|youtu\.be)/", url.strip(), re.I))


def clipboard():
    try:
        p = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=5)
        if p.returncode == 0:
            return {"text": p.stdout.strip(), "available": True, "message": ""}
        return {"text": "", "available": False, "message": "Termux:API در دسترس نیست یا مجوز کلیپ‌بورد وجود ندارد."}
    except FileNotFoundError:
        return {"text": "", "available": False, "message": "دستور termux-clipboard-get پیدا نشد. بسته termux-api و اپ Termux:API را نصب کنید."}
    except Exception as e:
        return {"text": "", "available": False, "message": str(e)}


def add_history(item):
    items = read_json(HISTORY, [])
    items.insert(0, item)
    HISTORY.write_text(json.dumps(items[:MAX_HISTORY], ensure_ascii=False, indent=2), encoding="utf-8")


def inspect(url):
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True, "socket_timeout": 30}) as y:
        i = y.extract_info(url, download=False)
    return {"title": i.get("title", ""), "channel": i.get("channel") or i.get("uploader") or "", "duration": i.get("duration") or 0, "thumbnail": i.get("thumbnail") or "", "url": url}


def do_download(url, media, quality, bitrate):
    target, storage_mode = download_dir()
    with lock:
        state.update(running=True, phase="starting", percent=0, speed="", eta="", title="", error="", started=time.time(), path=str(target))
    outtmpl = str(target / "%(title)s.%(ext)s")

    def hook(d):
        with lock:
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done = d.get("downloaded_bytes", 0)
                state["percent"] = round(done * 100 / total, 1) if total else 0
                state["speed"] = d.get("_speed_str", "")
                state["eta"] = d.get("_eta_str", "")
                state["phase"] = "downloading"
            elif d.get("status") == "finished":
                state.update(percent=100, phase="processing")

    opts = {
        "quiet": True, "no_warnings": True, "noplaylist": True, "retries": 10,
        "fragment_retries": 10, "continuedl": True, "overwrites": False,
        "concurrent_fragment_downloads": 1, "outtmpl": outtmpl,
        "progress_hooks": [hook], "windowsfilenames": False,
        "restrictfilenames": False,
    }
    if media == "mp3":
        opts.update(format="bestaudio/best", postprocessors=[{"key":"FFmpegExtractAudio", "preferredcodec":"mp3", "preferredquality":str(bitrate)}])
    else:
        opts.update(format=f"bestvideo[height<={int(quality)}]+bestaudio/best[height<={int(quality)}]", merge_output_format="mp4")
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=True)
        title = info.get("title", "Download")
        add_history({"title": title, "url": url, "type": media.upper(), "date": time.strftime("%Y-%m-%d %H:%M:%S"), "path": str(target), "storage": storage_mode})
        with lock: state.update(running=False, phase="done", percent=100, title=title, path=str(target))
    except Exception as e:
        with lock: state.update(running=False, phase="error", error=str(e)[-1600:], path=str(target))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def send(self, code, body, content_type="application/json; charset=utf-8"):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(raw))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(raw)

    def json(self, code, obj): self.send(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def body(self):
        n = int(self.headers.get("Content-Length", "0")); return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/": self.send(200, INDEX.read_bytes(), "text/html; charset=utf-8"); return
        if p == "/manifest.webmanifest": self.send(200, (ROOT/"web"/"manifest.webmanifest").read_bytes(), "application/manifest+json"); return
        if p == "/sw.js": self.send(200, (ROOT/"web"/"sw.js").read_bytes(), "application/javascript; charset=utf-8"); return
        if p == "/api/status":
            with lock: self.json(200, dict(state)); return
        if p == "/api/history": self.json(200, read_json(HISTORY, [])); return
        if p == "/api/settings": self.json(200, read_json(SETTINGS, DEFAULT_SETTINGS)); return
        if p == "/api/clipboard": self.json(200, clipboard()); return
        if p == "/api/storage":
            shared = writable_dir(SHARED_DOWNLOADS)
            self.json(200, {"shared_writable": shared, "shared_path": str(SHARED_DOWNLOADS), "private_path": str(PRIVATE_DOWNLOADS), "active_path": str(download_dir()[0])}); return
        self.send(404, "Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        p = urlparse(self.path).path
        try: data = self.body()
        except Exception: self.json(400, {"error":"JSON نامعتبر"}); return
        if p == "/api/info":
            url = str(data.get("url", "")).strip()
            if not valid_url(url): self.json(400, {"error":"لینک یوتیوب معتبر نیست"}); return
            try: self.json(200, inspect(url))
            except Exception as e: self.json(500, {"error":str(e)[-1200:]})
            return
        if p == "/api/download":
            url = str(data.get("url", "")).strip(); media = str(data.get("media", "mp4"))
            if media not in {"mp4", "mp3"}: self.json(400, {"error":"نوع خروجی نامعتبر است"}); return
            if not valid_url(url): self.json(400, {"error":"لینک یوتیوب معتبر نیست"}); return
            with lock:
                if state["running"]: self.json(409, {"error":"یک دانلود در حال اجراست"}); return
            quality = data.get("quality", 720); bitrate = data.get("bitrate", 192)
            threading.Thread(target=do_download, args=(url, media, quality, bitrate), daemon=True).start()
            self.json(202, {"ok":True}); return
        if p == "/api/settings":
            s = read_json(SETTINGS, DEFAULT_SETTINGS); s.update({k:data[k] for k in DEFAULT_SETTINGS if k in data}); SETTINGS.write_text(json.dumps(s, indent=2), encoding="utf-8"); self.json(200, s); return
        self.send(404, "Not found", "text/plain; charset=utf-8")


if __name__ == "__main__":
    ensure()
    print(f"miutima v2.0.0: http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
