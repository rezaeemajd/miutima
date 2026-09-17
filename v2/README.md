# miutima v2.1.0

Persian RTL mobile-first PWA for Android Termux.

## Highlights

- YouTube URL inspection
- MP4 / MP3 download
- 360–2160p video quality
- 128–320 kbps MP3 bitrate
- Live percentage / speed / ETA
- Private-first download workspace
- Safe completed-file transfer to Android Downloads
- Built-in MP4 / MP3 / image preview
- HTTP Range support for local media playback
- Animated inspection loader
- Animated processing/transfer indicator
- Animated completion card with check, glow and confetti
- Local history
- Browser Clipboard + Termux:API fallback
- Termux:Widget start / stop / open / status
- Local-only server at `127.0.0.1:8765`
- No root required

## Install

```bash
pkg update
pkg install -y git
rm -rf ~/miutima-v2.1.0-src
git clone --depth 1 --branch v2.1.0-media-player https://github.com/rezaeemajd/miutima.git ~/miutima-v2.1.0-src
bash ~/miutima-v2.1.0-src/v2/install.sh
```

## Run

```bash
~/.shortcuts/miutima-v2.sh
```

Open manually:

```bash
termux-open-url http://127.0.0.1:8765
```

Stop:

```bash
~/.shortcuts/miutima-v2-stop.sh
```

Status:

```bash
~/.shortcuts/miutima-v2-status.sh
```

## Download pipeline

```text
YouTube
  ↓
yt-dlp
  ↓
~/.miutima-v2/downloads/
  ↓
FFmpeg merge/extract
  ↓
safe completed-file transfer
  ↓
~/storage/downloads/miutima-v2/
  ↓
/media/current
  ↓
HTML5 media player
```

Temporary `.part` files are never intentionally written directly to Android shared storage.

## Player behavior

- MP4 is rendered as a native HTML5 `<video>` player.
- MP3 is rendered as a native HTML5 `<audio>` player.
- Image MIME types can be rendered as an image preview.
- The player uses the local `/media/current` endpoint.
- HTTP byte ranges are supported for better media seeking.
- Audible autoplay is not forced; use the visible Play button if the browser/WebView blocks automatic playback.

## Runtime paths

```text
~/.miutima-v2/app.py
~/.miutima-v2/web/
~/.miutima-v2/downloads/
~/.miutima-v2/history.json
~/.miutima-v2/settings.json
~/.miutima-v2/server.log
~/.miutima-v2/miutima.pid
```

## API

### GET

- `/`
- `/manifest.webmanifest`
- `/sw.js`
- `/api/status`
- `/api/history`
- `/api/settings`
- `/api/clipboard`
- `/api/storage`
- `/media/current`

### POST

- `/api/info`
- `/api/download`
- `/api/settings`

## Troubleshooting

If `/api/storage` reports `private-then-copy`, the application is using the safe private-first strategy.

```bash
curl -s http://127.0.0.1:8765/api/storage
```

For logs:

```bash
tail -n 80 ~/.miutima-v2/server.log
```

For process status:

```bash
ps -p "$(cat ~/.miutima-v2/miutima.pid)" -o pid,ppid,user,args
```

## Version preservation

`v2.1.0-media-player` is a separate branch based on the completed v2.0.0 line. Previous branches are preserved.
