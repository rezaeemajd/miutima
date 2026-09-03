# Platform Guide

miutima v1.1.0 is designed for **Windows CMD, Linux terminal and Android Termux**.

## Common requirements

- Python 3.10 or newer recommended
- Git
- FFmpeg
- Internet connection
- Python packages from `requirements.txt`

Install:

```bash
python -m pip install -r requirements.txt
```

## Windows CMD

Install Python and Git, then install FFmpeg and make sure `python`, `git` and `ffmpeg` are available in PATH.

```bat
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
python -m pip install -r requirements.txt
python miutima.py
```

### Windows Clipboard

Choose **Clipboard** from the miutima menu. miutima reads the Windows clipboard through PowerShell's native `Get-Clipboard` command. No extra Python clipboard package is required.

Copy a YouTube URL normally with `Ctrl+C`, start miutima, choose `2 - Clipboard`, and continue with the normal media/quality choices.

If PowerShell clipboard access is restricted by policy, use the normal URL option instead.

## Linux terminal

Install Python, Git and FFmpeg with your distribution package manager, then:

```bash
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
python3 -m pip install -r requirements.txt
python3 miutima.py
```

### Linux Clipboard

miutima checks clipboard providers in this order:

1. Wayland: `wl-paste`
2. X11: `xclip`
3. X11 fallback: `xsel`

Examples:

```bash
# Debian/Ubuntu X11
sudo apt install xclip -y

# Debian/Ubuntu Wayland
sudo apt install wl-clipboard -y
```

Copy a YouTube URL, choose **Clipboard** in miutima, and the URL is read automatically.

## Android Termux

Install Termux packages:

```bash
pkg update
pkg install python git ffmpeg termux-api -y
```

Then:

```bash
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
python -m pip install -r requirements.txt
python miutima.py
```

### Termux Clipboard

Install the Termux:API package in Termux:

```bash
pkg install termux-api -y
```

The **Termux:API Android application** must also be installed and permitted to access the clipboard.

Copy a YouTube URL in Android, return to Termux, choose **Clipboard**, and miutima uses `termux-clipboard-get`.

## Output

```text
miutima/
├── mp4ytd/     # downloaded MP4 files
└── mp3ytd/     # downloaded MP3 files
```

Settings and history are stored outside the repository:

```text
~/.config/miutima/config.json
~/.config/miutima/history.json
```

## Main menu

```text
1 - Download URL
2 - Clipboard
3 - Search YouTube
4 - Download History
5 - Settings
6 - Exit
```

## Updating

```bash
git pull
python -m pip install -r requirements.txt --upgrade
```

On Linux use `python3` if required by your distribution.
