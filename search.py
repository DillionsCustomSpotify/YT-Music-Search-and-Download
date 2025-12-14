import innertube
import json

client = innertube.InnerTube("WEB_REMIX")
data = client.search(query="fools masquerade")

"""
If theres a misspelling in the search:
- 0 is "showing results for: "
- 1 best match
- 2 results
No misspelling
- 0 best match
- 1 results
"""

dataFirstLevelResults = data["contents"]["tabbedSearchResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]

"""
with open("searchResult.json", "w") as f: json.dump(dataFirstLevelResults, f, indent=4)
exit()
"""

bestMatchData = None
try:
    bestMatchData = dataFirstLevelResults[-2]["musicCardShelfRenderer"]["contents"][-1] # get the last item in contents of that
except: print("# idk why tf 'contents' just doesn't exist sometimes. ignore it ig")
resultsData = dataFirstLevelResults[-1]["musicShelfRenderer"]["contents"]

iterateData = []
if bestMatchData != None: iterateData.append(bestMatchData)
iterateData.extend(resultsData)

def handleNavEndpoint(item):
    pageType = item["navigationEndpoint"]["browseEndpoint"]["browseEndpointContextSupportedConfigs"]["browseEndpointContextMusicConfig"]["pageType"]
    
    if pageType == "MUSIC_PAGE_TYPE_ALBUM":
        return handleAlbum(item)
    else:
        print(f"Unhandled item of type {pageType}")
        return None
    
def handleSong(item) -> dict:
    videoId = item["playlistItemData"]["videoId"]
    songInfoScrapped = client.player(videoId)
    songInfoFormatted = {
        "videoId": videoId,
        "name": songInfoScrapped["videoDetails"]["title"],
        
        "channelId": songInfoScrapped["videoDetails"]["channelId"],
        "artist": songInfoScrapped["videoDetails"]["author"],
        
        "thumbnails": songInfoScrapped["videoDetails"]["thumbnail"]["thumbnails"]
    }
    
    print(f"Song - {songInfoFormatted['name']} ({videoId})")
    return songInfoFormatted

def handleAlbum(item) -> dict:
    browserId = item["navigationEndpoint"]["browseEndpoint"]["browseId"]
    albumId = browserId.split("b_")[1]
    
    albumData = client.browse(browserId)
    albumSongsFull = albumData["contents"]["twoColumnBrowseResultsRenderer"]["secondaryContents"]["sectionListRenderer"] \
        ["contents"][0]["musicShelfRenderer"]["contents"]
    albumSongIds = [song["musicResponsiveListItemRenderer"]["playlistItemData"]["videoId"] for song in albumSongsFull]
    albumMetadata = albumData["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"] \
    ["sectionListRenderer"]["contents"][0]["musicResponsiveHeaderRenderer"]
    
    albumName = albumMetadata["title"]["runs"][0]["text"]
    artistName = albumMetadata["straplineTextOne"]["runs"][0]["text"]
    artistBrowserId = albumMetadata["straplineTextOne"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
    albumThumbnails = albumMetadata["thumbnail"]["musicThumbnailRenderer"]["thumbnail"]["thumbnails"]
    
    albumData = {
        "albumId": albumId,
        "songIds": albumSongIds,
        "name": albumName,
        
        "artist": artistName,
        "channelId": artistBrowserId,
        "thumbnails": albumThumbnails,
    }
    
    print(f"Album - ({browserId})")
    return albumData

searchResultData = []
for item in iterateData:
    item = item["musicResponsiveListItemRenderer"]
    
    d = None
    if "navigationEndpoint" in item:
        d = handleNavEndpoint(item)
    else:
        d = handleSong(item)
    
    if d != None: searchResultData.append(d)
    
    #print(item)

with open("searchResult.json", "w") as f: json.dump(searchResultData, f, indent=4)


