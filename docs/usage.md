# miutima Usage Guide

## 1. Install

```bash
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
pip install -r requirements.txt
```

On Termux:

```bash
pkg update
pkg install python ffmpeg git -y
pkg install termux-api -y
```

`termux-api` is optional and is only needed for clipboard integration.

## 2. Start

```bash
python miutima.py
```

Or:

```bash
python3 miutima.py
```

## 3. Main menu

```text
1 - 🔗 Download URL
2 - 📋 Clipboard
3 - 🔎 Search YouTube
4 - 📚 Download History
5 - ⚙️ Settings
6 - ❌ Exit
```

## 4. Download URL

Select **Download URL**, paste a supported YouTube URL, and miutima first runs the Video Inspector. After confirming the metadata, choose MP4 or MP3.

Supported URL forms include:

```text
https://www.youtube.com/watch?v=...
https://youtube.com/watch?v=...
https://youtu.be/...
```

## 5. Clipboard mode

On Android/Termux, copy a YouTube URL and choose **Clipboard**. miutima uses `termux-clipboard-get` when available.

If clipboard access is unavailable, install the Termux API package:

```bash
pkg install termux-api -y
```

The matching Android Termux:API companion app may also be required.

## 6. Video Inspector

Before downloading, miutima displays useful metadata:

- title
- channel/uploader
- duration
- view count
- upload date

This provides a quick confirmation that the correct video was selected.

## 7. Video mode

Choose one of:

```text
2160p
1440p
1080p
720p
480p
360p
```

miutima requests the best available video/audio combination within the selected height and uses FFmpeg to merge compatible streams into MP4.

## 8. Audio mode

Choose a bitrate:

```text
128 kbps
192 kbps
256 kbps
320 kbps
```

The best available audio stream is converted to MP3 using FFmpeg.

## 9. YouTube search

Choose **Search YouTube**, enter a query, and miutima displays up to eight results. Select a result to continue through the normal Inspector and download flow.

## 10. History

The latest 100 download records are stored locally at:

```text
~/.config/miutima/history.json
```

The History menu shows recent downloads and lets you select an item to download again.

## 11. Settings

Settings are stored at:

```text
~/.config/miutima/config.json
```

Available options:

- default video quality
- default audio bitrate
- embed metadata
- embed thumbnail
- subtitle download
- subtitle language

## 12. Subtitles

Enable subtitles in Settings and provide a language code such as `en` or `fa` when prompted. Subtitle availability depends on the source video.

## 13. Output

Downloads are saved next to the application:

```text
miutima/
├── mp4ytd/
│   └── video.mp4
└── mp3ytd/
    └── audio.mp3
```

Application data is stored separately under `~/.config/miutima/`.

## 14. Resume and retries

miutima enables socket, network, fragment, and file-access retries and continued downloads. If a transfer is interrupted, rerunning the same URL can allow yt-dlp to reuse the partial file where supported.

## 15. Verify installation

```bash
python --version
yt-dlp --version
ffmpeg -version
python -m py_compile miutima.py
```

Then run:

```bash
python miutima.py
```

## 16. Update

From the project directory:

```bash
git pull
pip install -r requirements.txt --upgrade
```

## 17. Responsible use

Only download media that you have the right to download. Respect copyright, applicable laws, and the terms and policies of the services from which content is retrieved.
