#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import TPBInterface, DownloadsInProgressFileInterface, QBittorrentInterface,MediaIndexFileInterface
from controllers import QueryGenerationController, NewTorrentController, CompletedDownloadsController
from data_types.ProgramMode import PROGRAM_MODE 


def findMediaInfoRecord(mediaInfoRecords, mediaInfoName):
	for record in mediaInfoRecords:
		if record["name"] == mediaInfoName:
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

            downloadIds = [ torrent["name"] for torrent in torrentRecords ]
            chosenDownloadId = DownloadsInProgressFileInterface.findNewDownload(downloadIds)

            if not chosenDownloadId:
                continue


            for torrent in torrentRecords:
                if chosenDownloadId == torrent["name"]:
                    chosenTorrent = torrent 
                    logging.info(f"Selected torrent: {chosenTorrent['name']} - seeders: {chosenTorrent['seeders']}")
                    break


            # if torrent was not found, return early
            if not chosenTorrent:
                logging.info("No new torrents found")
                continue

            mediaInfoRecord["magnet"] = chosenTorrent["magnet"].replace(" ", "+")
            mediaInfoRecord["torrentName"] = chosenTorrent["name"]
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

        for mediaInfoRecord in mediaInfoRecordsWithTorrents:
            # create internal id to be used as a temporary folder when downloading and to keep in the DownloadsInProgress.json file as an identifier
            mediaInfoRecord["mediaGrabId"] = f'{mediaInfoRecord["name"]}--s{mediaInfoRecord["typeSpecificData"]["latestSeason"]}e{mediaInfoRecord["typeSpecificData"]["latestEpisode"]}'

            if QBittorrentInterface.initTorrentDownload(mediaInfoRecord):
                NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, "latestEpisode", mediaInfoRecord["magnet"], mode)
