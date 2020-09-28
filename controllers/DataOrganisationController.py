#!/venv/bin/python

# pip dependencies
import json
import os
import logging


seasonTemplates = [
	"s",
	"season",
	"season ",
]


def generateSeasonQueryUrlLists(pbDomain):
	media = loadMediaFile()
	queryUrls = []
	for mediaInfo in media:
		queryUrls.append(generateSeasonIndexQueryUrls(mediaInfo["name"], int(mediaInfo["typeSpecificData"]["latestSeason"]) + 1, pbDomain))

	return queryUrls


def generateSeasonIndexQueryUrls(mediaName, relevantSeason, pbDomain):

	seasonQueries = []

	for template in seasonTemplates:

		searchSection = ""

		for nameFragment in mediaName.split():
			searchSection += nameFragment + "+"
		
		searchSection += "{template}{relevantSeason:>02}".format(template=template.replace(" ", "+"),relevantSeason=relevantSeason)

		# create search url
		seasonQueries.append(f"https://{pbDomain}/search.php?q={searchSection}&cat=0&page=0&orderby=99")

	return seasonQueries