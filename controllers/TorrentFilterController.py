#!/venv/bin/python

# pip dependencies
import re
import logging
from num2words import num2words


def filterSeasonTorrents(torrentTitles, mediaData):

	if not torrentTitles:
		return []

	name = mediaData["name"]
	relevantSeason = str(int(mediaData["typeSpecificData"]["latestSeason"]) + 1)

	seasonRegex = fr''

	for word in name.split():
		seasonRegex += word + '.{0,3}'
	
	seasonRegex += r'(?:season|s).{0,3}\d*'
	seasonRegex += f'(?:{relevantSeason}|{num2words(relevantSeason)})(?!.*episode).*$'

	logging.info(f"seasonRegex: {seasonRegex}")

	filteredTorrents = [ torrentTitle for torrentTitle in torrentTitles if re.search(seasonRegex, torrentTitle, re.IGNORECASE)]

	return filteredTorrents


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
