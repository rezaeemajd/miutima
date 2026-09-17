# miutima v2.0.0 — Termux PWA Edition

A new Android/Termux edition built beside the existing v1.x code. **No v1.x files are removed or overwritten.**

## What is new

- Local mobile web UI (PWA) at `http://127.0.0.1:8765`
- RTL Persian interface with responsive cards, dark theme and installable PWA manifest
- URL paste, clipboard import, media type, quality and bitrate controls
- Download progress/status through polling
- Local history and settings
- Termux:Widget one-tap launchers
- One-command installer that creates an isolated `~/.miutima-v2` environment
- Uses Termux `python`, `ffmpeg`, `termux-api`; no root required
- Existing `miutima.py`, v1 branches and v1 launchers remain untouched

## Install

```bash
pkg update
pkg install -y git
rm -rf ~/miutima-v2-src
mkdir -p ~/miutima-v2-src
git clone --depth 1 --branch v2.0.0 https://github.com/rezaeemajd/miutima.git ~/miutima-v2-src
bash ~/miutima-v2-src/v2/install.sh
```

The installer creates:

```text
~/.miutima-v2/
~/.shortcuts/miutima-v2.sh
~/.shortcuts/miutima-v2-stop.sh
~/.shortcuts/miutima-v2-open.sh
```

Install the Android apps **Termux:API** and **Termux:Widget** from the same trusted source/channel as your Termux installation. Then put the widget on the Android home screen.

## Start

From Termux:

```bash
~/.shortcuts/miutima-v2.sh
```

Or tap **miutima v2** in Termux:Widget. The launcher starts the local server and opens the PWA URL.

Manual browser URL:

```text
http://127.0.0.1:8765
```

## Stop

```bash
~/.shortcuts/miutima-v2-stop.sh
```

## Architecture

```text
Termux:Widget
     │
     ▼
launcher.sh ──► Python stdlib HTTP server
                       │
                       ├── PWA UI
                       └── yt-dlp + ffmpeg
```

The web UI is only bound to `127.0.0.1`, so it is not intentionally exposed on the LAN.

## Compatibility

Designed for Android + Termux on aarch64 without root. Downloads are saved under:

```text
~/storage/downloads/miutima-v2/
```

If storage is not configured, run:

```bash
termux-setup-storage
```

## Responsible use

Download only media you are legally permitted to download and respect copyright and service terms.
