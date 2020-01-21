#!/venv/bin/python

# pip dependencies
import json
import enum
import itertools
import pprint
import re
from dotenv import load_dotenv
import os
from os.path import join, dirname

# internal dependencies
from interfaces import HttpRequestInterface
from scrapers import IndexPageScraper, TorrentPageScraper
from controllers import BittorrentController
from controllers import DataOrganisationController

makeEpisodeQuery = False

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def init():
	# find site to search for torrents
	pbDomain = HttpRequestInterface.getPBSite()["domain"]
	queryRecords = DataOrganisationController.generateTVQueryUrls(pbDomain)

	return queryRecords, pbDomain


def filterTorrentPageUrls(torrentPageUrls, mediaData):

	if not torrentPageUrls:
		return []

	name = mediaData["name"]
	nameFirstLetter = name[0].lower()
	restOfName = name[1:]
	relevantSeason = mediaData["typeSpecificData"]["latestSeason"]

	seasonRegex = fr'[{nameFirstLetter.upper()}|{nameFirstLetter}]{restOfName}.*[Season\s.Ss0]*{relevantSeason}'
	seasonRegex = re.compile(seasonRegex)
	filteredTorrentPageUrls = list(filter(seasonRegex.search, torrentPageUrls))
	return filteredTorrentPageUrls


def getTorrentPageUrls(torrentIndexPages):
		
	for torrentIndexPage in torrentIndexPages:
		torrentPageUrls = IndexPageScraper.scrape(torrentIndexPage)
		if len(torrentPageUrls) > 0:
			return torrentPageUrls
			
	return None

def onSuccessfulTorrentAdd(queryRecord, torrentMagnet):

	# TODO: update data/MediaIndex.json to reflect what has been downloaded 
	
	# TODO: send email notification
	pass


def main():
	queryRecords, pbDomain = init()

	for queryRecord in queryRecords:

		seasonTorrentPageUrls = []
		episodeTorrentPageUrls = []

		# get page urls for seasons queries and filter them
		seasonTorrentPageUrls = filterTorrentPageUrls(getTorrentPageUrls(queryRecord["seasonIndexPageUrls"]), queryRecord)

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
					onSuccessfulTorrentAdd(torrentMagnet)

					# use break to move to the next media item
					break

		elif episodeTorrentPageUrls:
			for torrentPageUrl in episodeTorrentPageUrls:

				torrentPageUrl = f'https://{pbDomain}{torrentPageUrl}'
				torrentMagnet = TorrentPageScraper.scrape(torrentPageUrl)
				
				if torrentMagnet:
					if BittorrentController.initTorrentDownload(torrentMagnet):
						onSuccessfulTorrentAdd(torrentMagnet)

						# use break to move to the next media item
						break
					
	# when torrent is finished cp it to mounted network media drive (/mnt/share/media_drive)

	return


if __name__== "__main__":
	main()
