#!/venv/bin/python

# pip dependencies
import json
import enum
import itertools
from dotenv import load_dotenv
import os
from os.path import join, dirname

# internal dependencies
from interfaces import HttpRequestInterface
from scrapers import IndexPageScraper, TorrentPageScraper
from controllers import BittorrentController, DataOrganisationController, TorrentFilterController

makeEpisodeQuery = False

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def init():
	# find site to search for torrents
	pbDomain = HttpRequestInterface.getPBSite()["domain"]
	queryRecords = DataOrganisationController.generateTVQueryUrls(pbDomain)

	return queryRecords, pbDomain


def getTorrentPageUrls(torrentIndexPages):
		
	for torrentIndexPage in torrentIndexPages:
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
	pass


def main():
	queryRecords, pbDomain = init()

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
					print(f"ADDED TORRENT: {torrentMagnet}")
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
					
	# when torrent is finished cp it to mounted network media drive (/mnt/share/media_drive)

	return


if __name__== "__main__":
	main()
