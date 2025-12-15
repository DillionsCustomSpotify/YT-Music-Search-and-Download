import json
from yt_dlp import YoutubeDL

songId = "sqK-jh4TDXo"
URLS = [f'https://www.youtube.com/watch?v={songId}']

with YoutubeDL() as ydl:
    ydl.download(URLS)

