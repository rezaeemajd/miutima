# miutima

**miutima v1.1.0** is a smart, interactive YouTube media downloader for **Windows CMD, Linux terminal and Android Termux**.

> **Developer:** Amir Majd  
> **Website:** cofinets.com  
> **License:** MIT

## ✨ Features

- 🎬 YouTube video download as MP4
- 🎵 Audio download as MP3
- 📋 **Cross-platform Clipboard**
- 🔍 Video Inspector before download
- 🔎 YouTube search
- 📚 Download history and re-download
- ⚙️ Persistent settings
- 🎚️ Video quality: 2160p, 1440p, 1080p, 720p, 480p, 360p
- 🎚️ MP3 bitrate: 128, 192, 256, 320 kbps
- 📝 Optional subtitles
- 🖼️ Optional thumbnail
- 🏷️ Optional metadata
- 🔁 Network, fragment and file-access retries
- ▶️ Continued/resumable downloads
- 🚫 Does not intentionally overwrite completed downloads
- ⚙️ FFmpeg integration
- 📱 Android/Termux friendly
- 🪟 Windows CMD friendly
- 🐧 Linux terminal friendly

## 📋 Clipboard support

miutima uses native clipboard commands and does not require a Python clipboard package.

| Platform | Clipboard method | Extra setup |
|---|---|---|
| Windows | PowerShell `Get-Clipboard` | PowerShell available in Windows |
| Linux Wayland | `wl-paste` | `wl-clipboard` package |
| Linux X11 | `xclip` / `xsel` | install either package |
| Termux | `termux-clipboard-get` | Termux:API package/app |

### Windows

Copy a YouTube URL with `Ctrl+C`, start miutima and choose **2 - Clipboard**.

### Linux

Copy a URL and choose **2 - Clipboard**. On Wayland install `wl-clipboard`; on X11 install `xclip` or `xsel`.

### Termux

Install both the Termux package and the companion Android application:

```bash
pkg install termux-api -y
```

Then copy a YouTube URL in Android and choose **2 - Clipboard** in miutima.

See [`docs/platforms.md`](docs/platforms.md) for complete platform instructions.

## 🚀 Installation

### Windows CMD

```bat
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
python -m pip install -r requirements.txt
python miutima.py
```

A CMD launcher is also available:

```text
windows/run_miutima.bat
```

### Linux

```bash
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
python3 -m pip install -r requirements.txt
python3 miutima.py
```

Launcher:

```bash
bash linux/run_miutima.sh
```

### Android Termux

```bash
pkg update
pkg install python git ffmpeg termux-api -y
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
python -m pip install -r requirements.txt
python miutima.py
```

Launcher:

```bash
bash termux/run_miutima.sh
```

## ▶️ Main menu

```text
1 - 🔗 Download URL
2 - 📋 Clipboard
3 - 🔎 Search YouTube
4 - 📚 Download History
5 - ⚙️ Settings
6 - ❌ Exit
```

## 🎬 Video

Select a quality limit and miutima chooses the best available video/audio combination up to that resolution, then uses FFmpeg to merge streams into MP4 when necessary.

## 🎵 Audio

Select 128, 192, 256 or 320 kbps. FFmpeg converts the selected audio stream to MP3.

## 🔍 Inspector

Before downloading, miutima can display title, channel, duration, view count and upload date so you can verify the selected media.

## 🔎 Search

Use **Search YouTube** to search directly from the terminal. Select a result and continue through the normal download flow.

## 📚 History

The last 100 downloads are stored locally. The history menu shows recent items and can start a download again without manually copying the URL.

## ⚙️ Settings

Settings are stored outside the repository:

```text
~/.config/miutima/config.json
```

History is stored at:

```text
~/.config/miutima/history.json
```

Available settings include default video quality, audio bitrate, metadata, thumbnail and subtitle options.

## 📁 Output

```text
miutima/
├── mp4ytd/     # MP4 downloads
└── mp3ytd/     # MP3 downloads
```

Generated media and partial download files are excluded by `.gitignore`.

## 🔁 Reliability

miutima enables socket, network, fragment and file-access retries plus continued downloads. If a connection is interrupted, running the same download again can allow yt-dlp to resume a partial file where supported.

## 🛠️ Requirements

- Python 3.10+
- Git
- FFmpeg
- Internet access
- `yt-dlp`
- `rich`
- `imageio-ffmpeg`

Install Python dependencies with:

```bash
python -m pip install -r requirements.txt
```

On Linux where `python` is not Python 3, use `python3`.

## 🔄 Update

```bash
git pull
python -m pip install -r requirements.txt --upgrade
```

## 🧪 Verify

```bash
python --version
yt-dlp --version
ffmpeg -version
python -m py_compile miutima.py
```

## 📦 Versions

Stable version snapshots are preserved as branches:

- `v1.0.0` — original stable downloader
- `v1.1.0` — Smart Downloader
- `main` — latest development state

See [`CHANGELOG.md`](CHANGELOG.md) for the complete version history.

## ⚖️ Responsible use

miutima is a local interface built on top of yt-dlp. Users are responsible for complying with applicable laws, copyright, service terms and the rights of content owners. Download only media you are legally permitted to download.

## 🔐 Privacy

miutima does not require a miutima account and does not include project-owned analytics or tracking. Network requests required for extraction and downloading are made by the underlying downloader components.

## 📄 License

MIT License. See [`LICENSE`](LICENSE).

## 👨‍💻 Developer

**Amir Majd**  
Website: **cofinets.com**
