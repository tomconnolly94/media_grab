#!/venv/bin/python

# pip dependencies
import json
import os

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
	with open(os.getenv("MEDIA_FILE"), "r") as mediaIndexfile:
		return json.loads(mediaIndexfile.read())["media"]


def generatesingleMediaQueryUrls(mediaInfo, pbDomain):

	seasonQueries = []
	# increment last episode/season numbers
	mediaInfo["typeSpecificData"]["latestSeason"] = str(int(mediaInfo["typeSpecificData"]["latestSeason"]) + 1)
	mediaInfo["typeSpecificData"]["latestEpisode"] = str(int(mediaInfo["typeSpecificData"]["latestEpisode"]) + 1)

	for template in seasonTemplates:

		searchSection = ""

		for fragmentIndex, fragment in enumerate(template):
			value = list(mediaInfo["typeSpecificData"].values())[fragmentIndex]

			searchSection += "{fragment}{value:>02}".format(fragment=fragment,value=int(value))

		# create search url
		seasonQueries.append(f"https://{pbDomain}/s/?q={mediaInfo['name']} {searchSection}&page=0&orderby=99")

	episodeQueries = []

	for template in episodeTemplates:

		searchSection = ""

		for fragmentIndex, fragment in enumerate(template):
			value = list(mediaInfo["typeSpecificData"].values())[fragmentIndex]

			searchSection += "{fragment}{value:>02}".format(fragment=fragment,value=int(value))

		# create search url
		episodeQueries.append(f"https://{pbDomain}/s/?q={mediaInfo['name']} {searchSection}&page=0&orderby=99")

	return {
		"name": mediaInfo['name'],
		"seasonIndexPageUrls": seasonQueries,
		"episodeIndexPageUrls": episodeQueries,
		"typeSpecificData": mediaInfo["typeSpecificData"]
	}
