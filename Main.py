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


def main():

	logging.info("Media grab app started.")

	try:
		TPBInterface.init()
		mediaInfoRecords = MediaFileInterface.loadMediaFile() # information about the wanted media
		mediaSearchQueries = DataOrganisationController.generateSeasonQueries(mediaInfoRecords)

		for mediaInfoName, mediaSearchQueries in mediaSearchQueries.items():

			# make query for the mediaInfoRecord, if none are found, try the next query format
			for query in mediaSearchQueries:
				torrentInfo = TPBInterface.query(query)

				if torrentInfo:
					break

			#filter torrentInfo by applying regex to torrent titles
			filteredTorrentTitles = TorrentFilterController.filterSeasonTorrents([ torrent["title"] for torrent in torrentInfo ], mediaInfoRecords[mediaInfoName])

			#get list of filtered torrent objects
			filteredTorrents = [ torrent for torrent in torrentInfo if torrentInfo["title"] in 
			filteredTorrentTitles ]

			if filteredTorrents:
				chosenTorrent = filteredTorrents[0]
				logging.info(f'torrentInfo: {chosenTorrent}')

				if BittorrentController.initTorrentDownload(torrentInfo["itemMagnetLink"]):
					NewTorrentController.onSuccessfulTorrentAdd(chosenTorrent["magnet_link"], "latestSeason", torrentInfo["itemMagnetLink"])

	
	except Exception:
		logging.error("Exception occurred", exc_info=True)


if __name__== "__main__":
	main()
