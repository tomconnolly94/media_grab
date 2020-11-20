#!/venv/bin/python

#external dependencies
import json
import os

file = os.getenv("DOWNLOADS_IN_PROGRESS_FILE")

def notifyDownloadStarted(mediaType, mediaName):

    if not os.path.exists(file):
        createDownloadsInProgressFile(file)

    def operation(media, mediaName=mediaName, mediaType=mediaType):
        media[mediaType].append(mediaName)
        return media

    updateFile(operation)


def createDownloadsInProgressFile(fileLocation):
    initialFileDict = {
        "tv_seasons": [],
        "tv_episodes": [],
        "movies": []
    }
    
    initialFileContent = json.dumps(initialFileDict, sort_keys=False)

    file = open(fileLocation, "x")
    file.write(initialFileContent)


def notifyDownloadFinished(mediaType, mediaName):
    
    if not os.path.exists(file):
        return

    def operation(media, mediaName=mediaName, mediaType=mediaType):
        media[mediaType].remove(mediaName)
        return media

    updateFile(operation)


def updateFile(operation):
    with open(file, 'r+') as dipFile:
        #load file contents to dict
        fileContent = dipFile.read()
        media = json.loads(fileContent)

        #add new data to dict
        operation(media)

        #write new contents of file
        dipFile.seek(0)
        dipFile.write(media)