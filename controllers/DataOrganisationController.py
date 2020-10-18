#!/venv/bin/python

# pip dependencies
import json
import os
import logging


seasonTemplates = [
	"s",
	"s ",
	"season",
	"season "
]


def generateSeasonQueries(mediaInfoRecords):
	queryUrls = {}
	for record in mediaInfoRecords:
		queryUrls[record["name"]] = generateSeasonQueryGroup(record["name"], int(record["typeSpecificData"]["latestSeason"]))
	return queryUrls


def generateSeasonQueryGroup(mediaName, relevantSeason):

	seasonQueries = []

	for template in seasonTemplates:
		# create search url
		seasonQueries.append(f"{mediaName} {template}{relevantSeason:>02}")

	return seasonQueries