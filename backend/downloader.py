import yt_dlp
import os
import subprocess
import tempfile

FFMPEG_LOCATION = "D:/ffmpeg/ffmpeg-git-2026-03-10/bin"
FFMPEG_EXE = "D:/ffmpeg/ffmpeg-git-2026-03-10/bin/ffmpeg.exe"
YOUTUBE_COOKIES = os.environ.get("YOUTUBE_COOKIES", "")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_cookies_file():
    if not YOUTUBE_COOKIES:
        return None
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    tmp.write(YOUTUBE_COOKIES)
    tmp.close()
    return tmp.name


def download_audio(url: str):
    webm_path = os.path.join(OUTPUT_DIR, "audio.webm")
    mp3_path = os.path.join(OUTPUT_DIR, "audio.mp3")

    for f in [webm_path, mp3_path]:
        if os.path.exists(f):
            os.remove(f)

    cookies_file = get_cookies_file()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": webm_path,
        "quiet": False,
    }

    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Unknown")
        artist = info.get("uploader", "Unknown")

    ffmpeg = FFMPEG_EXE if os.path.exists(FFMPEG_EXE) else "ffmpeg"
    subprocess.run([
        ffmpeg, "-i", webm_path,
        "-q:a", "0", "-map", "a",
        mp3_path, "-y"
    ], check=True)

    return mp3_path, title, artist


def get_song_info_from_url(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Unknown"),
            "artist": info.get("uploader", "Unknown"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
        }