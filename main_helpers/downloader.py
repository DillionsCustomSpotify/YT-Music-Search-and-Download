import yt_dlp

class YTMusicDownloader():
    def __init__(self, downloadPath:str="./songs"):
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            #'outtmpl': './songs/%(artist)s - %(title)s.%(ext)s', # artist - title.m4a
            'outtmpl': f'{downloadPath}/%(id)s.%(ext)s', # id.m4a
        }
        
        self.downloader = yt_dlp.YoutubeDL(ydl_opts)
    
    def download(self, songIds: list[str]=[]) -> None:
        if songIds == None or len(songIds) == 0: return None
        urls = []
        for id in songIds:
            if "youtube.com" in id: urls.append(id)
            else: urls.append(f"https://music.youtube.com/watch?v={id}")
        
        self.downloader.download(urls)

