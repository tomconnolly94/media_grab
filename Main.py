#!/venv/bin/python

#pip dependencies
import json
import enum
import itertools
import pprint

#internal dependencies
from interfaces import HttpRequestInterface
from scrapers import IndexPageScraper, TorrentPageScraper
from controllers import BittorrentController
from controllers import DataOrganisationController

localDownloadLocation = "/home/pi/Downloads"

# Using enum class create enumerations
class MEDIA_TYPE(enum.Enum):
	TV = "tv"
	FILM = "film"


def loadMediaFile():
	mediaIndexfile = open("data/MediaIndex.json", "r")
	return json.loads(mediaIndexfile.read())["media"]

def init():
	
	#find site to search for torrents
	pbDomain = HttpRequestInterface.getPBSite()["domain"]
	media = loadMediaFile()
	queryUrls = []

	for mediaInfo in media:
		if mediaInfo["type"] == MEDIA_TYPE.TV.value:
			queryUrls.append(DataOrganisationController.generateTVQueryUrls(mediaInfo, pbDomain))

	return queryUrls, pbDomain


def getTorrentMagnets(query, queryKey):
		
	for queryUrl in query[queryKey]:
		torrentMagnets = IndexPageScraper.scrape(queryUrl)
		if len(torrentMagnets) > 0: # if any torrent magnets are found add them to the master list and dont look for any more
			return torrentMagnets
			
	return None


def main():
	#init all reusable variables
	queryUrls, pbDomain = init()

	#make season queries, scrape torrent page links from page and store them in a list
	for queryUrl in queryUrls:

		#get magnets for seasons queries
		torrentMagnets = getTorrentMagnets(queryUrl, "season_queries")
		if torrentMagnets:
			queryUrl["season_torrent_magnets"].extend(torrentMagnets)

		makeEpisodeQuery = False

		if makeEpisodeQuery:
			# get magnets for episodes queries
			torrentMagnets = getTorrentMagnets(queryUrl, "episode_queries")
			if torrentMagnets:
				queryUrl["episode_torrent_magnets"].extend(torrentMagnets)

	#start torrent
	for queryUrl in queryUrls:

		url = f'https://{pbDomain}{queryUrl["season_torrent_magnets"][0]}'

		torrentMagnet = TorrentPageScraper.scrape(url)
		BittorrentController.initTorrentDownload(torrentMagnet)
		break
	
	#when torrent is finished cp it to mounted network media drive (/mnt/share/media_drive)

	return


if __name__== "__main__":
	main()
