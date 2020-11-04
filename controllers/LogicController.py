#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import TPBInterface, MediaFileInterface
from controllers import BittorrentController, DataOrganisationController, TorrentFilterController, NewTorrentController


def findMediaInfoRecord(mediaInfoRecords, mediaInfoName):
	for record in mediaInfoRecords:
		if record["name"] == mediaInfoName:
			return record


def getMediaInfoRecordsWithTorrents(mediaSearchQueries, mediaInfoRecords):
    mediaInfoRecordsWithTorrents = []

    for mediaInfoName, queries in mediaSearchQueries.items():

        torrentRecords = TPBInterface.getTorrentRecords(queries)

        #filter torrentRecords by applying regex to torrent titles
        mediaInfoRecord = findMediaInfoRecord(mediaInfoRecords, mediaInfoName)
        torrentTitles = [ torrent.title for torrent in torrentRecords ]
        filteredTorrentTitles = TorrentFilterController.filterSeasonTorrents(torrentTitles, mediaInfoRecord)

        #get list of filtered torrent objects
        filteredTorrents = [ torrent for torrent in torrentRecords if torrent.title in filteredTorrentTitles ]

        if filteredTorrents:
            chosenTorrent = filteredTorrents[0]
            logging.info(f'torrentInfo: {chosenTorrent.magnet_link}')
            mediaInfoRecord["magnet_link"] = chosenTorrent.magnet_link
            mediaInfoRecordsWithTorrents.append(mediaInfoRecord)

    return mediaInfoRecordsWithTorrents


def runProgramLogic(mediaInfoRecords):
    mediaSearchQueries = DataOrganisationController.generateSeasonQueries(mediaInfoRecords)

    mediaInfoRecordsWithTorrents = getMediaInfoRecordsWithTorrents(mediaSearchQueries, mediaInfoRecords)

    for mediaInfoRecord in mediaInfoRecordsWithTorrents:
        magnet = mediaInfoRecord["magnet_link"]
        if BittorrentController.initTorrentDownload(magnet):
            NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, "latestSeason", magnet)
