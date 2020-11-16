#!/venv/bin/python

# external dependencies
import os
import json

writeFile = None


def updateMedia(mediaInfoRecords, queryRecord, updateableField):

	for mediaRecord in mediaInfoRecords:
		if mediaRecord["name"] == queryRecord["name"]:
			mediaRecord["typeSpecificData"][updateableField] = queryRecord["typeSpecificData"][updateableField]
			return mediaInfoRecords
	return None


def writeMediaFile(queryRecord, updateableField):
	
	with open(os.getenv("MEDIA_FILE"), 'r') as mediaFileSrc:
		media = json.load(mediaFileSrc)["media"]

	updatedMedia = updateMedia(media, queryRecord, updateableField)

	if not updatedMedia:
		return

	media = { "media": updatedMedia }

	if writeFile:
		with open(os.getenv("MEDIA_FILE"), "w") as mediaFileTarget:
			json.dump(media, mediaFileTarget)

	return
    

def loadMediaFile():
	with open(os.getenv("MEDIA_FILE"), "r") as mediaIndexfile:
		return json.loads(mediaIndexfile.read())["media"]
