#!/venv/bin/python

# external dependencies
import os
import json
from interfaces import TheMovieDatabaseInterface
import logging

# internal dependencies
from dataTypes.MediaInfoRecord import MediaInfoRecord

writeFile = True


def incrementEpisode(mediaInfoRecords, queryMediaInfoRecord):
	"""
	incrementEpisode takes a set of mediaInfoRecords finds the one that matches the queryMediaInfoRecord and updates the episode number, incrementing to the first episode of a new season if theMovieDatabaseInterface suggests that is necessary
	:testedWith: TestMediaIndexFileInterface:test_incrementEpisode
	:param mediaInfoRecords: the set of MediaInfoRecord's, one of which should be updated
	:param queryMediaInfoRecord: the relevant MediaInfoRecord that corresponds to the record that should be updated
	:return: None if the queryMediaInfoRecord could not be found, the set of updated mediaInfoRecords if it can
	"""
	theMovieDatabaseInterface = TheMovieDatabaseInterface.getInstance()

	for mediaInfoRecord in mediaInfoRecords:
		if mediaInfoRecord.getShowName() == queryMediaInfoRecord.getShowName():
			maxNumberOfEpisodes = theMovieDatabaseInterface.getShowEpisodeCount(mediaInfoRecord.getShowName(), mediaInfoRecord.getLatestSeasonNumber())
			prevEpisodeValue = mediaInfoRecord.getLatestEpisodeNumber()
			prevSeasonValue = mediaInfoRecord.getLatestSeasonNumber()

			if maxNumberOfEpisodes and (mediaInfoRecord.getLatestEpisodeNumber() + 1) > maxNumberOfEpisodes:
				# set data to next season first episode
				mediaInfoRecord.setLatestSeasonNumber(
					queryMediaInfoRecord.getLatestSeasonNumber() + 1)
				mediaInfoRecord.setLatestEpisodeNumber(1)

				currentLatestEpisodeValue = mediaInfoRecord.getLatestEpisodeNumber()
				currentLatestSeasonValue = mediaInfoRecord.getLatestSeasonNumber()
				logging.info(f"Updated latest episode number from {prevEpisodeValue} to {currentLatestEpisodeValue}")
				logging.info(f"Updated latest season number from {prevSeasonValue} to {currentLatestSeasonValue}")
			else:
				mediaInfoRecord.setLatestEpisodeNumber(mediaInfoRecord.getLatestEpisodeNumber() + 1)

				currentLatestEpisodeValue = mediaInfoRecord.getLatestEpisodeNumber()
				logging.info(f"Updated latest episode number from {prevEpisodeValue} to {currentLatestEpisodeValue}")

			return mediaInfoRecords
	return None


def writeMediaFile(queryMediaInfoRecord):
	"""
	writeMediaFile opens the MediaIndex.json file and loads the content into a list of MediaInfoRecord objects it then increments the episode/season number for the record provided in queryMediaInfoRecord
	:testedWith: None IO/glue code which does not require testing
	:param queryMediaInfoRecord: the mediaInfoRecord that requires updating
	:return: the success/failure of the operation
	"""
	mediaInfoRecords = loadMediaFile()

	updatedMediaInfoRecords = incrementEpisode(
	    mediaInfoRecords, queryMediaInfoRecord)

	if not updatedMediaInfoRecords:
		return False

	updatedMediaInfoRecordsAsDict = [ mediaInfoRecord.toDict() for mediaInfoRecord in mediaInfoRecords ]

	media = { "media": updatedMediaInfoRecordsAsDict }

	if writeFile:
		with open(os.getenv("MEDIA_FILE"), "w") as mediaFileTarget:
			json.dump(media, mediaFileTarget)

	return True
    

def loadMediaFile():
	"""
	loadMediaFile opens the MediaIndex.json file and loads the content into a list of MediaInfoRecord objects
	:testedWith: None IO/glue code which does not require testing
	:return: a list of MediaInfoRecord's loaded from the MediaIndex.json
	"""
	mediaIndexFileLocation = os.getenv("MEDIA_FILE")
	logging.info(f"MediaIndex File: {mediaIndexFileLocation}")
	with open(mediaIndexFileLocation, "r") as mediaIndexfile:

		mediaInfoRecords = []
		mediaInfoRecordsRaw = json.loads(mediaIndexfile.read())["media"]
		for mediaInfoRecordRaw in mediaInfoRecordsRaw:

			blacklistTerms = mediaInfoRecordRaw["blacklistTerms"] if "blacklistTerms" in mediaInfoRecordRaw.keys() else []

			mediaInfoRecords.append(MediaInfoRecord(mediaInfoRecordRaw["name"], 
				mediaInfoRecordRaw["typeSpecificData"]["latestSeason"], 
				mediaInfoRecordRaw["typeSpecificData"]["latestEpisode"],
				blacklistTerms))
		
		return mediaInfoRecords
