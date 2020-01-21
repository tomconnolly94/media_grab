#!/venv/bin/python

# pip dependencies
import json
import enum
import itertools
import pprint
import re

# internal dependencies
from interfaces import HttpRequestInterface
from scrapers import IndexPageScraper, TorrentPageScraper
from controllers import BittorrentController
from controllers import DataOrganisationController

makeEpisodeQuery = False

def init():
	# find site to search for torrents
	pbDomain = HttpRequestInterface.getPBSite()["domain"]
	queryRecords = DataOrganisationController.generateTVQueryUrls(pbDomain)

	return queryRecords, pbDomain


def filterTorrentPageUrls(torrentPageUrls, mediaData):
	seasonRegex1 = f'Vikings.*Season[\s.Ss]*0*5'
	seasonRegex = re.compile(rf'{seasonRegex1}')
	return list(filter(seasonRegex.search, torrentPageUrls))


def getTorrentPageUrls(torrentIndexPages):
		
	for torrentIndexPage in torrentIndexPages:
		#TODO: apply some sort of regex to the name of the torrent page 
		# url to ensure only strictly relevant page URls are returned.
		torrentPageUrls = IndexPageScraper.scrape(torrentIndexPage)
		if len(torrentPageUrls) > 0:
			return torrentPageUrls
			
	return None


def main():
	queryRecords, pbDomain = init()

	for queryRecord in queryRecords:

		# get page urls for seasons queries
		seasonTorrentPageUrls = getTorrentPageUrls(queryRecord["seasonIndexPageUrls"])
		filterTorrentPageUrls(torrentPageUrls, queryRecord["typeSpecificData"])

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
					# TODO: send email notification

					# TODO: update data/MediaIndex.json to reflect what has been downloaded 

					# use break to move to the next media item
					break

		elif episodeTorrentPageUrls:
			for torrentPageUrl in episodeTorrentPageUrls:

				torrentPageUrl = f'https://{pbDomain}{torrentPageUrl}'
				torrentMagnet = TorrentPageScraper.scrape(torrentPageUrl)
				
				if torrentMagnet:
					if BittorrentController.initTorrentDownload(torrentMagnet):
						# TODO: send email notification

						# TODO: update data/MediaIndex.json to reflect what has been downloaded 

						# use break to move to the next media item
						break
					
	# when torrent is finished cp it to mounted network media drive (/mnt/share/media_drive)

	return


if __name__== "__main__":
	main()
