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


def generateTVEpisodeQueries(mediaInfoRecords):
	queryUrls = {}
	for record in mediaInfoRecords:
		queryUrls[record.getShowName()] = generateTVEpisodeQueryGroup(record.getShowName(), record.getLatestSeasonNumber(), record.getLatestEpisodeNumber())
	return queryUrls


def generateTVEpisodeQueryGroup(mediaName, relevantSeason, relevantEpisode):
	queries = []

	for index, template in enumerate(episodeTemplates):
		# create search url
		if " " in template:
			queries.append(f'"{mediaName}" {seasonTemplates[index]}{relevantSeason} {template}{relevantEpisode}')
		else:
			queries.append(f'"{mediaName}" {seasonTemplates[index]}{relevantSeason:>02}{template}{relevantEpisode:>02}') # force season number to two digits, e.g. "1" -> "01"

	return queries
