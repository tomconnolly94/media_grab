#!/venv/bin/python

# pip dependencies
import re
import logging
from num2words import num2words


def filterEpisodeTorrents(torrents, mediaData):

	if not torrents:
		return []
		
	name = mediaData["name"]
	nameFirstLetter = name[0].lower()
	restOfName = name[1:]
	restOfName = restOfName.replace(" ", "\\D*")
	relevantSeason = mediaData["typeSpecificData"]["latestSeason"].zfill(2)
	relevantEpisode = mediaData["typeSpecificData"]["latestEpisode"].zfill(2)

	episodeRegex = rf"[{nameFirstLetter.upper()}|{nameFirstLetter}]{restOfName}\D*[Ss]{relevantSeason}[Ee]{relevantEpisode}"
	logging.info(f"Regex filter used: {episodeRegex}")
	episodeRegex = re.compile(episodeRegex, flags=re.IGNORECASE | re.MULTILINE)
	
	torrentTitles = [ torrent["name"] for torrent in torrents ]
	filteredTorrentTitles = list(filter(episodeRegex.search, torrentTitles))
	
    # get a list of filtered in torrent items
	filteredTorrents = [ torrent for torrent in torrents if torrent["name"] in filteredTorrentTitles and int(torrent["seeders"]) > 0 ]

	return filteredTorrents
