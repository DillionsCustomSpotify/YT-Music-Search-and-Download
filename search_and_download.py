
from main_helpers.search import YTMusicSearcher
from main_helpers.downloader import YTMusicDownloader

class YTMusicSearchAndDownload():
    def __init__(self, downloadPath:str="./songs"):
        self.downloadPath = downloadPath
        
        self.searcher = YTMusicSearcher()
        self.downloader = YTMusicDownloader(self.downloadPath)
    
    def updateDownloadPath(self, downloadPath:str="./songs"):
        self.downloader = YTMusicDownloader(downloadPath)
    
    def search(self, searchString:str="") -> list[dict]:
        return self.searcher.search(searchString)

    def downloadSongs(self, songIds:list[str]="") -> None:
        self.downloader.download(songIds)


if __name__ == "__main__":
    ytmsad = YTMusicSearchAndDownload("./testing")
    searchResults = ytmsad.search("Alterclad")
    toDownload = []
    for result in searchResults:
        resultType = result["type"]
        if resultType == "song":
            toDownload.append(result["videoId"])
            break
        print(f"{resultType} - {result['name']}")
    
    ytmsad.downloadSongs(toDownload)

