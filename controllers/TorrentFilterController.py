#!/venv/bin/python

# external dependencies
import re
import logging
from num2words import num2words


def filterEpisodeTorrents(torrents, mediaData):

	if not torrents:
		return []
		
	name = mediaData.getShowName()
	nameFirstLetter = name[0].lower()
	restOfName = name[1:]
	restOfName = restOfName.replace(" ", "\\D*")
	relevantSeason = str(mediaData.getLatestSeasonNumber()).zfill(2)
	relevantEpisode = str(mediaData.getLatestEpisodeNumber()).zfill(2)

	episodeRegex = rf"[{nameFirstLetter.upper()}|{nameFirstLetter}]{restOfName}\D*[Ss]{relevantSeason}[Ee]{relevantEpisode}"
	logging.info(f"Regex filter used: {episodeRegex}")
	episodeRegex = re.compile(episodeRegex, flags=re.IGNORECASE | re.MULTILINE)
	
	torrentTitles = [ torrent.getName() for torrent in torrents ]
	filteredTorrentTitles = list(filter(episodeRegex.search, torrentTitles))
	
    # get a list of filtered in torrent items
	filteredTorrents = [ torrent for torrent in torrents if torrent.getName() in filteredTorrentTitles and int(torrent.getSeeders()) > 0 ]

	return filteredTorrents
