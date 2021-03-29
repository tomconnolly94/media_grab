#!/venv/bin/python

# external dependencies
import os
import json
from interfaces import TheMovieDatabaseInterface
import logging

# internal dependencies
from dataTypes.MediaInfoRecord import MediaInfoRecord

writeFile = True


def incrementEpisode(mediaInfoRecords, queryRecord):

	theMovieDatabaseInterface = TheMovieDatabaseInterface.getInstance()

	for mediaInfoRecord in mediaInfoRecords:
		if mediaInfoRecord.getShowName() == queryRecord.getShowName():
			maxNumberOfEpisodes = theMovieDatabaseInterface.getShowEpisodeCount(mediaInfoRecord.getShowName(), mediaInfoRecord.getLatestSeasonNumber())
			prevEpisodeValue = mediaInfoRecord.getLatestEpisodeNumber()
			prevSeasonValue = mediaInfoRecord.getLatestSeasonNumber()

			if maxNumberOfEpisodes and (mediaInfoRecord.getLatestEpisodeNumber() + 1) > maxNumberOfEpisodes:
				# set data to next season first episode
				mediaInfoRecord.setLatestSeasonNumber(queryRecord.getLatestSeasonNumber() + 1)
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


def writeMediaFile(queryRecord):
	
	mediaInfoRecords = loadMediaFile()
	
	updatedMediaInfoRecords = incrementEpisode(mediaInfoRecords, queryRecord)

	if not updatedMediaInfoRecords:
		return

	updatedMediaInfoRecordsAsDict = [ mediaInfoRecord.toDict() for mediaInfoRecord in mediaInfoRecords ]

	media = { "media": updatedMediaInfoRecordsAsDict }

	if writeFile:
		with open(os.getenv("MEDIA_FILE"), "w") as mediaFileTarget:
			json.dump(media, mediaFileTarget)

	return
    

def loadMediaFile():
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
