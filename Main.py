#!/venv/bin/python

# pip dependencies
import json
import enum
import itertools
import pprint

# internal dependencies
from interfaces import HttpRequestInterface
from scrapers import IndexPageScraper, TorrentPageScraper
from controllers import BittorrentController
from controllers import DataOrganisationController


def loadMediaFile():
	mediaIndexfile = open("data/MediaIndex.json", "r")
	return json.loads(mediaIndexfile.read())["media"]


def init():
	
	# find site to search for torrents
	pbDomain = HttpRequestInterface.getPBSite()["domain"]
	media = loadMediaFile()
	queryUrls = []

	for mediaInfo in media:
		queryUrls.append(DataOrganisationController.generateTVQueryUrls(mediaInfo, pbDomain))

	return queryUrls, pbDomain


def getTorrentPageUrls(torrentIndexPages):
		
	for torrentIndexPages in torrentIndexPages:
		#TODO: apply some sort of regex to the name of the torrent page 
		# url to ensure only strictly relevant page URls are returned.
		torrentPageUrls = IndexPageScraper.scrape(torrentIndexPages)
		if len(torrentPageUrls) > 0:
			return torrentPageUrls
			
	return None


def main():
	# init all reusable variables
	queryUrls, pbDomain = init()

	# scrape torrent pages for torrent magnets
	for queryUrl in queryUrls:

		# get magnets for seasons queries
		seasonTorrentPageUrls = getTorrentPageUrls(queryUrl["seasonIndexPageUrls"])

		makeEpisodeQuery = False

		if makeEpisodeQuery:
			# get magnets for episodes queries
			episodeTorrentPageUrls = getTorrentPageUrls(queryUrl["episodeIndexPageUrls"])


		if seasonTorrentPageUrls:
			
			for torrentPageUrl in seasonTorrentPageUrls:

				torrentPageUrl = f'https://{pbDomain}{torrentPageUrl}'
				torrentMagnet = TorrentPageScraper.scrape(torrentPageUrl)
				
				if torrentMagnet:
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
