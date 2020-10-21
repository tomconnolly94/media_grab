#!/venv/bin/python

# external dependencies
from dotenv import load_dotenv
import os
from os.path import join, dirname
import logging

# internal dependencies
from interfaces import TPBInterface, MediaFileInterface
from controllers import BittorrentController, DataOrganisationController, TorrentFilterController, LoggingController, NewTorrentController

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

makeEpisodeQueries = False
makeSeasonQueries = True

#intitialise logging module
LoggingController.initLogging()

def findMediaInfoRecord(mediaInfoRecords, mediaInfoName):
	for record in mediaInfoRecords:
		if record["name"] == mediaInfoName:
			return record


def main():

	logging.info("Media grab app started.")

	try:
		TPBInterface.init()
		mediaInfoRecords = MediaFileInterface.loadMediaFile() # information about the wanted media
		mediaSearchQueries = DataOrganisationController.generateSeasonQueries(mediaInfoRecords)

		for mediaInfoName, queries in mediaSearchQueries.items():

			# make query for the mediaInfoRecord, if none are found, try the next query format
			for query in queries:
				torrentQuery = TPBInterface.query('taskmaster')

				if not torrentQuery:
					continue
				
				torrentInfo = []

				for torrent in torrentQuery:
					torrentInfo.append(torrent)
				break


			#filter torrentInfo by applying regex to torrent titles
			mediaInfoRecord = findMediaInfoRecord(mediaInfoRecords, mediaInfoName)
			torrentTitles = [ torrent.title for torrent in torrentInfo ]
			filteredTorrentTitles = TorrentFilterController.filterSeasonTorrents(torrentTitles, mediaInfoRecord)

			#get list of filtered torrent objects
			filteredTorrents = [ torrent for torrent in torrentInfo if torrent.title in 
			filteredTorrentTitles ]

			if filteredTorrents:
				chosenTorrent = filteredTorrents[0]
				logging.info(f'torrentInfo: {chosenTorrent}')

				if BittorrentController.initTorrentDownload(chosenTorrent.magnet_link):
					NewTorrentController.onSuccessfulTorrentAdd(mediaInfoRecord, "latestSeason", chosenTorrent.magnet_link)

	
	except Exception:
		logging.error("Exception occurred", exc_info=True)


if __name__== "__main__":
	main()
