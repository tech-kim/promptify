import yt_dlp
import os
import subprocess
import tempfile
import glob

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
    mp3_path = os.path.join(OUTPUT_DIR, "audio.mp3")

    # 기존 파일 모두 삭제
    for f in glob.glob(os.path.join(OUTPUT_DIR, "audio.*")):
        os.remove(f)

    cookies_file = get_cookies_file()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(OUTPUT_DIR, "audio.%(ext)s"),
        "quiet": False,
    }

    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "Unknown")
        artist = info.get("uploader", "Unknown")
        ext = info.get("ext", "webm")

    # 다운로드된 파일 찾기
    downloaded = glob.glob(os.path.join(OUTPUT_DIR, "audio.*"))
    downloaded = [f for f in downloaded if not f.endswith(".mp3")]

    if not downloaded:
        raise Exception("다운로드된 파일을 찾을 수 없습니다")

    input_file = downloaded[0]

    # ffmpeg으로 mp3 변환
    ffmpeg = "ffmpeg"
    subprocess.run([
        ffmpeg, "-i", input_file,
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