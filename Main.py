#!/venv/bin/python

#pip dependencies
from controllers import http_request
import json
import enum
import itertools
import pprint

#internal dependencies
from scrapers import index_page_scraper
from controllers import bit_torrent

localDownloadLocation = "/home/pi/Downloads"
pp = pprint.PrettyPrinter(indent=4)

# Using enum class create enumerations
class MEDIA_TYPE(enum.Enum):
	TV = "tv"
	FILM = "film"

seasonTemplates = [
	[ "s" ],
	[ "season " ],
	[ "season"],
]

episodeTemplates = [
	[ "s", "e" ],
	[ "s", " e"]
]		

def init():
	
	#find site to search for torrents
	pbDomain = http_request.getPBSite()["domain"]
	mediaIndexfile = open("data/media_index.json", "r")
	media = json.loads(mediaIndexfile.read())["media"]
	queryUrls = []

	for mediaInfo in media:

		if mediaInfo["type"] == MEDIA_TYPE.TV.value:
			
			#TODO: create multiple variants of the search URL 
			#1. "name s0x" 2. "name season 0x" 3. "name season0x" 4. "name s0xe0x" 5. "name s0x e0x" 

			seasonQueries = []

			for template in seasonTemplates:

				searchSection = ""

				for fragmentIndex, fragment in enumerate(template):
					value = list(mediaInfo["type_specific_data"].values())[fragmentIndex]

					searchSection += "{fragment}{value:>02}".format(fragment=fragment,value=int(value))

				#create search url
				seasonQueries.append(f"https://{pbDomain}/s/?q={mediaInfo['name']} {searchSection}&page=0&orderby=99")

			episodeQueries = []

			for template in episodeTemplates:

				searchSection = ""

				for fragmentIndex, fragment in enumerate(template):
					value = list(mediaInfo["type_specific_data"].values())[fragmentIndex]

					searchSection += "{fragment}{value:>02}".format(fragment=fragment,value=int(value))

				#create search url
				episodeQueries.append(f"https://{pbDomain}/s/?q={mediaInfo['name']} {searchSection}&page=0&orderby=99")

			queryUrls.append({
				"name": mediaInfo['name'],
				"season_queries": seasonQueries,
				"episode_queries": episodeQueries,
				"season_torrent_magnets": [],
				"episode_torrent_magnets": []
			})

	return queryUrls

def groupQueryUrls(queryUrls, queryType):
	urlList = []
	for queryUrl in queryUrls:
		urlList.extend(queryUrl[queryType])
	return urlList


def main():
	#init all reusable variables
	queryUrls = init()

	#make season queries, scrape torrent page links from page and store them in a list
	for queryUrl in queryUrls:
		
		for seasonQueryUrl in queryUrl["season_queries"]:
			torrentMagnets = index_page_scraper.scrape(seasonQueryUrl)
			if len(torrentMagnets) > 0: # if any torrent magnets are found add them to the master list and dont look for any more
				queryUrl["season_torrent_magnets"].extend(torrentMagnets)
				break

		makeEpisodeQuery = False

		if makeEpisodeQuery:
			# if no season torrent magnets can be found, look for episode torrent magnets
			for episodeQueryUrl in queryUrl["episode_queries"]:
				torrentMagnets = index_page_scraper.scrape(episodeQueryUrl)
				if len(torrentMagnets) > 0: # if any torrent magnets are found add them to the master list and dont look for any more
					queryUrl["episode_torrent_magnets"].extend(torrentMagnets)
					break

	pp.pprint(queryUrls)
	#start torrent, download to localDownloadLocation
	for queryUrl in queryUrls:
		bit_torrent.initTorrent(queryUrl["season_torrent_magnets"][0])
		break
	
	#when torrent is finished cp it to mounted network media_drive

	return





if __name__== "__main__":
	main()
