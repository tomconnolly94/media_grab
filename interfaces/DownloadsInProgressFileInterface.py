#!/venv/bin/python

#external dependencies
import json
import os

def notifyDownloadStarted(mediaType, mediaName):

    file = os.getenv("DOWNLOADS_IN_PROGRESS_FILE")

    if not os.path.exists(file):
        createDownloadsInProgressFile(file)

    with open(file, 'rw') as dipFile:
        media = json.loads(dipFile.read())
        media[mediaType].append(mediaName)



def createDownloadsInProgressFile(fileLocation):
    initialFileDict = {
        "tv_seasons": [],
        "tv_episodes": [],
        "movies": []
    }
    
    initialFileContent = json.dumps(initialFileDict, sort_keys=False)

    file = open(fileLocation, "x")
    file.write(initialFileContent)

def notifyDownloadFinished():
    pass