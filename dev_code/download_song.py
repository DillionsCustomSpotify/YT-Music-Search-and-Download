import yt_dlp
import json

songId = "0iVlSNpq8i8"
URL = f'https://music.youtube.com/watch?v={songId}'

ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'outtmpl': './songs/%(artist)s - %(title)s.%(ext)s',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download([URL])

