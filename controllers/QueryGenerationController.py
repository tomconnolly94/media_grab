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

episodeTemplates = [
	"e",
	"e ",
	"episode",
	"episode "
]


def addTVEpisodeQueriesToMediaInfoRecords(mediaInfoRecords):
	"""
	addTVEpisodeQueriesToMediaInfoRecords for each mediaInfoRecord passed in, a group of queries is generated that are, when put through a torrent search engine, likely to return relevant torrent results. This group is assigned to the original object so no return value is required.
	:testedWith: TestQueryGenerationController:test_addTVEpisodeQueriesToMediaInfoRecords
	:param mediaInfoRecords: a list of mediaInfoRecords 
	:return: None
	"""
	queryUrls = {}
	for record in mediaInfoRecords:
		record.setMediaSearchQueries(generateTVEpisodeQueryGroup(record.getShowName(
		), record.getLatestSeasonNumber(), record.getLatestEpisodeNumber()))


def generateTVEpisodeQueryGroup(mediaName, relevantSeason, relevantEpisode):
	"""
	generateTVEpisodeQueryGroup for the input mediaName and the relevant season and episode numbers, use the query templated to generate query strings that are likely to return torrent results
	:testedWith: TestQueryGenerationController:test_generateEpisodeQueryGroup
	:param mediaName: the name of the media
	:param relevantSeason: the season number
	:param relevantEpisode: the episode number
	:return: a list of query strings
	"""
	queries = []

	for index, template in enumerate(episodeTemplates):
		# create search url
		if " " in template:
			queries.append(f'"{mediaName}" {seasonTemplates[index]}{relevantSeason} {template}{relevantEpisode}')
		else:
			queries.append(f'"{mediaName}" {seasonTemplates[index]}{relevantSeason:>02}{template}{relevantEpisode:>02}') # force season number to two digits, e.g. "1" -> "01"

	return queries
