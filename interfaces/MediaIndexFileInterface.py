#!/venv/bin/python

# external dependencies
import os
import json
from interfaces import TheMovieDatabaseInterface
import logging


writeFile = True


def incrementEpisode(mediaInfoRecords, queryRecord):

	for mediaRecord in mediaInfoRecords:
		if mediaRecord["name"] == queryRecord["name"]:
			maxNumberOfEpisodes = TheMovieDatabaseInterface.getShowEpisodeCount(mediaRecord["name"], mediaRecord["typeSpecificData"]["latestSeason"])
			prevEpisodeValue = mediaRecord["typeSpecificData"]["latestEpisode"]
			prevSeasonValue = mediaRecord["typeSpecificData"]["latestSeason"]


			if int(mediaRecord["typeSpecificData"]["latestEpisode"]) + 1 > maxNumberOfEpisodes:
				# set data to next season first episode
				mediaRecord["typeSpecificData"]["latestSeason"] = str(int(queryRecord["typeSpecificData"]["latestSeason"]) + 1)
				mediaRecord["typeSpecificData"]["latestEpisode"] = str(1)

				currentLatestEpisodeValue = mediaRecord["typeSpecificData"]["latestEpisode"]
				currentLatestSeasonValue = mediaRecord["typeSpecificData"]["latestSeason"]
				logging.info(f"Updated latest episode from {prevEpisodeValue} to {currentLatestEpisodeValue}")
				logging.info(f"Updated latest season from {prevSeasonValue} to {currentLatestSeasonValue}")
			else:
				mediaRecord["typeSpecificData"]["latestEpisode"] = str(int(mediaRecord["typeSpecificData"]["latestEpisode"]) + 1)

				currentLatestEpisodeValue = mediaRecord["typeSpecificData"]["latestEpisode"]
				logging.info(f"Updated latest episode from {prevEpisodeValue} to {currentLatestEpisodeValue}")

			return mediaInfoRecords
	return None


def writeMediaFile(queryRecord, updateableField):
	
	with open(os.getenv("MEDIA_FILE"), 'r') as mediaFileSrc:
		media = json.load(mediaFileSrc)["media"]
	

	updatedMedia = incrementEpisode(media, queryRecord)

	if not updatedMedia:
		return

	media = { "media": updatedMedia }

	if writeFile:
		with open(os.getenv("MEDIA_FILE"), "w") as mediaFileTarget:
			json.dump(media, mediaFileTarget)

	return
    

def loadMediaFile():
	mediaIndexFileLocation = os.getenv("MEDIA_FILE")
	logging.info(f"MediaIndex File: {mediaIndexFileLocation}")
	with open(mediaIndexFileLocation, "r") as mediaIndexfile:
		return json.loads(mediaIndexfile.read())["media"]
