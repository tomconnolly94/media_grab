#!/venv/bin/python

# external dependencies
import re
import logging

# internal dependencies
from src.dataTypes.TorrentRecord import TorrentCategory


def createBlacklistFilterFunc(backlistTerms):
	"""
	createBlacklistFilterFunc defines and returns a function that can be passed to a filter call to remove all torrents that contain any of the disallowed blacklistTerms
	:testedWith: TestTorrentFilterController:test_createBlacklistFilterFunc
	:param blacklistTerms: a list of strings representing terms that the torrent name should not contain
	:return: a function that will filter for blacklist terms
	"""
	def blacklistFilterFunc(item):

		for term in backlistTerms:

			if len(term.strip()) > 0 and re.search(term, item, re.IGNORECASE):
				return False
		return True

	return blacklistFilterFunc


def filterBySeason(torrentTitles, name, relevantSeason):
	"""
	filterBySeason applies a regex that matches a torrent for a specific season of a show
	:testedWith: None yet
	:param torrentTitles: a list of torrent titles to be filtered
	:param name: name of tv show
	:param relevantSeason: relevant season number as a string, to cutomise the regex
	:param oneAboveRelevantSeason: relevant season number +1 as a string to allow removal of multi season torrents
	:return: a list of filtered season torrent titles
	"""

	# regex used for dev - "the\Doffice.*?(?:season|s).{0,1}1+(?!episode|e|\d|-| 2)"

	# create season regex
	oneAboveRelevantSeason = str(int(relevantSeason) + 1)
	relevantSeasonReduced = str(int(relevantSeason))

	#"rick\D*and\D*morty.*?(?:season|s).{0,1}(?:05|5)+(?![ .]?episode|[ .]?e|\d|-|[\s]?6)"gmi

	seasonRegexString = rf"{name}.*?(?:season|s).{{0,1}}(?:{relevantSeason}|{relevantSeasonReduced})+(?![ .]?episode|[ .]?e|\d|-|\s?{oneAboveRelevantSeason})"
	logging.info(f"Season regex filter used: {seasonRegexString}")
	seasonRegex = re.compile(
		seasonRegexString, flags=re.IGNORECASE | re.MULTILINE | re.X)

	return list(filter(seasonRegex.search, torrentTitles))


def filterByEpisode(torrentTitles, name, relevantSeason, relevantEpisode):
	"""
	filterByEpisode applies a regex that matches a torrent for a specific episode of a specific season of a show
	:testedWith: None yet
	:param torrentTitles: a list of torrent titles to be filtered
	:param name: name of tv show
	:param relevantSeason: relevant season number as a string, to cutomise the regex
	:param relevantEpisode: relevant episode number as a string, to cutomise the regex
	:return: a list of filtered episode torrent titles
	"""

	# create episode regex
	episodeRegexString = rf"{name}\D*[Ss]{relevantSeason}[Ee]{relevantEpisode}"
	logging.info(f"Episode regex filter used: {episodeRegexString}")
	episodeRegex = re.compile(
		episodeRegexString, flags=re.IGNORECASE | re.MULTILINE)

	return list(filter(episodeRegex.search, torrentTitles))


def filterByBlacklist(mediaInfoRecord, torrentTitles):
	"""
	filterUsingBlacklist removes any torrent titles from filteredTorrentTitles that contain terms from the mediaInfoRecord's blacklist
	:testedWith: None yet
	:param mediaInfoRecord: mediaInfoRecord from which to extract the blacklist
	:param torrentTitles: list of torrent titles to be filtered
	:return: a list of filtered torrent titles
	"""

	blacklistFilterFunc = createBlacklistFilterFunc(
		mediaInfoRecord.getBlacklistTerms())

	# apply blacklist filters to torrent names to avoid any unwanted terms
	return list(filter(blacklistFilterFunc, torrentTitles))


def filterTorrentsByTitleList(torrents, titles, category):

	filteredTorrents = [torrent for torrent in torrents if torrent.getName() in titles ]

	for torrent in filteredTorrents:
		torrent.setCategory(category)

	return filteredTorrents


def filterTorrents(torrents, mediaInfoRecord):
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
    name = name.replace(" ", "\\D*")
    relevantSeason = str(mediaInfoRecord.getLatestSeasonNumber()).zfill(2)
    relevantEpisode = str(mediaInfoRecord.getLatestEpisodeNumber()).zfill(2)

    torrentTitles = [ torrent.getName() for torrent in torrents ]

    # apply blacklist filters to torrent names to avoid any unwanted terms
    blacklistFilteredTorrentTitles = filterByBlacklist(
		mediaInfoRecord, torrentTitles)

    # filter seasons and episodes with regexes
    filteredEpisodeTorrentTitles = filterByEpisode(
		blacklistFilteredTorrentTitles, name, relevantSeason, relevantEpisode)
    filteredSeasonTorrentTitles = filterBySeason(
		blacklistFilteredTorrentTitles, name, relevantSeason)

    filteredEpisodeTorrents = filterTorrentsByTitleList(torrents, filteredEpisodeTorrentTitles, TorrentCategory.TV_EPISODE)
    filteredSeasonTorrents = filterTorrentsByTitleList(torrents, filteredSeasonTorrentTitles, TorrentCategory.TV_SEASON)

    # filter by seeder numbers
    filteredEpisodeTorrents = [ 
		torrent for torrent in filteredEpisodeTorrents if torrent.getSeeders() > 0 
	]
    filteredSeasonTorrents = [
        torrent for torrent in filteredSeasonTorrents if torrent.getSeeders() > 0
    ]

    filteredTorrents = filteredSeasonTorrents + filteredEpisodeTorrents
    logging.info(f"{len(torrents)} torrents filtered down to {len(filteredTorrents)} ({len(filteredSeasonTorrents)} season, {len(filteredEpisodeTorrents)} episode)")

    return filteredTorrents
