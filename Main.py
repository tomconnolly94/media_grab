#!/venv/bin/python

# pip dependencies
import json
import enum
import itertools
from dotenv import load_dotenv
import os
from os.path import join, dirname

# internal dependencies
from interfaces import HttpRequestInterface, MailInterface
from scrapers import IndexPageScraper, TorrentPageScraper
from controllers import BittorrentController, DataOrganisationController, TorrentFilterController

makeEpisodeQuery = False

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def initDomain():
	# find site to search for torrents
	return HttpRequestInterface.getPBSite()["domain"]


def initQueryRecords(pbDomain):
	return DataOrganisationController.generateTVQueryUrls(pbDomain)


def getTorrentPageUrls(torrentIndexPages):
		
	for torrentIndexPage in torrentIndexPages:
		print("Index page torrent > " + torrentIndexPage)
		torrentPageUrls = IndexPageScraper.scrape(torrentIndexPage)
		if len(torrentPageUrls) > 0:
			return torrentPageUrls
			
	return None


def onSuccessfulTorrentAdd(queryRecord, updateableField, torrentMagnet):

	# TODO: update data/MediaIndex.json to reflect what has been downloaded 
	with open(os.getenv("MEDIA_FILE"), 'r') as mediaFileSrc:
		media = json.load(mediaFileSrc)["media"]

	for mediaRecord in media:
		if mediaRecord["name"] == queryRecord["name"]:
			mediaRecord["typeSpecificData"][updateableField] = queryRecord["typeSpecificData"][updateableField]

	media = { "media": media }

	with open(os.getenv("MEDIA_FILE"), "w") as mediaFileTarget:
		json.dump(media, mediaFileTarget)

	# TODO: send email notification
	addMessage = f'ADDED TORRENT: {queryRecord["name"]} season {queryRecord["typeSpecificData"][updateableField]} \n\n Magnet:{torrentMagnet}'
	MailInterface.sendMail(addMessage)
	
	print(addMessage)


def main():

	while True:
		pbDomain = initDomain()
		queryRecords = initQueryRecords(pbDomain)

		for queryRecord in queryRecords:

			seasonTorrentPageUrls = []
			episodeTorrentPageUrls = []

			# get page urls for seasons queries and filter them
			seasonTorrentPageUrls = TorrentFilterController.filterTorrentPageUrls(getTorrentPageUrls(queryRecord["seasonIndexPageUrls"]), queryRecord)

			if makeEpisodeQuery:
				# get page urls for episodes queries
				episodeTorrentPageUrls = getTorrentPageUrls(queryRecord["episodeIndexPageUrls"])


			if seasonTorrentPageUrls:
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
					
					if torrentMagnet:
						if BittorrentController.initTorrentDownload(torrentMagnet):
							onSuccessfulTorrentAdd(queryRecord, "latestEpisode", torrentMagnet)

							# use break to move to the next media item
							break


if __name__== "__main__":
	main()
