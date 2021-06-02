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

	seasonRegexString = rf"{name}.*?(?:season|s).{{0,1}}(?:{relevantSeason}|{relevantSeasonReduced})+(?!episode|e|\d|-|{oneAboveRelevantSeason}| {oneAboveRelevantSeason})"
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


def filterUsingBlacklist(mediaInfoRecord, torrentTitles):
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
	return list(
		filter(blacklistFilterFunc, torrentTitles))


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

	# filter for torrents matching a relevant episode or season number
	filteredTorrentTitles = list(set(
		filterByEpisode(torrentTitles, name, relevantSeason, relevantEpisode) +
		filterBySeason(torrentTitles, name, relevantSeason)
	))

	# apply blacklist filters to torrent names to avoid any unwanted terms
	filteredTorrentTitles = filterUsingBlacklist(
		mediaInfoRecord, filteredTorrentTitles)
	
    # get a list of filtered in torrent items
	filteredTorrents = [torrent for torrent in torrents if torrent.getName(
	) in filteredTorrentTitles and int(torrent.getSeeders()) > 0 ]

	return filteredTorrents


# test data for new season filtering:

# match - The Office Season 1 COMPLETE 720p x265-KRAVE2017-05-16 VIP2.09 GiB4411 KraveHQ 
# match - The Office (US) (2005) Season 1-9 S01-S09 (1080p BluRay x265 HEV2021-02-07 VIP165.73 GiB36429 Cybotage 
# match - The Office - The Complete Season 7 [HDTV]2011-05-21 VIP4.61 GiB2817 FaMoUz 
# match - The Office Season 8 COMPLETE 720p x265-KRAVE2017-05-20 VIP4.15 GiB2119 KraveHQ 
# match - The Office Season 5 COMPLETE 720p x265-KRAVE2017-05-18 VIP4.58 GiB135 KraveHQ 
# match - The Office US Season 7 Complete 720p
# match - The.Office.US.S02.1080p.AMZN.WEBRip.x264-AJP69 [Season 2 Two]2018-07-31 VIP41.58 GiB313 GoodFilms 
# match - The Office Season 5 Complete [HDTV][XVID] [USA]2009-05-19 VIP4.78 GiB10 .BONE. 
# match - The Office - The Complete Season 6 [DVDRip]2010-10-17 VIP4.67 GiB13 FaMoUz 
# match - The Office Season 7 Complete 720p WEB-DL2011-05-28 VIP19.12 GiB01 Konashine 
# match - The.Office.US.S09.Season.9.720p.BluRay.x264-DEMAND [PublicHD]2013-08-28 VIP25.26 GiB01 aoloffline 
# match - The Office Season 7 HDTV-Spynx2013-09-03 VIP4.61 GiB01 TvTeam 
# match - The Office Season 2 COMPLETE 720p x265-KRAVE2017-05-17 VIP3.91 GiB08 KraveHQ 
# match - The Office Season 4 COMPLETE 720p x265-KRAVE2017-05-17 VIP3.48 GiB08 KraveHQ
# match - The Office Season 7 COMPLETE 720p x265-KRAVE episode 2

# not match - The.Office.US.S02.E01.1080p.AMZN.WEBRip.x264-AJP69
# not match - The office Season 02 Episode 01.1080p.AMZN.WEBRip.x264-AJP69
# not match - The Office US Season 1 2 3 4 5 6 7 8 9 - threesixtyp

# match - The Office (US) (2005) Season 1-9 S01-S09 (1080p BluRay x265 HEV
# match - The Office Season 1 COMPLETE 720p x265-KRAVE
# match - The Office Season 8 COMPLETE 720p x265-KRAVE
# match - The Office - The Complete Season 7 [HDTV]
# match - The Office US Season 7 Complete 720p
# match - The Office Season 9 COMPLETE 720p BluRay x265-KRAVE
# match - The Office Season 5 COMPLETE 720p x265-KRAVE
