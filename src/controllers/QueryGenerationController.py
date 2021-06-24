#!/venv/bin/python


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
	
	for record in mediaInfoRecords:

		seasonQueries = generateTVSeasonQuery(record.getShowName(), record.getLatestSeasonNumber()) if record.getLatestEpisodeNumber() == 1 else []
		episodeQueries = generateTVEpisodeQueryGroup(record.getShowName(), record.getLatestSeasonNumber(), record.getLatestEpisodeNumber())

		record.setMediaSearchQueries(seasonQueries + episodeQueries)


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

def generateTVSeasonQuery(mediaName, relevantSeason):
	"""
	generateTVSeasonQuery for the input mediaName and the relevant season, use the query templates to generate query strings that are likely to return torrent results for a full season
	:testedWith: none yet
	:param mediaName: the name of the media
	:param relevantSeason: the season number
	:return: a list of query strings
	"""
	queries = []

	for template in seasonTemplates[2:]:
		# create search url
		if " " in template:
			queries.append(
				f'"{mediaName}" {template}{relevantSeason}')
		else:
			# force season number to two digits, e.g. "1" -> "01"
			queries.append(
				f'"{mediaName}" {template}{relevantSeason:>02}')

	return queries
