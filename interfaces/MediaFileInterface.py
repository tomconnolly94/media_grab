#!/venv/bin/python

# external dependencies
import os
import json


def writeMediaFile(queryRecord, updateableField):
	
	with open(os.getenv("MEDIA_FILE"), 'r') as mediaFileSrc:
		media = json.load(mediaFileSrc)["media"]

	for mediaRecord in media:
		if mediaRecord["name"] == queryRecord["name"]:
			mediaRecord["typeSpecificData"][updateableField] = queryRecord["typeSpecificData"][updateableField]

	media = { "media": media }

	with open(os.getenv("MEDIA_FILE"), "w") as mediaFileTarget:
		json.dump(media, mediaFileTarget)

	return
    

def loadMediaFile():
	with open(os.getenv("MEDIA_FILE"), "r") as mediaIndexfile:
		return json.loads(mediaIndexfile.read())["media"]
