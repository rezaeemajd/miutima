# miutima v1.1.0 — Usage Guide

## Installation

### Windows CMD
```cmd
git clone -b v1.1.0 https://github.com/rezaeemajd/miutima.git
cd miutima
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

### Linux / Ubuntu / WSL
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

### Android Termux
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

Use Python 3.11+.

## Main menu

```text
1 - Download URL
2 - Clipboard
3 - Search YouTube
4 - Download History
5 - Settings
6 - Exit
```

## Clipboard

### Windows CMD
Copy a URL with `Ctrl+C`, choose `2 - Clipboard`.

Test:
```cmd
powershell -NoProfile -NonInteractive -Command "Get-Clipboard -Raw"
```

### WSL
Copy the URL in Windows, then:
```bash
command -v powershell.exe
powershell.exe -NoProfile -NonInteractive -Command 'Get-Clipboard -Raw'
```

v1.1.0 detects WSL and tries Windows PowerShell before Linux clipboard providers.

### Linux
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

### Termux
```bash
pkg install termux-api -y
termux-clipboard-get
```

The matching Termux:API Android companion application is also required. The command should print the text copied in Android.

## YouTube search

Choose `3`, enter a query and select a result. miutima displays up to eight results and continues through the normal Inspector/download flow.

### `Connection refused`

If search reports `Unable to download API page` and `Errno 111 Connection refused`, this is a network/proxy connection problem. v1.1.0 tries the normal environment settings and then retries with proxy use disabled.

Test WSL/Linux:
```bash
curl -I https://www.youtube.com
getent hosts www.youtube.com
env | grep -i proxy
```

Temporary direct test:
```bash
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
curl -I https://www.youtube.com
```

If direct access works, repair the proxy configuration in the shell environment.

## Download URL

Enter a supported YouTube URL. The Inspector displays title, channel, duration, views and upload date. Then choose MP4/MP3 and confirm.

## MP4

Available quality limits:

```text
2160p / 1440p / 1080p / 720p / 480p / 360p
```

FFmpeg merges video/audio streams when required.

## MP3

Available bitrates:

```text
128 / 192 / 256 / 320 kbps
```

FFmpeg converts the selected audio stream to MP3.

## History

The latest 100 records are stored in:

```text
~/.config/miutima/history.json
```

## Settings

```text
~/.config/miutima/config.json
```

Options include video quality, audio bitrate, metadata, thumbnail and subtitles.

## Output

```text
miutima/
├── mp4ytd/
└── mp3ytd/
```

## Verification

```bash
python --version
python -m pip show yt-dlp rich imageio-ffmpeg
python -m py_compile miutima.py
ffmpeg -version
```

## Update

```bash
git checkout v1.1.0
git pull origin v1.1.0
python -m pip install --upgrade -r requirements.txt
```

## Responsible use

Download only media you are legally permitted to download and respect copyright, creator rights and applicable service terms.
