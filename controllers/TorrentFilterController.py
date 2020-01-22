#!/venv/bin/python

# pip dependencies
import re
import logging

def filterSeasonTorrentPageUrls(torrentPageUrls, mediaData):

	if not torrentPageUrls:
		return []

	name = mediaData["name"]
	nameFirstLetter = name[0].lower()
	restOfName = name[1:]
	relevantSeason = mediaData["typeSpecificData"]["latestSeason"]

	seasonRegex = fr'[{nameFirstLetter.upper()}|{nameFirstLetter}]{restOfName}\D*(?:[Ss]eason|[\s\.Ss0])*{relevantSeason}'
	logging.info(f"seasonRegex: {seasonRegex}")
	seasonRegex = re.compile(seasonRegex)
	filteredTorrentPageUrls = list(filter(seasonRegex.search, torrentPageUrls))
	return filteredTorrentPageUrls


def filterEpisodeTorrentPageUrls(torrentPageUrls, mediaData):

	if not torrentPageUrls:
		return []
		
	name = mediaData["name"]
	nameFirstLetter = name[0].lower()
	restOfName = name[1:]
	relevantSeason = mediaData["typeSpecificData"]["latestSeason"]
	relevantEpisode = mediaData["typeSpecificData"]["latestEpisode"]

	episodeRegex = fr'[{nameFirstLetter.upper()}|{nameFirstLetter}]{restOfName}\D*[Ss]0{relevantSeason}[Ee]0{relevantEpisode}'
	logging.info(f"episodeRegex: {episodeRegex}")
	episodeRegex = re.compile(episodeRegex)
	filteredTorrentPageUrls = list(filter(episodeRegex.search, torrentPageUrls))
	return filteredTorrentPageUrls
