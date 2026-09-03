# miutima v1.0.0

**miutima** is a lightweight interactive YouTube media downloader written in Python. Version 1.0.0 is the original stable foundation of the project and is preserved as a separate Git branch so it remains available while newer versions continue to evolve.

**Developer:** Amir Majd  
**Website:** https://cofinets.com  
**License:** MIT

## v1.0.0 features

- YouTube URL download
- MP4 video download
- MP3 audio extraction
- Video quality selection: 2160p, 1440p, 1080p, 720p, 480p, 360p
- Playlist support
- Estimated media size before download
- Rich terminal interface and progress bar
- FFmpeg support through system FFmpeg or `imageio-ffmpeg`
- Retry and fragment-retry support
- Resume/continued downloads
- Windows, Linux and Android Termux compatible Python code

> Search, clipboard, history and settings are **not part of the original v1.0.0 feature set**. They were introduced during later development.

## Requirements

- Python 3.11 or newer is recommended.
- Internet access.
- `pip` for installing Python packages.
- FFmpeg is recommended. If it is not installed, miutima can use the FFmpeg binary supplied by `imageio-ffmpeg`.
- On Termux, install Python and FFmpeg with Termux packages.

The current yt-dlp line recommends Python 3.11+; using Python 3.10 may show a deprecation warning and should be avoided for a new installation.

## Windows CMD

Open **Command Prompt (CMD)** and run:

```cmd
git clone -b v1.0.0 https://github.com/rezaeemajd/miutima.git
cd miutima
py -3 --version
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt
py -3 miutima.py
```

If `py` is not available but `python` is installed:

```cmd
python --version
python -m pip install -r requirements.txt
python miutima.py
```

### Windows usage

1. Run `miutima.py`.
2. Choose video or audio.
3. Choose video quality when downloading MP4.
4. Paste the YouTube URL when requested.
5. miutima analyzes the URL and shows the title and estimated size.
6. Confirm the download.
7. Files are saved under the project directory:
   - `mp4ytd\` for MP4
   - `mp3ytd\` for MP3

## Linux / WSL

For Ubuntu, Debian or another Linux terminal:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

git clone -b v1.0.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

For WSL, the same Linux instructions apply. If WSL networking is unavailable, fix WSL Internet/DNS first; v1.0.0 does not contain the later network fallback added to v1.1.0.

## Android Termux

Install the required packages:

```bash
pkg update
pkg upgrade -y
pkg install python git ffmpeg -y
```

Then install miutima:

```bash
git clone -b v1.0.0 https://github.com/rezaeemajd/miutima.git
cd miutima
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python miutima.py
```

## Output folders

miutima creates these folders beside `miutima.py`:

```text
miutima/
├── miutima.py
├── requirements.txt
├── README.md
├── LICENSE
├── mp4ytd/
└── mp3ytd/
```

Downloaded files are ignored by Git through `.gitignore`.

## Troubleshooting

### `python` or `python3` not found

Install Python for your operating system and verify it:

```text
python --version
```

or:

```text
python3 --version
```

### FFmpeg error

Install FFmpeg from your operating system package manager. On Ubuntu/WSL:

```bash
sudo apt install -y ffmpeg
```

On Termux:

```bash
pkg install ffmpeg -y
```

### Network / connection errors

Check that the terminal can access YouTube. A VPN, proxy, firewall, DNS filter or restricted network can prevent yt-dlp from reaching YouTube.

### Interrupted download

miutima enables continued downloads. Run the same download again and yt-dlp can reuse an available partial download where supported.

## Version history

- **v1.0.0** — original stable downloader; preserved unchanged as the historical baseline.
- **v1.1.0** — smart downloader features including search, clipboard, history and settings.

## Responsible use

Use miutima only for content you are legally permitted to download. Respect copyright, platform terms and the rights of content creators.

## Author

**Amir Majd**  
Website: https://cofinets.com
