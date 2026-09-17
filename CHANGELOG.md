# Changelog

All notable changes to miutima are documented here.

## v2.1.0 — Media Player Edition

### Added

- Built-in local media preview after download
- HTML5 video player for MP4 output
- HTML5 audio player for MP3 output
- Image MIME preview support in the media endpoint
- HTTP Range support for local media playback and seeking
- File name, media type and file size display
- Dedicated Play button for mobile/WebView playback
- Animated processing/transfer indicator
- Animated download-complete effect with success check, glow and confetti
- Version, designer and project links in the application header
- Clickable GitHub project link
- `miutima-v2-status.sh` diagnostic shortcut

### Improved

- Termux launcher validates that its PID belongs to the expected miutima process
- PWA shell cache version bumped to prevent stale UI after updates
- More detailed v2.1.0 README and troubleshooting documentation
- Completed-file delivery is isolated behind `/media/current`

### Preserved

- v2.0.0 remains unchanged on its own branch
- v1.0.0 and v1.1.0 remain preserved
- Existing root `miutima.py` remains intact

## v2.0.0 — Termux PWA Edition

- New mobile-first Persian RTL PWA interface
- Local-only HTTP service on `127.0.0.1:8765`
- URL inspection, MP4/MP3 download controls
- Download progress, status and local history
- Termux clipboard integration
- Non-destructive isolated installer under `~/.miutima-v2`
- Termux:Widget launch/stop/open scripts
- v1.0.0 and v1.1.0 code paths and branches remain preserved

## v1.1.0 — Smart Downloader

- Cross-platform clipboard support for Windows, WSL, Linux and Termux
- Video Inspector before download
- YouTube search
- Download history with re-download
- Persistent settings in `~/.config/miutima/`
- MP3 quality selection: 128/192/256/320 kbps
- Optional metadata, thumbnail and subtitles
- Retry, fragment retry and resume support
- Complete Windows, Linux, WSL and Termux documentation

## v1.0.0 — Stable Foundation

- MP4 video downloads
- MP3 audio downloads
- Playlist support
- Rich terminal interface
- Video quality selection
- FFmpeg integration
- Retry and resumable downloads
- Windows, Linux and Termux compatible Python implementation

## Version policy

Version branches are preserved snapshots. New v2 branches are built without deleting or overwriting the existing v1.x branches.
