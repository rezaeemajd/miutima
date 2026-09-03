# miutima v1.1.0 — Usage Guide

## 1. Install

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

Python 3.11+ is recommended.

## 2. Main menu

```text
1 - Download URL
2 - Clipboard
3 - Search YouTube
4 - Download History
5 - Settings
6 - Exit
```

## 3. Download URL

Choose **1**, paste a YouTube URL and let the Inspector analyze it. Then select MP4 or MP3 and confirm the download.

Supported URL forms include:

```text
https://www.youtube.com/watch?v=VIDEO_ID
https://youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
```

## 4. Clipboard

### Windows CMD

Copy a URL with `Ctrl+C`, choose **2 - Clipboard**.

Test directly:

```cmd
powershell -NoProfile -NonInteractive -Command "Get-Clipboard -Raw"
```

### WSL

Copy a URL in Windows and test:

```bash
command -v powershell.exe
powershell.exe -NoProfile -NonInteractive -Command 'Get-Clipboard -Raw'
```

v1.1.0 automatically tries Windows PowerShell from WSL and then Linux clipboard tools.

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

Install the package and the matching Termux:API Android companion application:

```bash
pkg install termux-api -y
termux-clipboard-get
```

The last command should print the text copied in Android.

## 5. Search YouTube

Choose **3**, enter a query and select a result. v1.1.0 displays up to eight results.

### Search error: Connection refused

If you see `Errno 111 Connection refused`, the terminal cannot establish the connection required by yt-dlp. v1.1.0 retries once with proxy use disabled.

In WSL, test:

```bash
curl -I https://www.youtube.com
getent hosts www.youtube.com
env | grep -i proxy
```

For a temporary direct-connection test:

```bash
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
curl -I https://www.youtube.com
```

If this works, an incorrect proxy setting is the likely cause.

## 6. Inspector

Before a download, miutima can show title, channel, duration, view count and upload date.

## 7. MP4

Select a maximum quality:

```text
2160p / 1440p / 1080p / 720p / 480p / 360p
```

FFmpeg merges video and audio streams when required.

## 8. MP3

Select:

```text
128 / 192 / 256 / 320 kbps
```

FFmpeg extracts and converts the best available audio stream.

## 9. History

The latest 100 download records are stored in:

```text
~/.config/miutima/history.json
```

Select a history item to download it again.

## 10. Settings

Stored in:

```text
~/.config/miutima/config.json
```

Options include default video quality, audio bitrate, metadata, thumbnail and subtitles.

## 11. Subtitles

Enable subtitles in Settings and enter a language code such as `en` or `fa`. Availability depends on the source.

## 12. Output

```text
miutima/
├── mp4ytd/
└── mp3ytd/
```

## 13. Resume and retries

Network, fragment and file-access retries are enabled. Continued downloads are enabled so an interrupted download can often resume when the same URL is started again.

## 14. Verify

```bash
python --version
python -m pip show yt-dlp rich imageio-ffmpeg
python -m py_compile miutima.py
ffmpeg -version
```

## 15. Update

```bash
git checkout v1.1.0
git pull origin v1.1.0
python -m pip install --upgrade -r requirements.txt
```

## 16. Responsible use

Download only media you are legally permitted to download and respect copyright, creator rights and applicable service terms.
