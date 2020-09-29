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

makeEpisodeQueries = False
makeSeasonQueries = True


def getPDDomain():
	# find site to search for torrents
	return HttpRequestInterface.getPBSite()


def getTorrentInfo(queryUrlList):
		
	for queryUrl in queryUrlList:
		logging.info("Index page torrent > " + queryUrl)
		torrents = IndexPageScraper.scrape(queryUrl)
		if torrents:
			return torrents
			
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


def loadMediaFile():
	with open(os.getenv("MEDIA_FILE"), "r") as mediaIndexfile:
		return json.loads(mediaIndexfile.read())["media"]


def findMediaInfo(mediaName, mediaInfoRecords):
	for mediaInfoRecord in mediaInfoRecords:
		if mediaName == mediaInfoRecord["name"]:
			return mediaInfoRecord
		
	return None

def main():

	try:
		pbDomain = getPDDomain()
		mediaInfoRecords = loadMediaFile() # information about the wanted media
		queryUrlLists = DataOrganisationController.generateSeasonQueryUrlLists(pbDomain, mediaInfoRecords) # generate urls for each media itemS

		#TODO: somehow pass the correct member of mediaInfo into the filterSeasonTorrents function on line 102

		for mediaName, queryUrlList in queryUrlLists.items():

			# get page urls for seasons queries and filter them
			torrentInfo = getTorrentInfo(queryUrlList)
			logging.info(f'torrentInfo: {torrentInfo}')

			mediaInfoRecord = findMediaInfo(mediaName, mediaInfoRecords)

			if mediaInfoRecord:
				torrentInfo = TorrentFilterController.filterSeasonTorrents(torrentInfo, mediaInfoRecord)

				if BittorrentController.initTorrentDownload(torrentInfo["itemMagnetLink"]):
					onSuccessfulTorrentAdd(mediaInfoRecord, "latestSeason", torrentInfo["itemMagnetLink"])

	
	except Exception as e:
		logging.error("Exception occurred", exc_info=True)


if __name__== "__main__":
	main()
