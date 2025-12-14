import innertube
import json

client = innertube.InnerTube("WEB_REMIX")
id = "MPREb_jXXSDeV1ivu"

albumData = client.browse(f"{id}")

albumData = albumData["contents"]["twoColumnBrowseResultsRenderer"]["secondaryContents"]["sectionListRenderer"] \
        ["contents"][0]["musicShelfRenderer"]["contents"]


with open("tempData.json", "w") as f: json.dump(albumData, f, indent=4)

print(albumData)

