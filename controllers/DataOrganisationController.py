#!/venv/bin/python

seasonTemplates = [
	[ "s" ],
	[ "season " ],
	[ "season"],
]

episodeTemplates = [
	[ "s", "e" ],
	[ "s", " e"]
]

def generateTVQueryUrls(mediaInfo, pbDomain):
	
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

	return {
		"name": mediaInfo['name'],
		"season_queries": seasonQueries,
		"episode_queries": episodeQueries,
		"season_torrent_magnets": [],
		"episode_torrent_magnets": []
	}
