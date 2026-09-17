# miutima v2.0.0

**miutima** is a media downloader project by **Amir Majd**. The v2 branch adds a mobile-first **Persian RTL PWA** for Android Termux while preserving the existing v1.x implementation.

## Version preservation

- `v1.0.0` — preserved snapshot
- `v1.1.0` — preserved snapshot
- `main` — existing development state
- `v2.0.0` — new Termux PWA edition

The v2 work is isolated in `v2/`; the original `miutima.py` is not replaced.

## v2 features

- Responsive Persian RTL mobile UI
- PWA manifest + service worker
- MP4 / MP3 download controls
- YouTube URL inspection
- Termux clipboard button
- Quality: 360/480/720/1080/1440/2160
- MP3 bitrate: 128/192/256/320 kbps
- Download progress and status
- Local download history
- Termux:Widget launch / stop / open shortcuts
- No root required
- Local server bound to `127.0.0.1:8765`

## Install on Android Termux

```bash
pkg update
pkg install -y git
rm -rf ~/miutima-v2-src
mkdir -p ~/miutima-v2-src
git clone --depth 1 --branch v2.0.0 https://github.com/rezaeemajd/miutima.git ~/miutima-v2-src
bash ~/miutima-v2-src/v2/install.sh
```

Install the compatible **Termux:API** and **Termux:Widget** Android companion apps for your Termux distribution. Give storage permission when prompted.

## Run from the widget

After installation, add the Termux:Widget widget to the Android home screen and tap **miutima v2**.

The launcher starts the local server and opens:

```text
http://127.0.0.1:8765
```

You can also run:

```bash
~/.shortcuts/miutima-v2.sh
```

Stop:

```bash
~/.shortcuts/miutima-v2-stop.sh
```

Open the UI only:

```bash
~/.shortcuts/miutima-v2-open.sh
```

## Storage

Downloads go to:

```text
~/storage/downloads/miutima-v2/
```

If needed:

```bash
termux-setup-storage
```

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
       ├── Persian PWA UI
       └── yt-dlp + ffmpeg
```

## Existing v1 usage

The existing v1 documentation and code remain available in the preserved branches and in this branch's original root files. For the classic terminal interface, use `miutima.py`.

## Responsible use

Download only media you are legally permitted to download and respect copyright, creator rights and applicable service terms.
