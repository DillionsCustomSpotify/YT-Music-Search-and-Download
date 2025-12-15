import innertube

class YTMusicSearcher():
    def __init__(self):
        self.client = innertube.InnerTube("WEB_REMIX")

    def search(self, searchString:str="") -> list[dict]:
        if searchString == None or searchString == "": return []
        data = self.client.search(query=searchString)
        dataFirstLevelResults = data["contents"]["tabbedSearchResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]

        bestMatchData = None
        try:
            # we must put it into a dict with 'musicResponsiveListItemRenderer' as the key b/c thats how we fetch the data
            bestMatchData = {"musicResponsiveListItemRenderer": dataFirstLevelResults[-2]["musicCardShelfRenderer"]["title"]["runs"][0]}
        except:
            # idk why 'contents' just doesn't exist sometimes. ignore it ig
            pass
        resultsData = dataFirstLevelResults[-1]["musicShelfRenderer"]["contents"]

        iterateData = []
        if bestMatchData != None: iterateData.append(bestMatchData)
        iterateData.extend(resultsData)
        
        searchResultData = []
        for item in iterateData:
            item = item["musicResponsiveListItemRenderer"]
            
            d = None
            if "navigationEndpoint" in item:
                d = self._handleNavEndpoint(item)
            else:
                d = self._handleSong(item)
            
            if d != None: searchResultData.append(d)
        
        return searchResultData

    
    def _handleNavEndpoint(self, item) -> dict:
        # We can get this case from the bestMatchData
        if "watchEndpoint" in item["navigationEndpoint"]:
            videoId = item["navigationEndpoint"]["watchEndpoint"]["videoId"]
            songDummyData = {"playlistItemData":{"videoId": videoId}}
            return self._handleSong(songDummyData)
        
        pageType = item["navigationEndpoint"]["browseEndpoint"]["browseEndpointContextSupportedConfigs"]["browseEndpointContextMusicConfig"]["pageType"]
        
        if pageType == "MUSIC_PAGE_TYPE_ALBUM":
            return self._handleAlbum(item)
        elif pageType == "MUSIC_PAGE_TYPE_ARTIST":
            return self._handleArtist(item)
        else:
            #print(f"Unhandled item of type {pageType}")
            return None
        
    def _handleSong(self, item) -> dict:
        videoId = item["playlistItemData"]["videoId"]
        songInfoScrapped = self.client.player(videoId)
        songInfoFormatted = {
            "type": "song",
            
            "videoId": videoId,
            "name": songInfoScrapped["videoDetails"]["title"],
            "lengthSeconds": songInfoScrapped["videoDetails"]["lengthSeconds"],
            "musicVideoType": songInfoScrapped["videoDetails"]["musicVideoType"],
            
            "channelId": songInfoScrapped["videoDetails"]["channelId"],
            "artist": songInfoScrapped["videoDetails"]["author"],
            
            "thumbnails": songInfoScrapped["videoDetails"]["thumbnail"]["thumbnails"]
        }
        
        if "PODCAST" in songInfoFormatted["musicVideoType"]: return None # skip it, I don't want podcasts
        
        #print(f"Song - {songInfoFormatted['name']} ({videoId})")
        return songInfoFormatted

    def _handleAlbum(self, item) -> dict:
        browserId = item["navigationEndpoint"]["browseEndpoint"]["browseId"]
        albumId = browserId.split("b_")[1]
        
        albumDataScrapped = self.client.browse(browserId)
        albumSongsFull = albumDataScrapped["contents"]["twoColumnBrowseResultsRenderer"]["secondaryContents"]["sectionListRenderer"] \
            ["contents"][0]["musicShelfRenderer"]["contents"]
        albumSongIds = [song["musicResponsiveListItemRenderer"]["playlistItemData"]["videoId"] for song in albumSongsFull]
        albumMetadata = albumDataScrapped["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"] \
        ["sectionListRenderer"]["contents"][0]["musicResponsiveHeaderRenderer"]
        
        albumName = albumMetadata["title"]["runs"][0]["text"]
        artistName = albumMetadata["straplineTextOne"]["runs"][0]["text"]
        artistBrowserId = albumMetadata["straplineTextOne"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
        albumThumbnails = albumMetadata["thumbnail"]["musicThumbnailRenderer"]["thumbnail"]["thumbnails"]
        
        albumData = {
            "type": "album",
            
            "albumId": albumId,
            "songIds": albumSongIds,
            "name": albumName,
            
            "artist": artistName,
            "channelId": artistBrowserId,
            "thumbnails": albumThumbnails,
        }
        
        #print(f"Album - {albumData['name']} ({browserId})")
        return albumData

    def _handleArtist(self, item) -> dict:
        browseId = item["navigationEndpoint"]["browseEndpoint"]["browseId"]
        artistDataScrapped = self.client.browse(browseId)
        artistDataScrappedHeader = artistDataScrapped["header"]["musicImmersiveHeaderRenderer"]
        
        artistThumbnails = []
        artistThumbnails.extend(artistDataScrappedHeader["thumbnail"]["musicThumbnailRenderer"]["thumbnail"]["thumbnails"])
        artistThumbnails.extend(artistDataScrapped["microformat"]["microformatDataRenderer"]["thumbnail"]["thumbnails"])
        
        artistData = {
            "type": "artist",
            
            "channelId": artistDataScrappedHeader["subscriptionButton"]["subscribeButtonRenderer"]["channelId"],
            "name": artistDataScrappedHeader["title"]["runs"][0]["text"],
            "description": artistDataScrapped["microformat"]["microformatDataRenderer"]["description"],
            "thumbnails": artistThumbnails
        }
        
        #print(f"Artist - {artistData['name']} ({artistData['channelId']})")
        return artistData

