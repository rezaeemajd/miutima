#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import os
import re
import subprocess
import threading
import time
import unicodedata
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
state = {"running": False, "phase": "idle", "percent": 0, "speed": "", "eta": "", "title": "", "error": "", "started": None, "path": "", "media_url": "", "media_type": "", "file_name": "", "file_size": 0}
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


def storage_info():
    shared = writable_dir(SHARED_DOWNLOADS)
    return shared, SHARED_DOWNLOADS, PRIVATE_DOWNLOADS


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


def safe_title(title: str) -> str:
    title = unicodedata.normalize("NFC", str(title or "Download"))
    title = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", title)
    title = re.sub(r"\s+", " ", title).strip(" .")
    return (title or "Download")[:150]


def transfer_to_shared(source: Path, title: str) -> tuple[Path, str]:
    shared_ok = writable_dir(SHARED_DOWNLOADS)
    if not shared_ok:
        return source, "private"
    ext = source.suffix or ".bin"
    base = safe_title(title)
    destination = SHARED_DOWNLOADS / f"{base}{ext}"
    if destination.exists(): destination = SHARED_DOWNLOADS / f"{base} [{int(time.time())}]{ext}"
    staging = destination.with_name(destination.name + ".miutima-copying")
    try:
        total = source.stat().st_size
        copied = 0
        with source.open("rb") as src, staging.open("wb") as dst:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk: break
                dst.write(chunk); copied += len(chunk)
            dst.flush(); os.fsync(dst.fileno())
        if copied != total or staging.stat().st_size != total:
            raise IOError(f"انتقال فایل ناقص بود ({copied} از {total} بایت).")
        try:
            staging.replace(destination)
        except OSError:
            with staging.open("rb") as src, destination.open("wb") as dst:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk: break
                    dst.write(chunk)
                dst.flush(); os.fsync(dst.fileno())
            staging.unlink(missing_ok=True)
        if destination.stat().st_size != total: raise IOError("اندازه فایل نهایی با فایل دانلودشده یکسان نیست.")
        return destination, "shared"
    except Exception as e:
        try: staging.unlink(missing_ok=True)
        except OSError: pass
        raise RuntimeError(f"انتقال به Downloads اندروید ناموفق بود: {e}") from e


def resolve_final_file(work_dir: Path, prepared: Path, media: str) -> Path:
    preferred = work_dir / (prepared.stem + (".mp3" if media == "mp3" else ".mp4"))
    if preferred.exists() and not preferred.name.endswith(".part"): return preferred
    candidates = sorted([p for p in work_dir.glob(f"{prepared.stem}.*") if not p.name.endswith(".part") and not p.name.endswith(".miutima-copying")], key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates: return candidates[0]
    raise FileNotFoundError("فایل نهایی دانلود پس از پایان عملیات پیدا نشد.")


def reset_media_state():
    state.update(media_url="", media_type="", file_name="", file_size=0)


def do_download(url, media, quality, bitrate):
    PRIVATE_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    work_dir = PRIVATE_DOWNLOADS
    outtmpl = str(work_dir / "%(title)s [%(id)s].%(ext)s")
    with lock:
        reset_media_state()
        state.update(running=True, phase="starting", percent=0, speed="", eta="", title="", error="", started=time.time(), path=str(work_dir))

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

    opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "retries": 10, "fragment_retries": 10, "continuedl": True, "overwrites": False, "concurrent_fragment_downloads": 1, "outtmpl": outtmpl, "progress_hooks": [hook], "windowsfilenames": False, "restrictfilenames": False}
    if media == "mp3":
        opts.update(format="bestaudio/best", postprocessors=[{"key":"FFmpegExtractAudio", "preferredcodec":"mp3", "preferredquality":str(bitrate)}])
    else:
        opts.update(format=f"bestvideo[height<={int(quality)}]+bestaudio/best[height<={int(quality)}]", merge_output_format="mp4")

    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=True)
            requested_title = info.get("title", "Download")
            prepared = Path(y.prepare_filename(info))
        with lock: state.update(percent=100, phase="processing", path=str(work_dir))
        source = resolve_final_file(work_dir, prepared, media)
        destination, storage_mode = transfer_to_shared(source, requested_title)
        mime = mimetypes.guess_type(destination.name)[0] or ("audio/mpeg" if destination.suffix.lower() == ".mp3" else "application/octet-stream")
        add_history({"title": requested_title, "url": url, "type": media.upper(), "date": time.strftime("%Y-%m-%d %H:%M:%S"), "path": str(destination.parent), "file": destination.name, "storage": storage_mode, "mime": mime})
        with lock:
            state.update(running=False, phase="done", percent=100, title=requested_title, path=str(destination), media_url="/media/current", media_type=mime, file_name=destination.name, file_size=destination.stat().st_size, error="")
    except Exception as e:
        with lock: state.update(running=False, phase="error", error=str(e)[-1600:], path=str(work_dir), media_url="")


def current_media_path() -> Path | None:
    with lock: raw = state.get("path", "")
    if not raw: return None
    path = Path(raw).resolve()
    allowed = [PRIVATE_DOWNLOADS.resolve(), SHARED_DOWNLOADS.resolve()]
    if not any(path == root or root in path.parents for root in allowed): return None
    if not path.is_file(): return None
    return path


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def send(self, code, body, content_type="application/json; charset=utf-8"):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(raw))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(raw)

    def json(self, code, obj): self.send(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")
    def body(self):
        n = int(self.headers.get("Content-Length", "0")); return json.loads(self.rfile.read(n) or b"{}")

    def serve_media(self):
        path = current_media_path()
        if not path: self.send(404, "Media not available", "text/plain; charset=utf-8"); return
        size = path.stat().st_size
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        range_header = self.headers.get("Range", "")
        start, end = 0, size - 1
        if range_header.startswith("bytes="):
            try:
                spec = range_header[6:].split(",", 1)[0]
                a, b = spec.split("-", 1)
                if a: start = int(a)
                else: start = max(0, size - int(b))
                if b: end = min(size - 1, int(b))
                if start > end or start >= size: raise ValueError
            except ValueError:
                self.send_response(416); self.send_header("Content-Range", f"bytes */{size}"); self.end_headers(); return
        length = end - start + 1
        self.send_response(206 if range_header else 200)
        self.send_header("Content-Type", mime); self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Length", str(length)); self.send_header("Content-Disposition", "inline; filename*=UTF-8''{0}".format(__import__('urllib.parse').parse.quote(path.name))); self.send_header("Cache-Control", "no-store")
        if range_header: self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with path.open("rb") as f:
            f.seek(start); remaining = length
            while remaining:
                chunk = f.read(min(1024 * 1024, remaining))
                if not chunk: break
                self.wfile.write(chunk); remaining -= len(chunk)

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/": self.send(200, INDEX.read_bytes(), "text/html; charset=utf-8"); return
        if p == "/manifest.webmanifest": self.send(200, (ROOT/"web"/"manifest.webmanifest").read_bytes(), "application/manifest+json"); return
        if p == "/sw.js": self.send(200, (ROOT/"web"/"sw.js").read_bytes(), "application/javascript; charset=utf-8"); return
        if p == "/media/current": self.serve_media(); return
        if p == "/api/status":
            with lock: self.json(200, dict(state)); return
        if p == "/api/history": self.json(200, read_json(HISTORY, [])); return
        if p == "/api/settings": self.json(200, read_json(SETTINGS, DEFAULT_SETTINGS)); return
        if p == "/api/clipboard": self.json(200, clipboard()); return
        if p == "/api/storage":
            shared, shared_path, private_path = storage_info(); active = shared_path if shared else private_path
            self.json(200, {"shared_writable": shared, "shared_path": str(shared_path), "private_path": str(private_path), "active_path": str(active), "download_strategy": "private-then-copy"}); return
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
            threading.Thread(target=do_download, args=(url, media, quality, bitrate), daemon=True).start(); self.json(202, {"ok":True}); return
        if p == "/api/settings":
            s = read_json(SETTINGS, DEFAULT_SETTINGS); s.update({k:data[k] for k in DEFAULT_SETTINGS if k in data}); SETTINGS.write_text(json.dumps(s, indent=2), encoding="utf-8"); self.json(200, s); return
        self.send(404, "Not found", "text/plain; charset=utf-8")


if __name__ == "__main__":
    ensure()
    print(f"miutima v2.1.0: http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
