from controllers import http_request
import json
import enum

localDownloadLocation = "/home/pi/Downloads"

# Using enum class create enumerations
class MEDIA_TYPE(enum.Enum):
	TV = "tv"
	FILM = "film"

def init():
	
	#find site to search for torrents
	pbDomain = http_request.getPBSite()["domain"]
	mediaIndexfile = open("data/media_index.json", "r")
	media = json.loads(mediaIndexfile.read())["media"]
	queryUrls = []

	for media_info in media:

		searchSuffix = ""

		print(media_info["type"])
		print(MEDIA_TYPE.TV.value)

		if media_info["type"] == MEDIA_TYPE.TV.value:
			searchSuffix += f's{media_info["type_specific_data"]["latest_season"]} e{media_info["type_specific_data"]["latest_season"]}'
		
		print(searchSuffix)

		#create search url
		queryUrls.append(f"https://{pbDomain}/s/?q={media_info['name']}{searchSuffix}&page=0&orderby=99")

		#TODO: create multiple variants of the search URL 
		#1. "name s0x" 2. "name season 0x" 3. "name season0x" 4. "name s0xe0x" 5. "name s0x e0x" 

	print(queryUrls)
	return queryUrls


def main():
	#init all reusable variables
	queryUrls = init()


	#make season query


	#if season query fails, make individual episode queries


	#start torrent, download to localDownloadLocation

	
	#when torrent is finished cp it to mounted network media_drive

	pass





if __name__== "__main__":
	main()
