# miutima Usage Guide

## 1. Install

Clone the repository and install its Python dependencies:

```bash
git clone https://github.com/rezaeemajd/miutima.git
cd miutima
pip install -r requirements.txt
```

On Termux, install FFmpeg with:

```bash
pkg install ffmpeg -y
```

## 2. Start the application

```bash
python miutima.py
```

On systems where `python` maps to Python 2 or is unavailable, use:

```bash
python3 miutima.py
```

## 3. Select media type

Choose one of the available modes:

```text
1 - Video (MP4)
2 - Audio (MP3)
```

### Video

Select a target video height. The application requests the best available video/audio combination up to that height and merges the streams into MP4 when necessary.

### Audio

Select audio mode and provide the YouTube URL. The application downloads the best available audio and converts it to MP3 at 192 kbps.

## 4. Enter a URL

Supported URL forms include:

```text
https://www.youtube.com/watch?v=...
https://youtube.com/watch?v=...
https://youtu.be/...
```

The application validates the hostname before starting extraction.

## 5. Output directories

Files are saved relative to the directory containing `miutima.py`:

```text
mp4ytd/
mp3ytd/
```

The folders are created automatically if they do not exist.

## 6. Resume and retries

The downloader enables continued downloads and several retry mechanisms. If the network drops during a transfer, rerunning the same download can allow yt-dlp to reuse a partial file when supported.

For best results on unstable mobile connections, keep the device connected to a reliable network while the transfer is running.

## 7. Verify installation

Check Python:

```bash
python --version
```

Check yt-dlp:

```bash
yt-dlp --version
```

Check FFmpeg:

```bash
ffmpeg -version
```

Then run:

```bash
python miutima.py
```

## 8. Updating

From the project directory:

```bash
git pull
pip install -r requirements.txt --upgrade
```

## 9. Development notes

The main entry point is `miutima.py`. The application keeps downloaded media out of Git through `.gitignore`, so the repository remains lightweight and source-focused.

For changes, run a syntax check before committing:

```bash
python -m py_compile miutima.py
```

## 10. Responsible use

Only download media that you have the right to download. Respect copyright, applicable laws, and the terms and policies of the services from which content is retrieved.
