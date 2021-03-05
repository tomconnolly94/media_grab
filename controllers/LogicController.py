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
    return sorted(torrents, key=lambda torrent: -1 * int(torrent["seeders"]))
    


def getMediaInfoRecordsWithTorrents(mediaSearchQueries, mediaInfoRecords):
    mediaInfoRecordsWithTorrents = []

    for mediaInfoName, queries in mediaSearchQueries.items():

        torrentRecords = TPBInterface.getTorrentRecords(queries)
        if not torrentRecords:
            return []
        # filter torrentRecords by applying regex to torrent titles
        mediaInfoRecord = findMediaInfoRecord(mediaInfoRecords, mediaInfoName)
        torrentTitles = [ torrent["name"] for torrent in torrentRecords ]
        filteredTorrentTitles = TorrentFilterController.filterEpisodeTorrents(torrentTitles, mediaInfoRecord)
        logging.info(f"{len(torrentTitles)} torrents filtered down to {len(filteredTorrentTitles)}")

        # get list of filtered torrent objects
        filteredTorrents = [ torrent for torrent in torrentRecords if torrent["name"] in filteredTorrentTitles ]

        # order torrents by number of seeders
        filteredSortedTorrents = sortTorrents(filteredTorrents)

        if filteredSortedTorrents:
            chosenTorrent = None

            downloadIds = [ torrent["name"] for torrent in filteredSortedTorrents ]
            chosenDownloadId = DownloadsInProgressFileInterface.findNewDownload(downloadIds)

            if not chosenDownloadId:
                return []


            for torrent in filteredSortedTorrents:
                if chosenDownloadId == torrent["name"]:
                    chosenTorrent = torrent 
                    logging.info(f"Selected torrent: {chosenTorrent['name']} - seeders: {chosenTorrent['seeders']}")
                    break


            # if torrent was not found, return early
            if not chosenTorrent:
                logging.info("No new torrents found,")
                return []

            mediaInfoRecord["magnet"] = chosenTorrent["magnet"].replace(" ", "+")
            mediaInfoRecord["torrentName"] = chosenTorrent["name"]
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
            NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, "latestEpisode", magnet, mode)
