# miutima v1.0.0 — Usage Guide

## 1. Start the program

From the repository directory:

### Windows CMD
```cmd
py -3 miutima.py
```

### Linux / WSL
```bash
python3 miutima.py
```

### Termux
```bash
python miutima.py
```

## 2. Select media type

miutima asks whether you want:

- `1` — Video (MP4)
- `2` — Audio (MP3)

For MP4, select one of:

- 2160p (4K)
- 1440p
- 1080p
- 720p (default)
- 480p
- 360p

If the requested quality does not exist for the video, yt-dlp selects the best compatible format allowed by the format expression.

## 3. Enter the URL

Paste a supported YouTube URL such as:

```text
https://www.youtube.com/watch?v=VIDEO_ID
```

or:

```text
https://youtu.be/VIDEO_ID
```

miutima validates the host before contacting YouTube.

## 4. Analysis and size estimate

Before downloading, miutima asks yt-dlp for media information and displays the title and an estimated size. The estimate is not guaranteed because streaming formats and server-side information can change.

## 5. Download and resume

The downloader uses retries, fragment retries and continued-download support. If a transfer is interrupted, running the same download again can allow yt-dlp to continue an existing partial file when supported.

## 6. Playlist behavior

v1.0.0 supports playlists. The program passes `noplaylist=False`, so a playlist URL can result in multiple downloaded files.

## 7. Output

Files are stored next to the script:

```text
mp4ytd/   # MP4 video
mp3ytd/   # MP3 audio
```

## 8. FFmpeg

FFmpeg is required for operations such as merging separate video/audio streams and extracting MP3. miutima first checks for a system `ffmpeg`; if none is available, it uses the executable provided by `imageio-ffmpeg`.

## 9. Common problems

### `Connection refused`

This normally means the machine cannot establish the required network connection. Check:

```bash
ping -c 1 1.1.1.1
```

and, where applicable:

```bash
curl -I https://www.youtube.com
```

Check proxy variables if you use a proxy:

```bash
env | grep -i proxy
```

### Python version warning

Use Python 3.11+ for current yt-dlp versions.

### Permission denied on Linux/Termux

Do not run the downloader as root unless you have a specific administrative reason. Choose a directory where your user can write files.

## 10. Legal use

Only download media when you have permission or a lawful basis to do so. Follow YouTube's terms and applicable copyright law.
