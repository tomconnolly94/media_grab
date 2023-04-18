#!/venv/bin/python

# external dependencies
import logging


# internal dependencies
from src.interfaces import TPBInterface, QBittorrentInterface, MediaIndexFileInterface
from src.controllers import QueryGenerationController, NewTorrentController, CompletedDownloadsController
from src.dataTypes.ProgramMode import PROGRAM_MODE
from src.controllers import ErrorController


def getMediaInfoRecordsWithTorrents(mediaInfoRecords):
    """
    getMediaInfoRecordsWithTorrents uses the TPB interface to assign a torrentRecord to each mediaInfoRecord passed in, records for which a torrent cannot be found are not returned 
    :testedWith: TestLogicController:test_getMediaInfoRecordsWithTorrents
    :param mediaInfoRecords: the downloadId of the download
    :return: mediaInfoRecords with valid torrentRecords
    """
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
    """
    runProgramLogic groups the core of the top level operations of the program together
    :testedWith: TestLogicController:test_runProgramLogic
    :param mode: the mode of the program run, the type of media the program is focusing on
    :return: None
    """
    try:
        #analyse folder to look for completed downloads
        CompletedDownloadsController.auditDumpCompleteDir()
    except Exception as exception:
        ErrorController.reportError("Exception occurred - runProgramLogic, audit dump stage", exception=exception, sendEmail=True)

    mutatingFilter = []

    while True:
        # load information about the requested media
        mediaInfoRecords = MediaIndexFileInterface.loadMediaFile()

        # ascertain mode of program
        if mode == PROGRAM_MODE.TV:
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
            try:
                if qbittorrentInterfaceInstance.initTorrentDownload(mediaInfoRecord):
                    NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, mode)
            except Exception as exception:
                ErrorController.reportError("Exception occurred - runProgramLogic, init download stage", exception=exception, sendEmail=True)
