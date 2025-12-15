import innertube
import json

DEBUG_WRITE_FILES = True

client = innertube.InnerTube("WEB_REMIX")
data = client.search(query="jamie paige")

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

if DEBUG_WRITE_FILES:
    with open("./raw-data/rawsSearchResultsPinpointed.json", "w") as f: json.dump(dataFirstLevelResults, f, indent=4)

bestMatchData = None
try:
    # we must put it into a dict with 'musicResponsiveListItemRenderer' as the key b/c thats how we fetch the data
    bestMatchData = {"musicResponsiveListItemRenderer": dataFirstLevelResults[-2]["musicCardShelfRenderer"]["title"]["runs"][0]}
    if DEBUG_WRITE_FILES:
        with open("./raw-data/rawBestMatch.json", "w") as f: json.dump(bestMatchData, f, indent=4)
except:
    # idk why tf 'contents' just doesn't exist sometimes. ignore it ig
    print("bestMatchData not found, skipping it...")
    pass
resultsData = dataFirstLevelResults[-1]["musicShelfRenderer"]["contents"]

iterateData = []
if bestMatchData != None: iterateData.append(bestMatchData)
iterateData.extend(resultsData)

def handleNavEndpoint(item):
    # We can get this case from the bestMatchData
    if "watchEndpoint" in item["navigationEndpoint"]:
        videoId = item["navigationEndpoint"]["watchEndpoint"]["videoId"]
        songDummyData = {"playlistItemData":{"videoId": videoId}}
        return handleSong(songDummyData)
    
    pageType = item["navigationEndpoint"]["browseEndpoint"]["browseEndpointContextSupportedConfigs"]["browseEndpointContextMusicConfig"]["pageType"]
    
    if pageType == "MUSIC_PAGE_TYPE_ALBUM":
        return handleAlbum(item)
    elif pageType == "MUSIC_PAGE_TYPE_ARTIST":
        return handleArtist(item)
    else:
        print(f"Unhandled item of type {pageType}")
        return None
    
def handleSong(item) -> dict:
    videoId = item["playlistItemData"]["videoId"]
    songInfoScrapped = client.player(videoId)
    songInfoFormatted = {
        "videoId": videoId,
        "name": songInfoScrapped["videoDetails"]["title"],
        "lengthSeconds": songInfoScrapped["videoDetails"]["lengthSeconds"],
        "musicVideoType": songInfoScrapped["videoDetails"]["musicVideoType"],
        
        "channelId": songInfoScrapped["videoDetails"]["channelId"],
        "artist": songInfoScrapped["videoDetails"]["author"],
        
        "thumbnails": songInfoScrapped["videoDetails"]["thumbnail"]["thumbnails"]
    }
    
    if "PODCAST" in songInfoFormatted["musicVideoType"]: return None # skip it, I don't want podcasts
    
    if DEBUG_WRITE_FILES:
        with open("./raw-data/rawSong.json", "w") as f: json.dump(songInfoScrapped, f, indent=4)
    
    print(f"Song - {songInfoFormatted['name']} ({videoId})")
    return songInfoFormatted

def handleAlbum(item) -> dict:
    browserId = item["navigationEndpoint"]["browseEndpoint"]["browseId"]
    albumId = browserId.split("b_")[1]
    
    albumDataScrapped = client.browse(browserId)
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
        "albumId": albumId,
        "songIds": albumSongIds,
        "name": albumName,
        
        "artist": artistName,
        "channelId": artistBrowserId,
        "thumbnails": albumThumbnails,
    }
    
    print(f"Album - {albumData['name']} ({browserId})")
    return albumData

def handleArtist(item):
    browseId = item["navigationEndpoint"]["browseEndpoint"]["browseId"]
    artistDataScrapped = client.browse(browseId)
    artistDataScrappedHeader = artistDataScrapped["header"]["musicImmersiveHeaderRenderer"]
    
    artistThumbnails = []
    artistThumbnails.extend(artistDataScrappedHeader["thumbnail"]["musicThumbnailRenderer"]["thumbnail"]["thumbnails"])
    artistThumbnails.extend(artistDataScrapped["microformat"]["microformatDataRenderer"]["thumbnail"]["thumbnails"])
    
    artistData = {
        "channelId": artistDataScrappedHeader["subscriptionButton"]["subscribeButtonRenderer"]["channelId"],
        "name": artistDataScrappedHeader["title"]["runs"][0]["text"],
        "description": artistDataScrapped["microformat"]["microformatDataRenderer"]["description"],
        "thumbnails": artistThumbnails
    }
    
    if DEBUG_WRITE_FILES:
        with open("./raw_data/rawArtist.json", "w") as f: json.dump(artistDataScrapped, f, indent=4)
        
    print(f"Artist - {artistData['name']} ({artistData['channelId']})")
    return artistData

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

if DEBUG_WRITE_FILES:
    with open("./dev_code/searchResult.json", "w") as f: json.dump(searchResultData, f, indent=4)


