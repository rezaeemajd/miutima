# miutima

**miutima v1.1.0** is a smart, interactive command-line media downloader for **Termux and Linux**. It provides a Rich-based terminal interface for downloading YouTube videos as MP4 or audio as MP3, with clipboard mode, video inspection, search, history, settings, retry/resume support, and FFmpeg integration.

> **Developer:** Amir Majd  
> **Version:** v1.1.0  
> **Project:** miutima

## ✨ Features

- 🎬 Download YouTube videos as **MP4**
- 🎵 Download YouTube audio as **MP3** at selectable 128/192/256/320 kbps
- 📋 **Clipboard mode** on Termux when `termux-clipboard-get` is available
- 🔎 **YouTube search** directly from the terminal
- 🔍 **Video Inspector** before downloading: title, channel, duration, views, upload date
- 📚 **Download history** with re-download support
- ⚙️ Persistent **settings** stored in `~/.config/miutima/config.json`
- 📝 Optional subtitle downloading
- 🖼️ Optional thumbnail embedding
- 🏷️ Optional metadata embedding
- 📊 Interactive terminal UI powered by Rich
- 📦 Download-size estimation when metadata provides size information
- 🔁 Network, fragment, and file-access retries
- ▶️ Continued/resumable downloads
- 🚫 Avoids overwriting existing downloads
- ⚙️ FFmpeg support for media conversion and MP4 merging
- 📱 Designed to work well on Android/Termux
- 🐧 Works on Linux systems with Python 3
- 🔗 Accepts standard `youtube.com` and `youtu.be` URLs

## 📁 Project Structure

```text
miutima/
├── miutima.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── docs/
    └── usage.md
```

Downloaded files are stored outside version control in `mp4ytd/` and `mp3ytd/`.

Local application data:

```text
~/.config/miutima/
├── config.json
└── history.json
```

## 🛠️ Requirements

- Python **3.10+** recommended
- `yt-dlp`
- `rich`
- `imageio-ffmpeg`
- FFmpeg
- Internet access
- Optional on Termux: `termux-api` for clipboard integration

## 🚀 Installation

### Termux

```bash
pkg update
pkg install python ffmpeg git -y
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
pip install -r requirements.txt
```

For clipboard support:

```bash
pkg install termux-api -y
```

### Linux

```bash
sudo apt update
sudo apt install python3 python3-pip ffmpeg git -y
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
python3 -m pip install -r requirements.txt
```

## ▶️ Run

```bash
python miutima.py
```

The v1.1 main menu is:

```text
1 - 🔗 Download URL
2 - 📋 Clipboard
3 - 🔎 Search YouTube
4 - 📚 Download History
5 - ⚙️ Settings
6 - ❌ Exit
```

## 📋 Clipboard Mode

Copy a YouTube URL on Android and select **Clipboard** in miutima. If `termux-clipboard-get` is available, miutima reads the copied URL and continues to the normal inspector/download flow.

## 🔍 Video Inspector

Before a download, miutima can show the title, channel/uploader, duration, view count, and upload date so the user can confirm the correct video.

## 🔎 YouTube Search

Search directly from the terminal. miutima displays up to eight results and lets the user select one for the normal download flow.

## 📚 Download History

The latest 100 download records are stored locally in `~/.config/miutima/history.json`. A selected item can be downloaded again.

## ⚙️ Settings

Available settings include:

- default video quality
- default audio bitrate
- metadata embedding
- thumbnail embedding
- subtitle downloading
- subtitle language

## 🎬 MP4 Downloads

Supported target heights:

- 2160p (4K)
- 1440p
- 1080p
- 720p
- 480p
- 360p

FFmpeg merges compatible video/audio streams into MP4.

## 🎵 MP3 Downloads

Audio mode selects the best available audio stream and converts it to MP3 at the selected bitrate: **128, 192, 256, or 320 kbps**.

## 📝 Subtitles and Metadata

When enabled in Settings, miutima can request subtitles and embed available metadata/thumbnail information. Availability depends on the source and formats exposed by yt-dlp.

## 🔁 Reliability

miutima enables socket, network, fragment, and file-access retries, continued downloads, and avoids intentionally overwriting completed files. Partial downloads can usually be resumed by yt-dlp.

## 🧪 Troubleshooting

### `ModuleNotFoundError`

```bash
pip install -r requirements.txt
```

### Clipboard unavailable on Termux

```bash
pkg install termux-api -y
```

The matching Termux:API Android companion app may also be required. Normal URL mode works without clipboard integration.

### FFmpeg missing

```bash
ffmpeg -version
```

Termux:

```bash
pkg install ffmpeg -y
```

Debian/Ubuntu:

```bash
sudo apt install ffmpeg -y
```

### Download stops or times out

Check connectivity and retry. miutima already enables multiple retry mechanisms and continued downloads.

## ⚖️ Legal & Responsible Use

miutima is a downloader interface built on top of yt-dlp. Users are responsible for complying with YouTube's Terms of Service, copyright law, and the rights of content owners in their jurisdiction. Download only content that you are legally permitted to download.

## 🔐 Privacy

miutima is local software. It does not require a miutima account and does not include a project-owned analytics or tracking service. Network requests are made by the underlying downloader/search components.

## 📌 Version

**miutima v1.1.0 — Smart Downloader**

## 👨‍💻 Developer

**Amir Majd**

## 📄 License

Released under the **MIT License**. See [`LICENSE`](LICENSE).
