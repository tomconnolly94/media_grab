#!/venv/bin/python

# external dependencies
import re
import logging
from num2words import num2words


def createBlacklistFilterFunc(backlistTerms):
	def blacklistFilterFunc(item):

		for term in backlistTerms:
			if re.search(term, item, re.IGNORECASE):
				return False
		return True

	return blacklistFilterFunc


def filterEpisodeTorrents(torrents, mediaInfoRecord):

	if not torrents:
		return []
		
	name = mediaInfoRecord.getShowName()
	nameFirstLetter = name[0].lower()
	restOfName = name[1:]
	restOfName = restOfName.replace(" ", "\\D*")
	relevantSeason = str(mediaInfoRecord.getLatestSeasonNumber()).zfill(2)
	relevantEpisode = str(mediaInfoRecord.getLatestEpisodeNumber()).zfill(2)

	episodeRegex = rf"{nameFirstLetter}{restOfName}\D*[Ss]{relevantSeason}[Ee]{relevantEpisode}"
	logging.info(f"Regex filter used: {episodeRegex}")
	episodeRegex = re.compile(episodeRegex, flags=re.IGNORECASE | re.MULTILINE)
	
	torrentTitles = [ torrent.getName() for torrent in torrents ]
	filteredTorrentTitles = list(filter(episodeRegex.search, torrentTitles))

	blacklistFilterFunc = createBlacklistFilterFunc(
		mediaInfoRecord.getBlacklistTerms())

	# apply blacklist filters to torrent names to avoid any unwanted terms
	filteredTorrentTitles = list(
		filter(blacklistFilterFunc, filteredTorrentTitles))
	
    # get a list of filtered in torrent items
	filteredTorrents = [torrent for torrent in torrents if torrent.getName(
	) in filteredTorrentTitles and int(torrent.getSeeders()) > 0 ]

	return filteredTorrents
