#!/venv/bin/python

# pip dependencies
import json

seasonTemplates = [
	[ "s" ],
	[ "season " ],
	[ "season"],
]

episodeTemplates = [
	[ "s", "e" ],
	[ "s", " e"]
]


def generateTVQueryUrls(pbDomain):
	media = loadMediaFile()
	queryUrls = []
	for mediaInfo in media:
		queryUrls.append(generatesingleMediaQueryUrls(mediaInfo, pbDomain))

	return queryUrls


def loadMediaFile():
	mediaIndexfile = open("data/MediaIndex.json", "r")
	return json.loads(mediaIndexfile.read())["media"]


def generatesingleMediaQueryUrls(mediaInfo, pbDomain):

	seasonQueries = []

	for template in seasonTemplates:

		searchSection = ""

		for fragmentIndex, fragment in enumerate(template):
			value = list(mediaInfo["type_specific_data"].values())[fragmentIndex]

			searchSection += "{fragment}{value:>02}".format(fragment=fragment,value=int(value))

		# create search url
		seasonQueries.append(f"https://{pbDomain}/s/?q={mediaInfo['name']} {searchSection}&page=0&orderby=99")

	episodeQueries = []

	for template in episodeTemplates:

		searchSection = ""

		for fragmentIndex, fragment in enumerate(template):
			value = list(mediaInfo["type_specific_data"].values())[fragmentIndex]

			searchSection += "{fragment}{value:>02}".format(fragment=fragment,value=int(value))

		# create search url
		episodeQueries.append(f"https://{pbDomain}/s/?q={mediaInfo['name']} {searchSection}&page=0&orderby=99")

	return {
		"name": mediaInfo['name'],
		"seasonIndexPageUrls": seasonQueries,
		"episodeIndexPageUrls": episodeQueries,
		"typeSpecificData": mediaInfo["typeSpecificData"]
	}
