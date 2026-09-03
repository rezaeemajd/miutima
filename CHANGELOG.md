# Changelog

All notable changes to miutima are documented here.

## v1.1.0 — Smart Downloader

### Features

- Cross-platform clipboard support:
  - Windows: PowerShell `Get-Clipboard`
  - WSL: `powershell.exe` / `pwsh.exe` Windows clipboard fallback
  - Linux Wayland: `wl-paste`
  - Linux X11: `xclip` / `xsel`
  - Termux: `termux-clipboard-get`
- Video Inspector before download
- YouTube search
- Download history with re-download
- Persistent settings in `~/.config/miutima/`
- MP3 quality selection: 128/192/256/320 kbps
- Optional metadata, thumbnail and subtitles
- Retry, fragment retry and resume support
- Windows, Linux, WSL and Termux documentation

### Stability fixes

- Search now retries once with proxy usage disabled when the normal yt-dlp connection fails.
- WSL clipboard now explicitly tries Windows PowerShell instead of relying only on Linux clipboard providers.
- Clipboard diagnostics now explain the expected platform-specific setup.
- Settings subtitle handling was simplified to avoid unintended language changes when subtitles are disabled.
- Documentation now includes WSL network/proxy diagnostics and clipboard tests.

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
