#!/venv/bin/python

# external dependencies
import re
import logging
from num2words import num2words


def createBlacklistFilterFunc(backlistTerms):
	"""
	createBlacklistFilterFunc defines and returns a function that can be passed to a filter call to remove all torrents that contain any of the disallowed blacklistTerms
	:testedWith: TestTorrentFilterController:test_createBlacklistFilterFunc
	:param blacklistTerms: a list of strings representing terms that the torrent name should not contain
	:return: a function that will filter for blacklist terms
	"""
	def blacklistFilterFunc(item):

		for term in backlistTerms:
			if re.search(term, item, re.IGNORECASE):
				return False
		return True

	return blacklistFilterFunc


def filterEpisodeTorrents(torrents, mediaInfoRecord):
	"""
	filterEpisodeTorrents applies a set of filters that involve regex matching with the download name and ensuring the number of sources exceeds one
	:testedWith: TestTorrentFilterController:filterEpisodeTorrents
	:param torrents: a list of potential download items for the mediaInfoRecord to be filtered
	:param mediaInfoRecord: the mediaInfoRecord for which the torrents were found
	:return: a list of filtered downloads
	"""
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
