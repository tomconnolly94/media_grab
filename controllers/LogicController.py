#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import TPBInterface, DownloadsInProgressFileInterface, QBittorrentInterface
from controllers import QueryGenerationController, TorrentFilterController, NewTorrentController, CompletedDownloadsController
from data_types.ProgramMode import PROGRAM_MODE 


def findMediaInfoRecord(mediaInfoRecords, mediaInfoName):
	for record in mediaInfoRecords:
		if record["name"] == mediaInfoName:
			return record


def sortTorrents(torrents):
    # order torrents by number of seeders
    return sorted(torrents, key=lambda torrent: int(torrent["seeders"]))
    


def getMediaInfoRecordsWithTorrents(mediaSearchQueries, mediaInfoRecords):
    mediaInfoRecordsWithTorrents = []

    for mediaInfoName, queries in mediaSearchQueries.items():

        torrentRecords = TPBInterface.getTorrentRecords(queries)

        #filter torrentRecords by applying regex to torrent titles
        mediaInfoRecord = findMediaInfoRecord(mediaInfoRecords, mediaInfoName)
        torrentTitles = [ torrent["name"] for torrent in torrentRecords ]
        filteredTorrentTitles = TorrentFilterController.filterSeasonTorrents(torrentTitles, mediaInfoRecord)

        #get list of filtered torrent objects
        filteredTorrents = [ torrent for torrent in torrentRecords if torrent["name"] in filteredTorrentTitles ]

        # order torrents by number of seeders
        filteredSortedTorrents = sortTorrents(filteredTorrents)

        if filteredSortedTorrents:
            chosenTorrent = filteredSortedTorrents[0]
            mediaInfoRecord["magnet"] = chosenTorrent["magnet"]
            mediaInfoRecordsWithTorrents.append(mediaInfoRecord)

    return mediaInfoRecordsWithTorrents


def runProgramLogic(mediaInfoRecords, mode):

    # ascertain mode of program
    if mode == PROGRAM_MODE.TV_SEASONS:
        # mediaSearchQueries = QueryGenerationController.generateTVSeasonQueries(mediaInfoRecords)
        raise ValueError(f"mode: {mode} has no handler statement") 
    elif mode == PROGRAM_MODE.TV_EPISODES:
        mediaSearchQueries = QueryGenerationController.generateTVEpisodeQueries(mediaInfoRecords)
    else:
        raise ValueError(f"mode: {mode} has no handler statement") 

    #analyse folder to look for completed downloads
    CompletedDownloadsController.auditDumpCompleteDir(mode, DownloadsInProgressFileInterface.getDownloadingItems(mode))
    
    #add torrent magnet links to mediaInfoRecords
    mediaInfoRecordsWithTorrents = getMediaInfoRecordsWithTorrents(mediaSearchQueries, mediaInfoRecords)

    for mediaInfoRecord in mediaInfoRecordsWithTorrents:
        magnet = mediaInfoRecord["magnet"]
        if QBittorrentInterface.initTorrentDownload(magnet):
            NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, "latestSeason", magnet, mode)
