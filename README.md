# miutima

**miutima v1.0.0** is a lightweight, interactive command-line media downloader for **Termux and Linux**. It provides a clean Rich-based terminal interface for downloading YouTube videos as MP4 or audio as MP3.

> **Developer:** Amir Majd  
> **Version:** v1.0.0  
> **Project:** miutima

## ✨ Features

- 🎬 Download YouTube videos as **MP4**
- 🎵 Download YouTube audio as **MP3** at 192 kbps
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
├── miutima.py          # Main application
├── requirements.txt    # Python dependencies
├── README.md           # Project overview and setup
├── LICENSE             # MIT License
├── .gitignore          # Git exclusions
└── docs/
    └── usage.md        # Detailed usage guide
```

Downloaded files are stored outside version control in:

```text
mp4ytd/                 # MP4 video downloads
mp3ytd/                 # MP3 audio downloads
```

## 🛠️ Requirements

- Python **3.10+** recommended
- `yt-dlp`
- `rich`
- `imageio-ffmpeg`
- FFmpeg (the application can use a system FFmpeg binary or the executable supplied through `imageio-ffmpeg`)
- Internet access

## 🚀 Installation

### Termux

```bash
pkg update
pkg install python ffmpeg -y
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
pip install -r requirements.txt
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

Termux:

```bash
python miutima.py
```

Linux:

```bash
python3 miutima.py
```

The program displays a simple menu:

```text
1 - Video (MP4)
2 - Audio (MP3)
```

Choose the media type, enter a YouTube URL, and follow the prompts.

## 🎬 MP4 Downloads

For video downloads, miutima lets you choose a target height such as:

- 2160p (4K)
- 1440p
- 1080p
- 720p
- 480p
- 360p

The downloader selects the best available video/audio combination within the requested limit and uses FFmpeg to merge compatible streams into MP4.

## 🎵 MP3 Downloads

Audio mode selects the best available audio stream and uses FFmpeg to extract MP3 audio at **192 kbps**.

## 🔁 Reliability

miutima is configured for unstable connections with:

- socket timeout handling
- repeated network retries
- fragment retries
- file-access retries
- continued downloads
- no intentional overwriting of completed files
- one concurrent fragment download to reduce connection pressure

If a connection fails temporarily, yt-dlp can continue from an existing partial download where supported.

## 📊 Output

Successful downloads are placed next to the application:

```text
miutima/
├── mp4ytd/
│   └── video.mp4
└── mp3ytd/
    └── audio.mp3
```

Generated download files and partial files are ignored by Git through `.gitignore`.

## 🧪 Troubleshooting

### `ModuleNotFoundError`

Install the dependencies again:

```bash
pip install -r requirements.txt
```

### FFmpeg is missing

Check:

```bash
ffmpeg -version
```

On Termux:

```bash
pkg install ffmpeg -y
```

On Debian/Ubuntu:

```bash
sudo apt install ffmpeg -y
```

### Download stops or times out

Check connectivity and retry. miutima already enables multiple retry mechanisms and continued downloads. A partial file may be reusable by yt-dlp.

### YouTube reports a JavaScript-runtime warning

Recent yt-dlp versions may display warnings about optional JavaScript runtimes for some extraction paths. If the selected media remains downloadable, the warning is not necessarily fatal. Keep yt-dlp updated when extraction behavior changes.

## ⚖️ Legal & Responsible Use

miutima is a downloader interface built on top of yt-dlp. Users are responsible for complying with YouTube's Terms of Service, copyright law, and the rights of content owners in their jurisdiction. Download only content that you are legally permitted to download.

## 🔐 Privacy

miutima is a local command-line application. It does not require a miutima account and does not include a project-owned analytics or tracking service. Network requests required for media extraction and downloading are made by the underlying downloader components.

## 📌 Version

**miutima v1.0.0**

This first public version focuses on reliable interactive YouTube MP4/MP3 downloading from Termux and Linux.

## 👨‍💻 Developer

**Amir Majd**

Project name: **miutima**

## 📄 License

Released under the **MIT License**. See [`LICENSE`](LICENSE) for the complete license text.
