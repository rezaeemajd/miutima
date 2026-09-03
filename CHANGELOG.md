# Changelog

All notable changes to miutima are documented here.

## v1.1.0 — Smart Downloader

- Cross-platform clipboard support:
  - Windows: PowerShell `Get-Clipboard`
  - Linux Wayland: `wl-paste`
  - Linux X11: `xclip` / `xsel`
  - Termux: `termux-clipboard-get`
- Video Inspector before download
- YouTube search
- Download history with re-download
- Persistent settings in `~/.config/miutima/`
- MP3 quality selection: 128/192/256/320 kbps
- Optional metadata, thumbnail and subtitles
- Retry, fragment retry and resume support retained
- Windows, Linux and Termux documentation

## v1.0.0 — Stable Foundation

- MP4 video downloads
- MP3 audio downloads at 192 kbps
- Rich terminal interface
- Video quality selection
- FFmpeg integration
- Retry and resumable downloads
- Termux and Linux support

## Version policy

The `v1.0.0` and `v1.1.0` branches preserve stable snapshots. The `main` branch contains the latest development state.
