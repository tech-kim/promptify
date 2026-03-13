import yt_dlp

def download_audio(url):

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio/audio.%(ext)s',

        'ffmpeg_location': 'D:/ffmpeg/ffmpeg-git-2026-03-10/bin',

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "audio/audio.mp3"