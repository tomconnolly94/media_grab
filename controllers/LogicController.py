#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import TPBInterface, DownloadsInProgressFileInterface, QBittorrentInterface,MediaIndexFileInterface
from controllers import QueryGenerationController, NewTorrentController, CompletedDownloadsController
from dataTypes.ProgramMode import PROGRAM_MODE 


def findMediaInfoRecord(mediaInfoRecords, mediaInfoName):
	for record in mediaInfoRecords:
		if record.getShowName() == mediaInfoName:
			return record


def getMediaInfoRecordsWithTorrents(mediaSearchQueries, mediaInfoRecords):
    mediaInfoRecordsWithTorrents = []

    for mediaInfoName, queries in mediaSearchQueries.items():
        
        # filter torrentRecords by applying regex to torrent titles
        mediaInfoRecord = findMediaInfoRecord(mediaInfoRecords, mediaInfoName)
        
        torrentRecords = TPBInterface.getTorrentRecords(queries, mediaInfoRecord)
        if not torrentRecords:
            continue

        if torrentRecords:
            chosenTorrent = None

            downloadIds = [ torrent.getName() for torrent in torrentRecords ]
            chosenDownloadId = DownloadsInProgressFileInterface.findNewDownload(downloadIds)

            if not chosenDownloadId:
                continue


            for torrent in torrentRecords:
                if chosenDownloadId == torrent.getName():
                    chosenTorrent = torrent 
                    logging.info(f"Selected torrent: {chosenTorrent.getName()} - seeders: {chosenTorrent.getSeeders()}")
                    break


            # if torrent was not found, return early
            if not chosenTorrent:
                logging.info("No new torrents found")
                continue

            mediaInfoRecord.setTorrentRecord(chosenTorrent)
            mediaInfoRecordsWithTorrents.append(mediaInfoRecord)

    return mediaInfoRecordsWithTorrents


def runProgramLogic(mode):

    while True:
        # load information about the requested media
        mediaInfoRecords = MediaIndexFileInterface.loadMediaFile()

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

        if not mediaInfoRecordsWithTorrents:
            return

        qbittorrentInterfaceInstance = QBittorrentInterface.getInstance()

        for mediaInfoRecord in mediaInfoRecordsWithTorrents:
            if qbittorrentInterfaceInstance.initTorrentDownload(mediaInfoRecord):
                NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, "latestEpisode", mediaInfoRecord.getTorrentRecord().getMagnet(), mode)
