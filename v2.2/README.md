# miutima v2.2.0 — Cross-Platform Media Player

A new isolated edition of **miutima** for **Windows, Linux, WSL and Android Termux**. This branch keeps the previous versions intact and adds one unified local web interface with post-download media preview, playback, transfer animation and a polished completion effect.

## What v2.2.0 adds

- Windows + Linux + WSL + Termux support in one architecture
- MP4 video download and in-app video playback
- MP3 audio download and in-app audio playback
- Image preview through the same local media endpoint
- Live download percentage, speed and ETA
- Visible processing / transfer animation after download
- Animated success card with check, glow and confetti
- File name, type and size after completion
- HTTP byte-range support for seeking
- Persistent media library for all completed files in the v2.2 Downloads folder
- Click-to-play entries directly from download history
- Reopen and replay the same downloaded file without downloading it again
- Browser Clipboard API plus OS-specific clipboard fallback
- Local-only server bound to `127.0.0.1:8766`
- Separate runtime data under `~/.miutima-v2.2`
- Platform-specific Downloads destination
- Portable FFmpeg resolution with system FFmpeg or imageio-ffmpeg fallback
- No root required
- Previous versions are not deleted or overwritten

## Platform layout

| Platform | Main download folder | Start |
|---|---|---|
| Windows | `%USERPROFILE%\\Downloads\\miutima-v2.2` | `run-windows.bat` |
| Linux | `~/Downloads/miutima-v2.2` | `bash run-linux.sh` |
| WSL | Linux path inside WSL | `bash run-linux.sh` |
| Termux | `~/storage/downloads/miutima-v2.2` | `bash run-termux.sh` |

The application always downloads into a private work directory first and copies only the completed file to the platform Downloads directory. This prevents temporary `.part` files from being created directly in user-facing shared storage.

## Windows installation

Install Python 3.11+ first.

PowerShell:

```powershell
git clone --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git
cd miutima\v2.2
Set-ExecutionPolicy -Scope Process Bypass
.\install-windows.ps1
.\run-windows.bat
```

Or, without Git:

1. Download the repository ZIP for this branch.
2. Extract it.
3. Open PowerShell in `v2.2`.
4. Run `Set-ExecutionPolicy -Scope Process Bypass`.
5. Run `.\install-windows.ps1`.
6. Run `.\run-windows.bat`.

Open the UI at:

```
http://127.0.0.1:8766
```

## Linux installation

Python 3.11+ is recommended.

```bash
git clone --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git
cd miutima/v2.2
bash install-linux.sh
bash run-linux.sh
```

Open:

```
http://127.0.0.1:8766
```

Optional native FFmpeg:

```bash
sudo apt update
sudo apt install -y ffmpeg
```

If FFmpeg is not in PATH, v2.2 can use the `imageio-ffmpeg` package as a fallback.

## WSL

Inside WSL:

```bash
git clone --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git
cd miutima/v2.2
bash install-linux.sh
bash run-linux.sh
```

The application remains local to the WSL environment. The existing v1 clipboard implementation remains available separately.

## Termux installation

Install Termux:API if clipboard integration is wanted.

```bash
pkg update -y
pkg install -y git
git clone --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git
cd miutima/v2.2
bash install-termux.sh
bash run-termux.sh
```

Open:

```
http://127.0.0.1:8766
```

Termux shared storage:

```text
~/storage/downloads/miutima-v2.2/
```

If storage has not been linked yet:

```bash
termux-setup-storage
```

## How to use

1. Start the platform launcher.
2. Open `http://127.0.0.1:8766`.
3. Paste a YouTube URL or use **Clipboard**.
4. Press **بررسی و دریافت اطلاعات**.
5. Choose MP4 or MP3.
6. Choose quality / bitrate.
7. Start the download.
8. Watch the live progress.
9. During merge/conversion/final transfer, the small animated processing indicator remains visible.
10. When the final file is verified, the completion effect appears.
11. Press **نمایش و پخش فایل**.
12. Video opens in the video player, audio in the audio player, and supported images in the image preview.
13. Use **فایل‌های دانلودشده** in the media center to replay any completed file still present in Downloads.
14. Open **نمایش تاریخچه و پخش** and select any history item whose file still exists; unavailable files are clearly disabled.
15. Closing the player no longer destroys its media source, so the same file can be replayed or resumed.

## Media delivery

```text
YouTube
   |
   v
~/.miutima-v2.2/downloads/
   |
   +-- yt-dlp temporary files
   +-- FFmpeg merge / extraction
   |
   v
verified completed file
   |
   v
platform Downloads/miutima-v2.2/
   |
   v
/media/current (latest download)
   |
   +-- /media/file?name=... (persistent downloaded-file playback)
   |
   v
HTML5 video / audio / image preview
```

The `/media/current` endpoint is restricted to the application's controlled download roots and supports HTTP Range requests for media seeking. Completed files are also exposed through the restricted `/media/file?name=...` endpoint, which accepts only a filename inside the platform Downloads folder. The UI reads `/api/files` for the persistent media library and `/api/history` for history entries with an availability check.

## Runtime data

```text
~/.miutima-v2.2/
├── app.py
├── downloads/
├── history.json
└── settings.json
```

The server does not bind to the LAN; it listens on `127.0.0.1`.

## Troubleshooting

### Port 8766 is already in use

Linux / Termux:

```bash
ss -ltnp | grep 8766 || true
```

Windows:

```powershell
Get-NetTCPConnection -LocalPort 8766 -ErrorAction SilentlyContinue
```

Use another port:

```text
MIUTIMA_PORT=8770
```

Linux / Termux:

```bash
MIUTIMA_PORT=8770 python3 app.py
```

Windows PowerShell:

```powershell
$env:MIUTIMA_PORT="8770"
python app.py
```

### FFmpeg error

Check:

```bash
ffmpeg -version
```

On Windows, installing FFmpeg and putting it in PATH is recommended. v2.2 also includes `imageio-ffmpeg` as a fallback.

### Clipboard does not work

The browser Clipboard API is tried first.

- Windows: PowerShell `Get-Clipboard`
- Termux: `termux-clipboard-get`
- Linux: `wl-paste`, `xclip` or `xsel`

Termux:

```bash
pkg install -y termux-api
termux-clipboard-get
```

### Old UI appears

Close the old browser/PWA tab and reopen:

```
http://127.0.0.1:8766
```

The v2.2 Service Worker uses a new cache namespace.

### Inspect or download fails

Run directly from the platform directory to see the Python traceback:

```bash
python app.py
```

Then check the Python packages:

```bash
python -m pip show yt-dlp imageio-ffmpeg
```

## Upgrade / receive changes

Keep the existing checkout and fetch the new branch separately:

```bash
git fetch origin
git checkout v2.2.0-cross-platform-media
git pull --ff-only origin v2.2.0-cross-platform-media
```

For a completely isolated test:

```bash
git clone --depth 1 --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git miutima-v2.2-test
```

Do not delete the old v2.0.0 or v2.1.0 source trees just to test v2.2.0.

## Version preservation

The repository keeps these lines independently:

- `v1.0.0` — stable foundation
- `v1.1.0` — classic cross-platform terminal edition
- `v2.0.0` — Termux PWA edition
- `v2.1.0-media-player` — Termux media-player edition
- `v2.2.0-cross-platform-media` — this Windows/Linux/WSL/Termux edition

No previous branch is deleted or overwritten by this release.

## Responsible use

Download only media you are legally permitted to download and respect copyright, creator rights and applicable service terms.

## License

MIT License — see `LICENSE`.
