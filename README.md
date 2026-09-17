# miutima v2.1.0 — Media Player Edition

**miutima** is a media downloader project by **Amir Majd**. This branch adds a mobile-first Persian RTL PWA for Android Termux with safe private downloading, Android shared-storage transfer, an in-app MP4/MP3 player, polished progress effects, and detailed diagnostics.

> v2.1.0 is isolated on its own branch. It does **not** overwrite or delete v2.0.0, v1.1.0, v1.0.0, or the existing `main` development line.

## Project

- Developer / Designer: **Amir Majd**
- Website: `cofinets.com`
- Repository: `rezaeemajd/miutima`
- Version: **2.1.0**
- Platform: Android + Termux, no root required
- Local server: `127.0.0.1:8765`

## What is new in v2.1.0

### Built-in media preview

After a successful download, miutima automatically opens a polished media card inside the WebView/browser UI.

- MP4/video → HTML5 video player with controls, seek and fullscreen support where available
- MP3/audio → HTML5 audio player with controls
- Common image MIME types are also supported by the local media endpoint
- File name and detected media type are shown
- A dedicated **Play** button is provided for mobile browsers/WebViews
- The local media endpoint supports HTTP byte ranges, which makes seeking/streaming-style playback more practical for video files

Browsers can block unsolicited audible autoplay, so v2.1.0 intentionally uses a user-controlled **Play** action instead of forcing sound to start. citeturn0search0turn0search10

### Processing / transfer animation

When yt-dlp finishes downloading and miutima is merging/converting/copying the completed file, the UI now shows a compact animated processing indicator:

`⚙  در حال پردازش و انتقال فایل…`

with a moving progress accent so the user can clearly see that the application is still working.

### Completion effect

After the file has actually reached its final destination, the UI shows:

- animated success check
- glow effect
- lightweight confetti particles
- final file name and size
- one-tap **نمایش و پخش فایل** action

The normal live status and progress bar remain visible underneath the effect.

### New app header

The top of the UI now shows:

- miutima branding
- version `2.1.0`
- designer/developer `Amir Majd`
- clickable `cofinets.com`
- clickable GitHub project link

### More robust launcher

The Termux launcher now verifies that the PID belongs to the actual `~/.miutima-v2/app.py` process instead of trusting a stale PID file. A new status shortcut also reports the running process and `/api/storage` state.

## Core v2 features

- Persian RTL responsive mobile UI
- PWA manifest + Service Worker
- YouTube URL inspection
- MP4 video download
- MP3 audio extraction
- Video quality: 360 / 480 / 720 / 1080 / 1440 / 2160
- MP3 bitrate: 128 / 192 / 256 / 320 kbps
- Live download percentage, speed and ETA
- Secure private-first download strategy
- Android shared Downloads transfer after completion
- Clipboard button using browser Clipboard API with Termux:API fallback
- Local download history
- Built-in local media preview/player
- Completion animation and processing animation
- Termux:Widget start / stop / open / status shortcuts
- No root required
- Local-only HTTP server on `127.0.0.1:8765`

## Version preservation

The repository intentionally keeps previous work available:

- `v1.0.0` — preserved snapshot
- `v1.1.0` — preserved snapshot
- `main` — existing development state
- `v2.0.0` — preserved Termux PWA edition
- `v2.1.0-media-player` — this edition

The v2 implementation remains under `v2/`; the classic root `miutima.py` is not replaced.

## Installation — fresh v2.1.0 test

The safest way to test this version without touching an older installation is to clone it into a separate source directory. The installer writes the active v2 runtime under `~/.miutima-v2`.

```bash
pkg update
pkg install -y git

rm -rf ~/miutima-v2.1.0-src

git clone --depth 1 --branch v2.1.0-media-player \
  https://github.com/rezaeemajd/miutima.git \
  ~/miutima-v2.1.0-src

bash ~/miutima-v2.1.0-src/v2/install.sh
```

During installation, Android may ask to rebuild the Termux storage-link structure. This does **not** delete the actual shared-storage files, but read the Termux prompt before accepting it.

Install the compatible **Termux:API** and **Termux:Widget** Android companion applications for your Termux distribution if they are not already installed.

## Upgrade an existing v2 installation

Stop the current v2 server first:

```bash
~/.shortcuts/miutima-v2-stop.sh
```

Clone the new branch into a separate source directory:

```bash
rm -rf ~/miutima-v2.1.0-src

git clone --depth 1 --branch v2.1.0-media-player \
  https://github.com/rezaeemajd/miutima.git \
  ~/miutima-v2.1.0-src
```

Then install:

```bash
bash ~/miutima-v2.1.0-src/v2/install.sh
```

Start it:

```bash
~/.shortcuts/miutima-v2.sh
```

This updates the active v2 runtime while leaving the old source directories and old Git branches untouched.

## Termux:Widget shortcuts

The installer creates:

```text
~/.shortcuts/miutima-v2.sh
~/.shortcuts/miutima-v2-stop.sh
~/.shortcuts/miutima-v2-open.sh
~/.shortcuts/miutima-v2-status.sh
```

### Start

```bash
~/.shortcuts/miutima-v2.sh
```

### Stop

```bash
~/.shortcuts/miutima-v2-stop.sh
```

### Open UI only

```bash
~/.shortcuts/miutima-v2-open.sh
```

### Diagnose status

```bash
~/.shortcuts/miutima-v2-status.sh
```

The status shortcut prints the PID/command and queries `/api/storage`.

## How to use

1. Start **miutima v2** from Termux:Widget.
2. The local UI opens at:

```text
http://127.0.0.1:8765
```

3. Paste a YouTube URL or use **📋 کلیپ‌بورد**.
4. Press **🔎 بررسی و دریافت اطلاعات**.
5. Wait for the animated metadata loader to finish.
6. Select MP4 or MP3.
7. Select video quality or MP3 bitrate.
8. Press **⬇️ شروع دانلود**.
9. Watch the live progress, then the small processing/transfer animation.
10. After completion, the success effect appears.
11. Press **نمایش و پخش فایل** or use the media card below the status section.

## Storage architecture

Android shared storage can behave differently through its FUSE/storage bridge. To avoid creating yt-dlp `.part` files directly in shared storage, v2.1.0 always uses a private work directory first:

```text
YouTube
   │
   ▼
~/.miutima-v2/downloads/
   │
   ├── yt-dlp temporary .part files
   ├── FFmpeg merge/conversion
   │
   ▼
completed file
   │
   ▼
~/storage/downloads/miutima-v2/
   │
   ▼
/media/current
   │
   ▼
PWA media player
```

The final transfer avoids metadata-copy operations such as `shutil.copy2()` because some Android FUSE configurations can reject those operations even when ordinary file writes are permitted.

If shared storage is unavailable, the application keeps the completed file in:

```text
~/.miutima-v2/downloads/
```

The UI reports the active path and transfer strategy.

## Troubleshooting

### `Operation not permitted` on `.webm.part`

If you see a path like:

```text
~/storage/downloads/miutima-v2/...webm.part
```

you are running an older runtime. v2.1.0 downloads temporary files privately and only copies the completed file to shared storage.

Check:

```bash
~/.shortcuts/miutima-v2-status.sh
```

Then:

```bash
curl -s http://127.0.0.1:8765/api/storage
```

Expected strategy:

```text
private-then-copy
```

### Port 8765 already in use

Check the active process:

```bash
cat ~/.miutima-v2/miutima.pid
ps -p "$(cat ~/.miutima-v2/miutima.pid)" -o pid,ppid,user,args
```

Then stop and restart:

```bash
~/.shortcuts/miutima-v2-stop.sh
~/.shortcuts/miutima-v2.sh
```

### Stale browser/PWA UI

v2.1.0 bumps the Service Worker cache name. If an old shell is still visible, close the old tab/PWA completely and reopen:

```bash
termux-open-url http://127.0.0.1:8765
```

### Clipboard is empty

The UI first tries the browser Clipboard API and then `/api/clipboard`, which uses `termux-clipboard-get` when available.

Verify:

```bash
command -v termux-clipboard-get
termux-clipboard-get
```

### Server log

```bash
tail -n 80 ~/.miutima-v2/server.log
```

### Runtime files

```bash
find ~/.miutima-v2 -maxdepth 2 -type f -print
```

## Manual server start

For debugging only:

```bash
cd ~/.miutima-v2
source .venv/bin/activate
python app.py
```

Do not start a second copy while the Widget server is already listening on port `8765`.

## Architecture

```text
Android Home Screen
       │
       ▼
Termux:Widget
       │
       ▼
~/.shortcuts/miutima-v2.sh
       │
       ▼
127.0.0.1:8765
       │
       ├── Persian RTL PWA
       ├── yt-dlp
       ├── FFmpeg
       ├── private download workspace
       ├── safe shared-storage transfer
       └── local media endpoint + player
```

## Security / privacy model

- Server binds to `127.0.0.1`, not the LAN interface.
- Downloaded files are processed locally after the YouTube request.
- The media preview endpoint exposes only the current completed file under the application's controlled private/shared download roots.
- No root access is required.
- No cloud account is required by miutima itself.

## Browser media notes

The player uses standard HTML `<video>`, `<audio>`, and image rendering. Browser/WebView media support depends on the Android browser/WebView codecs. Audible autoplay is intentionally not forced because mobile browsers commonly block unsolicited audio/video playback; the user can press **▶️ پخش** instead. citeturn0search0turn0search3

## Existing v1 usage

The classic v1 implementation remains available. Use the preserved root `miutima.py` and its existing documentation for the terminal-oriented workflow.

## Responsible use

Download only media you are legally permitted to download and respect copyright, creator rights, and applicable service terms.

## License

MIT License — see `LICENSE`.
