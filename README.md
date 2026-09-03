# miutima v1.1.0

**miutima** is a smart interactive YouTube media downloader for **Windows CMD, Linux/Ubuntu/WSL and Android Termux**.

- **Developer:** Amir Majd
- **Website:** https://cofinets.com
- **License:** MIT

## v1.1.0 features

- MP4 video download
- MP3 audio extraction
- Video Inspector
- YouTube search with network fallback
- Clipboard support on Windows, WSL, Linux Wayland/X11 and Termux
- Download history and re-download
- Persistent settings
- Video quality: 2160p, 1440p, 1080p, 720p, 480p, 360p
- MP3 bitrate: 128, 192, 256, 320 kbps
- Optional subtitles
- Optional thumbnail
- Optional metadata
- Retry and fragment retry
- Continued/resumable downloads
- FFmpeg integration
- No intentional overwrite of completed downloads

## Important: Python version

Use **Python 3.11 or newer**.

Current yt-dlp releases are moving away from Python 3.10; Python 3.10 can display a deprecation warning. Using Python 3.11+ avoids that warning and is the recommended environment for this release.

Check your version:

```bash
python --version
```

or on Linux:

```bash
python3 --version
```

## Requirements

### All platforms

- Python 3.11+
- Git
- Internet access
- Python packages from `requirements.txt`
- FFmpeg recommended for MP4 merging and MP3 conversion

### Python packages

```text
yt-dlp
rich
imageio-ffmpeg
```

Install them with:

```bash
python -m pip install -r requirements.txt
```

## Windows CMD — complete installation

1. Install Python 3.11+ and Git.
2. Open **Command Prompt (CMD)**.
3. Clone the v1.1.0 branch:

```cmd
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
```

4. Create and activate a virtual environment (recommended):

```cmd
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

5. Install dependencies:

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

6. Start:

```cmd
python miutima.py
```

### Windows clipboard

Copy a YouTube URL with `Ctrl+C`, then choose **2 - Clipboard**.

miutima reads the Windows clipboard through PowerShell `Get-Clipboard`; no Python clipboard package is required.

If PowerShell is unavailable, verify:

```cmd
where powershell
powershell -NoProfile -Command "Get-Clipboard -Raw"
```

## Ubuntu / Debian Linux — complete installation

Install system packages:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git ffmpeg
```

Clone v1.1.0:

```bash
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run:

```bash
python miutima.py
```

### Linux clipboard — Wayland

Install:

```bash
sudo apt install -y wl-clipboard
```

Test:

```bash
wl-paste --no-newline
```

### Linux clipboard — X11

Install either `xclip` or `xsel`:

```bash
sudo apt install -y xclip
```

Test:

```bash
xclip -selection clipboard -o
```

miutima tries Wayland first and then X11 clipboard tools.

## WSL / Ubuntu on Windows

WSL is Linux, so the Linux installation above applies. However, WSL has a special clipboard path because the clipboard belongs to Windows.

### WSL clipboard — recommended setup

First check that Windows PowerShell can be called from WSL:

```bash
command -v powershell.exe
```

Then test:

```bash
powershell.exe -NoProfile -NonInteractive -Command 'Get-Clipboard -Raw'
```

Copy a YouTube URL in Windows with `Ctrl+C`. The command above should print it inside WSL.

v1.1.0 automatically tries `powershell.exe` / `pwsh.exe` when it detects WSL, before falling back to Linux clipboard tools.

If `powershell.exe` is not found, check:

```bash
ls -l /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
```

If Windows interop has been disabled in WSL, re-enable normal WSL Windows interop and restart the WSL distribution.

## Android Termux — complete installation

Install the Termux packages:

```bash
pkg update
pkg upgrade -y
pkg install python git ffmpeg termux-api -y
```

Then clone:

```bash
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
```

Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

Install:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run:

```bash
python miutima.py
```

### Termux clipboard

Termux clipboard access needs both:

1. The Termux package:

```bash
pkg install termux-api -y
```

2. The companion **Termux:API Android application** installed on the phone and compatible with the Termux installation.

Test the clipboard directly:

```bash
termux-clipboard-get
```

Copy a YouTube URL in Android first. The command must print the copied text. Then choose **2 - Clipboard** in miutima.

If `termux-clipboard-get` is missing:

```bash
pkg install termux-api -y
```

If it exists but returns nothing, check the Termux:API companion app installation and Android permissions.

## Clipboard summary

| Environment | Method | Extra requirement |
|---|---|---|
| Windows CMD | PowerShell `Get-Clipboard` | PowerShell |
| WSL | `powershell.exe Get-Clipboard` | Windows interop |
| Linux Wayland | `wl-paste` | `wl-clipboard` |
| Linux X11 | `xclip` / `xsel` | one of these packages |
| Termux | `termux-clipboard-get` | Termux:API package + Android app |

No Python clipboard library is required.

## Main menu

```text
1 - Download URL
2 - Clipboard
3 - Search YouTube
4 - Download History
5 - Settings
6 - Exit
```

## Search YouTube

Choose **3 - Search YouTube**, enter a search phrase, select a result, and miutima continues with the normal inspector/download flow.

### Search troubleshooting

If you see:

```text
Unable to download API page
Failed to establish a new connection
[Errno 111] Connection refused
```

this is a **network/proxy connection problem**, not a search-table problem.

v1.1.0 now makes two extraction attempts for search/inspection:

1. normal yt-dlp network/environment settings;
2. a direct connection with proxy use disabled.

If both fail, test WSL/Ubuntu networking:

```bash
curl -I https://www.youtube.com
```

Check proxy variables:

```bash
env | grep -i proxy
```

If you see an old or unreachable proxy such as `127.0.0.1:<port>`, fix or unset it before testing again:

```bash
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
```

Then test:

```bash
curl -I https://www.youtube.com
```

If your network genuinely requires a proxy, do not unset it permanently; configure the correct working proxy instead.

## Download workflow

### MP4

1. Enter a YouTube URL or select a search result.
2. Review the Inspector information.
3. Choose MP4.
4. Select quality.
5. Review the estimated size.
6. Confirm the download.
7. The video and audio streams are merged with FFmpeg when required.

### MP3

1. Enter a YouTube URL or select a search result.
2. Choose MP3.
3. Select bitrate: 128/192/256/320 kbps.
4. Confirm the download.
5. FFmpeg extracts the audio to MP3.

## Settings

Settings are stored locally outside the repository:

```text
~/.config/miutima/config.json
```

History:

```text
~/.config/miutima/history.json
```

Settings include:

- default video quality
- default MP3 bitrate
- metadata embedding
- thumbnail embedding
- subtitle enable/disable
- subtitle language

## Output

```text
miutima/
├── miutima.py
├── requirements.txt
├── README.md
├── LICENSE
├── docs/
├── windows/
├── linux/
├── termux/
├── mp4ytd/     # downloaded MP4 files
└── mp3ytd/     # downloaded MP3 files
```

Downloaded media and temporary files are excluded by `.gitignore`.

## Launchers

Windows CMD:

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

## Verify installation

Windows:

```cmd
python --version
python -m pip show yt-dlp rich imageio-ffmpeg
python -m py_compile miutima.py
```

Linux/WSL/Termux:

```bash
python --version
python -m pip show yt-dlp rich imageio-ffmpeg
python -m py_compile miutima.py
ffmpeg -version
```

## Updating v1.1.0

If you cloned the `v1.1.0` branch:

```bash
git checkout v1.1.0
git pull origin v1.1.0
python -m pip install --upgrade -r requirements.txt
```

## Version snapshots

- `v1.0.0` — original stable downloader, preserved with its own documentation.
- `v1.1.0` — Smart Downloader with search, clipboard, history and settings.
- `main` — latest development state.

Older versions remain available as Git branches so they can be checked out independently.

## Responsible use

Download only media you are legally permitted to download. Respect copyright, creator rights and applicable service terms.
