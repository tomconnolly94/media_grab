#!/venv/bin/python

# pip dependencies
import json
import enum
import itertools
from dotenv import load_dotenv
import os
from os.path import join, dirname
import logging
import time

# internal dependencies
from interfaces import HttpRequestInterface, MailInterface
from scrapers import IndexPageScraper, TorrentPageScraper
from controllers import BittorrentController, DataOrganisationController, TorrentFilterController

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logFormat = '%(asctime)s - %(levelname)s - %(message)s'
logDateFormat = '%d-%b-%y %H:%M:%S'

if os.getenv("ENVIRONMENT") == "production":
	logFilename = f"logs/media-grab_{time.strftime('%d-%m-%Y_%H-%M')}.log"
	logging.basicConfig(filename=logFilename, filemode='w', format=logFormat, datefmt=logDateFormat, level=logging.INFO)
else:
	logging.basicConfig(format=logFormat, datefmt=logDateFormat, level=logging.INFO)

logging.info('media_grab app started.')

makeEpisodeQueries = True
makeSeasonQueries = False


def initDomain():
	# find site to search for torrents
	return HttpRequestInterface.getPBSite()["domain"]


def initQueryRecords(pbDomain):
	return DataOrganisationController.generateTVQueryUrls(pbDomain)


def getTorrentPageUrls(torrentIndexPages):
		
	for torrentIndexPage in torrentIndexPages:
		logging.info("Index page torrent > " + torrentIndexPage)
		torrentPageUrls = IndexPageScraper.scrape(torrentIndexPage)
		if len(torrentPageUrls) > 0:
			return torrentPageUrls
			
	return None


def writeMediaFile(queryRecord, updateableField):
	
	with open(os.getenv("MEDIA_FILE"), 'r') as mediaFileSrc:
		media = json.load(mediaFileSrc)["media"]

	for mediaRecord in media:
		if mediaRecord["name"] == queryRecord["name"]:
			mediaRecord["typeSpecificData"][updateableField] = queryRecord["typeSpecificData"][updateableField]

	media = { "media": media }

	with open(os.getenv("MEDIA_FILE"), "w") as mediaFileTarget:
		json.dump(media, mediaFileTarget)

	return

def onSuccessfulTorrentAdd(queryRecord, updateableField, torrentMagnet):

	writeMediaFile(queryRecord, updateableField)

	# TODO: send email notification
	addMessage = f'ADDED TORRENT: {queryRecord["name"]} {updateableField} {queryRecord["typeSpecificData"][updateableField]} \n\n Magnet:{torrentMagnet}'
	MailInterface.sendMail(addMessage)
	
	logging.info(addMessage)


def main():

	try:
		pbDomain = initDomain()
		queryRecords = initQueryRecords(pbDomain)

		for queryRecord in queryRecords:

			seasonTorrentPageUrls = []
			episodeTorrentPageUrls = []

			if makeSeasonQueries:
				# get page urls for seasons queries and filter them
				logging.info(f'seasonIndexPageUrls: {getTorrentPageUrls(queryRecord["seasonIndexPageUrls"])}')
				seasonTorrentPageUrls = TorrentFilterController.filterSeasonTorrentPageUrls(getTorrentPageUrls(queryRecord["seasonIndexPageUrls"]), queryRecord)

			if makeEpisodeQueries:
				# get page urls for episodes queries
				logging.info(f'episodeIndexPageUrls: {getTorrentPageUrls(queryRecord["episodeIndexPageUrls"])}')
				episodeTorrentPageUrls = TorrentFilterController.filterEpisodeTorrentPageUrls(getTorrentPageUrls(queryRecord["episodeIndexPageUrls"]), queryRecord)

			if seasonTorrentPageUrls:
				# TODO: lines 89-103 are very similar to 106-119 find a way to remove duplication
				for torrentPageUrl in seasonTorrentPageUrls:

					torrentPageUrl = f'https://{pbDomain}{torrentPageUrl}'
					torrentMagnet = TorrentPageScraper.scrape(torrentPageUrl)
					
					# skip page if torrent magnet cannot be accessed
					if not torrentMagnet:
						continue

					# if adding torrent is successful, update various things
					if BittorrentController.initTorrentDownload(torrentMagnet):
						onSuccessfulTorrentAdd(queryRecord, "latestSeason", torrentMagnet)

						# use break to move to the next media item
						break

			elif episodeTorrentPageUrls:
				for torrentPageUrl in episodeTorrentPageUrls:

					torrentPageUrl = f'https://{pbDomain}{torrentPageUrl}'
					torrentMagnet = TorrentPageScraper.scrape(torrentPageUrl)
					
					# skip page if torrent magnet cannot be accessed
					if not torrentMagnet:
						continue

					if BittorrentController.initTorrentDownload(torrentMagnet):
						onSuccessfulTorrentAdd(queryRecord, "latestEpisode", torrentMagnet)

						# use break to move to the next media item
						break
	
	except Exception as e:
		logging.error("Exception occurred", exc_info=True)


if __name__== "__main__":
	main()
