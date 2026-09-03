# Changelog

All notable changes to miutima are documented here.

## v1.1.0 — Smart Downloader

### Features

- Cross-platform clipboard support for Windows, WSL, Linux and Termux
- Video Inspector before download
- YouTube search
- Download history with re-download
- Persistent settings in `~/.config/miutima/`
- MP3 quality selection: 128/192/256/320 kbps
- Optional metadata, thumbnail and subtitles
- Retry, fragment retry and resume support
- Complete Windows, Linux, WSL and Termux documentation

### Stability fixes

- Search retries once with proxy usage disabled when the normal yt-dlp connection fails.
- WSL clipboard explicitly tries Windows PowerShell (`powershell.exe` / `pwsh.exe`).
- Clipboard diagnostics now explain platform-specific setup.
- Subtitle settings no longer request a language when subtitles are being disabled.
- Documentation includes WSL network, DNS and proxy diagnostics.

## v1.0.0 — Stable Foundation

- MP4 video downloads
- MP3 audio downloads at 192 kbps
- Playlist support
- Rich terminal interface
- Video quality selection
- FFmpeg integration
- Retry and resumable downloads
- Windows, Linux and Termux compatible Python implementation

## Version policy

The `v1.0.0` and `v1.1.0` branches preserve version snapshots. The `main` branch contains the latest development state.
