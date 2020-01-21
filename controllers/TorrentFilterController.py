#!/venv/bin/python

# pip dependencies
import re

def filterTorrentPageUrls(torrentPageUrls, mediaData):

	if not torrentPageUrls:
		return []

	name = mediaData["name"]
	nameFirstLetter = name[0].lower()
	restOfName = name[1:]
	relevantSeason = mediaData["typeSpecificData"]["latestSeason"]

	seasonRegex = fr'[{nameFirstLetter.upper()}|{nameFirstLetter}]{restOfName}.*[Season\s.Ss0]*{relevantSeason}'
	seasonRegex = re.compile(seasonRegex)
	filteredTorrentPageUrls = list(filter(seasonRegex.search, torrentPageUrls))
	return filteredTorrentPageUrls
