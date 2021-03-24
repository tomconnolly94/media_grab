#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import TPBInterface, QBittorrentInterface,MediaIndexFileInterface
from controllers import QueryGenerationController, NewTorrentController, CompletedDownloadsController
from dataTypes.ProgramMode import PROGRAM_MODE 


def findMediaInfoRecord(mediaInfoRecords, mediaInfoName):
	for record in mediaInfoRecords:
		if record.getShowName() == mediaInfoName:
			return record


def getMediaInfoRecordsWithTorrents(mediaInfoRecords):
    mediaInfoRecordsWithTorrents = []

    for mediaInfoRecord in mediaInfoRecords:

        torrentRecords = TPBInterface.getTorrentRecords(mediaInfoRecord)
        if not torrentRecords:
            continue

        if torrentRecords:
            chosenTorrent = None

            downloadIds = [ torrent.getName() for torrent in torrentRecords ]
            chosenDownloadId = downloadIds[0]

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

    #analyse folder to look for completed downloads
    CompletedDownloadsController.auditDumpCompleteDir()

    mutatingFilter = []

    while True:
        # load information about the requested media
        mediaInfoRecords = MediaIndexFileInterface.loadMediaFile()

        # ascertain mode of program
        if mode == PROGRAM_MODE.TV_EPISODES:
	        # add torrent queries to mediaInfoRecords
            QueryGenerationController.addTVEpisodeQueriesToMediaInfoRecords(mediaInfoRecords)
        else:
            raise ValueError(f"mode: {mode} has no handler statement") 

        if len(mutatingFilter) != 0:
            # apply filter, select record if filter is empty (first run) or if the mediaInfoRecord produced new torrent downloads on the previous run
            mediaInfoRecords = [ mediaInfoRecord for mediaInfoRecord in mediaInfoRecords if mediaInfoRecord.getShowName() in mutatingFilter ]
        
        # add torrent magnet links to mediaInfoRecords
        mediaInfoRecordsWithTorrents = getMediaInfoRecordsWithTorrents(mediaInfoRecords)

        if not mediaInfoRecordsWithTorrents:
            return
            
        # update filter
        mutatingFilter = [ mediaInfoRecord.getShowName() for mediaInfoRecord in mediaInfoRecordsWithTorrents ]

        qbittorrentInterfaceInstance = QBittorrentInterface.getInstance()

        for mediaInfoRecord in mediaInfoRecordsWithTorrents:
            if qbittorrentInterfaceInstance.initTorrentDownload(mediaInfoRecord):
                NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, mode)
