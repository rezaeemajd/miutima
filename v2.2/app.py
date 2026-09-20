#!/usr/bin/env python3
from __future__ import annotations
import json, mimetypes, os, re, shutil, subprocess, sys, threading, time, unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, urlparse, parse_qs

import yt_dlp
try:
    import imageio_ffmpeg
except ImportError:
    imageio_ffmpeg=None

HOST="127.0.0.1"
PORT=int(os.environ.get("MIUTIMA_PORT","8766"))
ROOT=Path(__file__).resolve().parent
DATA=Path.home()/".miutima-v2.2"
WORK=DATA/"downloads"
HISTORY=DATA/"history.json"
SETTINGS=DATA/"settings.json"
INDEX=ROOT/"web"/"index.html"
MAX_HISTORY=100
DEFAULT_SETTINGS={"video_quality":720,"audio_bitrate":192}
state={"running":False,"phase":"idle","percent":0,"speed":"","eta":"","title":"","error":"","started":None,"path":"","media_url":"","media_type":"","file_name":"","file_size":0,"storage":""}
lock=threading.Lock()

def is_termux():
    return bool(os.environ.get("TERMUX_VERSION") or "com.termux" in str(Path.home()))

def download_dir():
    if is_termux():
        p=Path.home()/"storage"/"downloads"/"miutima-v2.2"
        try: p.mkdir(parents=True,exist_ok=True); return p
        except OSError: pass
    if os.name=="nt":
        p=Path(os.environ.get("USERPROFILE",str(Path.home())))/"Downloads"/"miutima-v2.2"
    else:
        xdg=Path(os.environ.get("XDG_DOWNLOAD_DIR",""))
        p=xdg if xdg and xdg.is_absolute() else Path.home()/"Downloads"
        p=p/"miutima-v2.2"
    try: p.mkdir(parents=True,exist_ok=True); return p
    except OSError: return Path.home()/"miutima-v2.2"

FINAL_DIR=download_dir()

def ensure():
    DATA.mkdir(parents=True,exist_ok=True); WORK.mkdir(parents=True,exist_ok=True); FINAL_DIR.mkdir(parents=True,exist_ok=True)
    if not HISTORY.exists(): HISTORY.write_text("[]",encoding="utf-8")
    if not SETTINGS.exists(): SETTINGS.write_text(json.dumps(DEFAULT_SETTINGS,indent=2),encoding="utf-8")

def read_json(p,default):
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return default

def valid_url(url):
    return bool(re.match(r"^https?://(?:(?:www\.)?youtube\.com|youtu\.be)/",url.strip(),re.I))

def clipboard():
    cmds=[]
    if os.name=="nt":
        if shutil.which("powershell"): cmds.append(["powershell","-NoProfile","-NonInteractive","-Command","Get-Clipboard -Raw"])
        if shutil.which("pwsh"): cmds.append(["pwsh","-NoProfile","-NonInteractive","-Command","Get-Clipboard -Raw"])
    if is_termux() and shutil.which("termux-clipboard-get"): cmds.append(["termux-clipboard-get"])
    if sys.platform.startswith("linux") and not is_termux():
        if shutil.which("wl-paste"): cmds.append(["wl-paste","--no-newline"])
        if shutil.which("xclip"): cmds.append(["xclip","-selection","clipboard","-o"])
        if shutil.which("xsel"): cmds.append(["xsel","--clipboard","--output"])
    for c in cmds:
        try:
            p=subprocess.run(c,capture_output=True,text=True,timeout=5)
            if p.returncode==0: return {"text":p.stdout.strip(),"available":True,"message":""}
        except Exception: pass
    return {"text":"","available":False,"message":"کلیپ‌بورد سیستم در دسترس نیست؛ از دکمه Paste مرورگر استفاده کنید."}

def add_history(item):
    items=read_json(HISTORY,[])
    if not isinstance(items,list): items=[]
    items.insert(0,item)
    HISTORY.write_text(json.dumps(items[:MAX_HISTORY],ensure_ascii=False,indent=2),encoding="utf-8")

def inspect(url):
    with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True,"noplaylist":True,"socket_timeout":30}) as y:
        i=y.extract_info(url,download=False)
    return {"title":i.get("title",""),"channel":i.get("channel") or i.get("uploader") or "","duration":i.get("duration") or 0,"thumbnail":i.get("thumbnail") or "","url":url}

def safe_title(title):
    title=unicodedata.normalize("NFC",str(title or "Download"))
    title=re.sub(r'[\\/:*?"<>|\x00-\x1f]','_',title)
    return re.sub(r"\s+"," ",title).strip(" .")[:150] or "Download"

def transfer(source,title):
    FINAL_DIR.mkdir(parents=True,exist_ok=True)
    ext=source.suffix or ".bin"; base=safe_title(title)
    dest=FINAL_DIR/f"{base}{ext}"
    if dest.exists(): dest=FINAL_DIR/f"{base} [{int(time.time())}]{ext}"
    tmp=dest.with_name(dest.name+".miutima-copying")
    total=source.stat().st_size; copied=0
    with source.open("rb") as src, tmp.open("wb") as dst:
        while True:
            chunk=src.read(1024*1024)
            if not chunk: break
            dst.write(chunk); copied+=len(chunk)
        dst.flush(); os.fsync(dst.fileno())
    if copied!=total: raise IOError(f"انتقال ناقص بود: {copied}/{total} بایت")
    try: tmp.replace(dest)
    except OSError:
        shutil.copyfile(tmp,dest); tmp.unlink(missing_ok=True)
    if dest.stat().st_size!=total: raise IOError("اندازه فایل نهایی نادرست است")
    return dest

def final_file(prepared,media):
    preferred=WORK/(prepared.stem+(".mp3" if media=="mp3" else ".mp4"))
    if preferred.is_file(): return preferred
    candidates=sorted([p for p in WORK.glob(prepared.stem+".*") if p.is_file() and not p.name.endswith(".part") and not p.name.endswith(".miutima-copying")],key=lambda p:p.stat().st_mtime,reverse=True)
    if candidates: return candidates[0]
    raise FileNotFoundError("فایل نهایی دانلود پیدا نشد")

def do_download(url,media,quality,bitrate):
    with lock:
        state.update(running=True,phase="starting",percent=0,speed="",eta="",title="",error="",started=time.time(),path="",media_url="",media_type="",file_name="",file_size=0,storage="")
    def hook(d):
        with lock:
            if d.get("status")=="downloading":
                total=d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done=d.get("downloaded_bytes",0)
                state.update(percent=round(done*100/total,1) if total else 0,speed=d.get("_speed_str",""),eta=d.get("_eta_str",""),phase="downloading")
            elif d.get("status")=="finished": state.update(percent=100,phase="processing")
    out=str(WORK/"%(title)s [%(id)s].%(ext)s")
    opts={"quiet":True,"no_warnings":True,"noplaylist":True,"retries":10,"fragment_retries":10,"file_access_retries":10,"continuedl":True,"overwrites":False,"concurrent_fragment_downloads":1,"outtmpl":out,"progress_hooks":[hook],"windowsfilenames":os.name=="nt"}
    if imageio_ffmpeg is not None:
        try: opts["ffmpeg_location"]=shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
        except Exception: pass
    if media=="mp3":
        opts.update(format="bestaudio/best",postprocessors=[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":str(bitrate)}])
    else:
        opts.update(format=f"bestvideo[height<={int(quality)}]+bestaudio/best[height<={int(quality)}]",merge_output_format="mp4")
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info=y.extract_info(url,download=True); prepared=Path(y.prepare_filename(info))
        with lock: state.update(percent=100,phase="processing",path=str(WORK))
        source=final_file(prepared,media)
        dest=transfer(source,info.get("title","Download"))
        mime=mimetypes.guess_type(dest.name)[0] or ("audio/mpeg" if dest.suffix.lower()==".mp3" else "application/octet-stream")
        add_history({"title":info.get("title","Download"),"url":url,"type":media.upper(),"date":time.strftime("%Y-%m-%d %H:%M:%S"),"path":str(dest.parent),"file":dest.name,"mime":mime})
        with lock: state.update(running=False,phase="done",percent=100,title=info.get("title","Download"),path=str(dest),media_url="/media/current",media_type=mime,file_name=dest.name,file_size=dest.stat().st_size,error="",storage=str(dest.parent))
    except Exception as e:
        with lock: state.update(running=False,phase="error",error=str(e)[-1800:],path=str(WORK),media_url="")

def safe_final_file(name):
    name=Path(str(name or "")).name
    if not name or name in {".",".."}: return None
    p=(FINAL_DIR/name).resolve()
    root=FINAL_DIR.resolve()
    if not (p==root or root in p.parents): return None
    return p if p.is_file() else None

def current_media():
    with lock: raw=state.get("path","")
    if not raw: return None
    p=Path(raw).resolve(); roots=[WORK.resolve(),FINAL_DIR.resolve()]
    if not any(p==r or r in p.parents for r in roots): return None
    return p if p.is_file() else None

def downloaded_files():
    FINAL_DIR.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in FINAL_DIR.iterdir():
        if not p.is_file() or p.name.endswith(".miutima-copying"): continue
        mime=mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        try:
            st=p.stat()
            rows.append({"name":p.name,"size":st.st_size,"mtime":st.st_mtime,"mime":mime,"url":"/media/file?name="+quote(p.name)})
        except OSError:
            pass
    rows.sort(key=lambda x:x["mtime"],reverse=True)
    return rows[:100]

def history_items():
    items=read_json(HISTORY,[])
    if not isinstance(items,list): return []
    out=[]
    for i,item in enumerate(items[:MAX_HISTORY]):
        x=dict(item)
        p=safe_final_file(x.get("file",""))
        x["available"]=bool(p)
        if p:
            x["media_url"]="/media/file?name="+quote(p.name)
            x["file_size"]=p.stat().st_size
        else:
            x["media_url"]=""
        x["history_index"]=i
        out.append(x)
    return out

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*_): pass
    def send(self,code,body,ctype="application/json; charset=utf-8"):
        raw=body.encode("utf-8") if isinstance(body,str) else body
        self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
    def json(self,code,obj): self.send(code,json.dumps(obj,ensure_ascii=False),"application/json; charset=utf-8")
    def body(self):
        n=int(self.headers.get("Content-Length","0")); return json.loads(self.rfile.read(n) or b"{}")
    def serve_media_file(self,p):
        size=p.stat().st_size; mime=mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        rh=self.headers.get("Range",""); start,end=0,size-1
        if rh.startswith("bytes="):
            try:
                a,b=rh[6:].split(",",1)[0].split("-",1)
                start=int(a) if a else max(0,size-int(b)); end=min(size-1,int(b)) if b else size-1
                if start<0 or start>=size or start>end: raise ValueError
            except ValueError:
                self.send_response(416); self.send_header("Content-Range",f"bytes */{size}"); self.end_headers(); return
        length=end-start+1
        self.send_response(206 if rh else 200); self.send_header("Content-Type",mime); self.send_header("Accept-Ranges","bytes"); self.send_header("Content-Length",str(length)); self.send_header("Content-Disposition",f"inline; filename*=UTF-8''{quote(p.name)}"); self.send_header("Cache-Control","no-store")
        if rh: self.send_header("Content-Range",f"bytes {start}-{end}/{size}")
        self.end_headers()
        with p.open("rb") as f:
            f.seek(start); left=length
            while left:
                chunk=f.read(min(1024*1024,left))
                if not chunk: break
                self.wfile.write(chunk); left-=len(chunk)

    def media(self):
        p=current_media()
        if not p: self.send(404,"Media not available","text/plain; charset=utf-8"); return
        self.serve_media_file(p)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/": self.send(200,INDEX.read_bytes(),"text/html; charset=utf-8"); return
        if p=="/manifest.webmanifest": self.send(200,(ROOT/"web"/"manifest.webmanifest").read_bytes(),"application/manifest+json"); return
        if p=="/sw.js": self.send(200,(ROOT/"web"/"sw.js").read_bytes(),"application/javascript; charset=utf-8"); return
        if p=="/media/current": self.media(); return
        if p=="/media/file":
            q=parse_qs(urlparse(self.path).query)
            target=safe_final_file(q.get("name",[""])[0])
            if not target:
                self.send(404,"Media not available","text/plain; charset=utf-8"); return
            self.serve_media_file(target); return
        if p=="/api/status":
            with lock: self.json(200,dict(state)); return
        if p=="/api/history": self.json(200,history_items()); return
        if p=="/api/files": self.json(200,downloaded_files()); return
        if p=="/api/settings": self.json(200,read_json(SETTINGS,DEFAULT_SETTINGS)); return
        if p=="/api/clipboard": self.json(200,clipboard()); return
        if p=="/api/storage": self.json(200,{"platform":"Termux" if is_termux() else ("Windows" if os.name=="nt" else "Linux"),"work_path":str(WORK),"download_path":str(FINAL_DIR),"active_path":str(FINAL_DIR),"download_strategy":"private-then-copy","port":PORT}); return
        self.send(404,"Not found","text/plain; charset=utf-8")
    def do_POST(self):
        p=urlparse(self.path).path
        try: data=self.body()
        except Exception: self.json(400,{"error":"JSON نامعتبر"}); return
        if p=="/api/info":
            url=str(data.get("url","")).strip()
            if not valid_url(url): self.json(400,{"error":"لینک یوتیوب معتبر نیست"}); return
            try: self.json(200,inspect(url))
            except Exception as e: self.json(500,{"error":str(e)[-1400:]})
            return
        if p=="/api/download":
            url=str(data.get("url","")).strip(); media=str(data.get("media","mp4"))
            if not valid_url(url) or media not in {"mp4","mp3"}: self.json(400,{"error":"پارامتر دانلود نامعتبر است"}); return
            with lock:
                if state["running"]: self.json(409,{"error":"یک دانلود در حال اجراست"}); return
            threading.Thread(target=do_download,args=(url,media,data.get("quality",720),data.get("bitrate",192)),daemon=True).start()
            self.json(202,{"ok":True}); return
        if p=="/api/settings":
            s=read_json(SETTINGS,DEFAULT_SETTINGS); s.update({k:data[k] for k in DEFAULT_SETTINGS if k in data}); SETTINGS.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf-8"); self.json(200,s); return
        self.send(404,"Not found","text/plain; charset=utf-8")

if __name__=="__main__":
    ensure(); print(f"miutima v2.2.0: http://{HOST}:{PORT}",flush=True); ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
