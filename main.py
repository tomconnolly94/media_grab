from controllers import http_request
import json
import enum
from scrapers import index_page_scraper

localDownloadLocation = "/home/pi/Downloads"

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
				"episode_queries": episodeQueries
			})

	return queryUrls


def main():
	#init all reusable variables
	queryUrls = init()

	#make season queries, scrape torrent page links from page and store them in a list
	torrent_page_links = [ index_page_scraper.scrape(seasonQueryURL) for seasonQueryURL in queryUrl.season_queries for queryUrl in queryUrls ]


	#if season query fails, make individual episode queries


	#start torrent, download to localDownloadLocation

	
	#when torrent is finished cp it to mounted network media_drive

	pass





if __name__== "__main__":
	main()
