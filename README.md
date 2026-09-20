# miutima v2.2.0 — Cross-Platform Media Player

**Windows • Linux • WSL • Android Termux**

A new isolated branch of miutima with a unified local web interface, built-in media preview, playback, transfer animation and completion effects.

## Highlights

- MP4 video + HTML5 video playback
- MP3 audio + HTML5 audio playback
- Image preview
- Windows, Linux, WSL and Termux support
- Live download progress, speed and ETA
- Processing / transfer animation
- Animated completion effect
- Clickable version / developer / GitHub information in the app header
- Local HTTP Range media delivery
- Private-first downloads and verified final transfer
- Platform-specific Downloads folders
- No root required

## Version history

Previous versions remain preserved. This release is on its own branch:

`v2.2.0-cross-platform-media`

The earlier `v2.1.0-media-player`, `v2.0.0`, `v1.1.0`, `v1.0.0` and `main` lines are not deleted or overwritten.

## Quick start

### Windows

```powershell
git clone --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git
cd miutima\v2.2
Set-ExecutionPolicy -Scope Process Bypass
.\install-windows.ps1
.\run-windows.bat
```

### Linux / WSL

```bash
git clone --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git
cd miutima/v2.2
bash install-linux.sh
bash run-linux.sh
```

### Termux

```bash
pkg update -y
pkg install -y git
git clone --branch v2.2.0-cross-platform-media https://github.com/rezaeemajd/miutima.git
cd miutima/v2.2
bash install-termux.sh
bash run-termux.sh
```

Then open:

`http://127.0.0.1:8766`

## Full documentation

See **v2.2/README.md** for complete installation, usage, storage architecture, troubleshooting, upgrades and platform-specific instructions.
