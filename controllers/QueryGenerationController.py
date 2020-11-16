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


def generateTVSeasonQueries(mediaInfoRecords):
	queryUrls = {}
	for record in mediaInfoRecords:
		queryUrls[record["name"]] = generateTVSeasonQueryGroup(record["name"], int(record["typeSpecificData"]["latestSeason"]))
	return queryUrls


def generateTVSeasonQueryGroup(mediaName, relevantSeason):
	queries = []

	for template in seasonTemplates:
		# create search url
		queries.append(f"{mediaName} {template}{relevantSeason:>02}")

	return queries
	

def generateMovieQueries(mediaInfoRecords):	
	return [mediaInfoRecords["name"]]