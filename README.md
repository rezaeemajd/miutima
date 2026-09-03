# miutima v1.1.0

**miutima** is a smart interactive YouTube media downloader for **Windows CMD, Linux/Ubuntu/WSL and Android Termux**.

- **Developer:** Amir Majd
- **Website:** https://cofinets.com
- **License:** MIT

## Features

- MP4 video download
- MP3 audio extraction
- Video Inspector
- YouTube search with network fallback
- Clipboard support on Windows, WSL, Linux Wayland/X11 and Termux
- Download history and re-download
- Persistent settings
- Video quality: 2160p, 1440p, 1080p, 720p, 480p, 360p
- MP3 bitrate: 128, 192, 256, 320 kbps
- Optional subtitles, thumbnail and metadata
- Retry and fragment retry
- Continued/resumable downloads
- FFmpeg integration
- No intentional overwrite of completed downloads

## Python version

Use **Python 3.11 or newer**. Current yt-dlp releases are moving away from Python 3.10, so Python 3.11+ is recommended for this project.

## Requirements

- Python 3.11+
- Git
- Internet access
- FFmpeg recommended
- `yt-dlp`, `rich`, `imageio-ffmpeg` from `requirements.txt`

## Windows CMD

```cmd
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

### Windows clipboard

Copy a YouTube URL with `Ctrl+C`, then select **2 - Clipboard**.

miutima uses PowerShell `Get-Clipboard`; no Python clipboard package is required.

Test:

```cmd
powershell -NoProfile -NonInteractive -Command "Get-Clipboard -Raw"
```

## Ubuntu / Debian Linux

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git ffmpeg
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

### Linux clipboard

Wayland:

```bash
sudo apt install -y wl-clipboard
wl-paste --no-newline
```

X11:

```bash
sudo apt install -y xclip
xclip -selection clipboard -o
```

Alternative X11 tool:

```bash
sudo apt install -y xsel
xsel --clipboard --output
```

## WSL / Ubuntu on Windows

WSL follows the Linux installation but v1.1.0 also supports the Windows clipboard directly.

Test Windows clipboard from WSL:

```bash
command -v powershell.exe
powershell.exe -NoProfile -NonInteractive -Command 'Get-Clipboard -Raw'
```

Copy a URL in Windows first. The second command should print it.

miutima automatically tries `powershell.exe`, then `pwsh.exe`, then Linux clipboard tools.

If `powershell.exe` is missing:

```bash
ls -l /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
```

## WSL search: `Connection refused`

If Search YouTube shows:

```text
Unable to download API page
Failed to establish a new connection
[Errno 111] Connection refused
```

this indicates a network/proxy connection problem. v1.1.0 first uses normal yt-dlp environment settings and then retries directly with proxy use disabled.

Test:

```bash
curl -I https://www.youtube.com
getent hosts www.youtube.com
env | grep -i proxy
```

If an old local proxy is configured, temporarily test:

```bash
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
curl -I https://www.youtube.com
```

If direct access works, fix the proxy configuration rather than changing the downloader.

## Android Termux

```bash
pkg update
pkg upgrade -y
pkg install python git ffmpeg termux-api -y
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

### Termux clipboard

Install the Termux package:

```bash
pkg install termux-api -y
```

Also install the **Termux:API companion Android application** compatible with your Termux installation.

Test:

```bash
termux-clipboard-get
```

Copy a URL in Android first. The command must print the URL. Then select **2 - Clipboard** in miutima.

## Main menu

```text
1 - Download URL
2 - Clipboard
3 - Search YouTube
4 - Download History
5 - Settings
6 - Exit
```

## Download workflow

### MP4

Enter a URL or select a search result, review Inspector information, select MP4 and a quality, confirm, and let FFmpeg merge streams when required.

### MP3

Enter a URL or select a search result, select MP3 and a bitrate, then confirm. FFmpeg converts the selected audio stream to MP3.

## Search

Select **3 - Search YouTube**, enter a query, select a result and continue with the normal download flow.

## History

The last 100 downloads are stored locally in:

```text
~/.config/miutima/history.json
```

## Settings

Stored in:

```text
~/.config/miutima/config.json
```

Settings include video quality, audio bitrate, metadata, thumbnail and subtitles.

## Output

```text
miutima/
├── mp4ytd/
└── mp3ytd/
```

## Launchers

Windows:

```cmd
windows\run_miutima.bat
```

Linux:

```bash
bash linux/run_miutima.sh
```

Termux:

```bash
bash termux/run_miutima.sh
```

## Verify

```bash
python -m py_compile miutima.py
python -m pip show yt-dlp rich imageio-ffmpeg
ffmpeg -version
```

## Version snapshots

- `v1.0.0` — original stable downloader, preserved with complete documentation.
- `v1.1.0` — Smart Downloader.
- `main` — latest development state.

## Responsible use

Download only media you are legally permitted to download. Respect copyright, creator rights and applicable service terms.
