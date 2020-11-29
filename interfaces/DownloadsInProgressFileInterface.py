#!/venv/bin/python

# external dependencies
import json
import os

# internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_MAP

file = os.getenv("DOWNLOADS_IN_PROGRESS_FILE")

def notifyDownloadStarted(mediaName, mediaType):

    if not os.path.exists(file):
        createDownloadsInProgressFile(file)

    def operation(media, mediaName=mediaName, mediaType=mediaType):
        media[mediaType].append(mediaName)
        return media

    updateFile(operation)


def createDownloadsInProgressFile(fileLocation):
    initialFileDict = {
        "tv_seasons": [],
        "tv_episodes": []
    }
    
    initialFileContent = json.dumps(initialFileDict, sort_keys=False)

    file = open(fileLocation, "x")
    file.write(initialFileContent)


def notifyDownloadFinished(mediaName, mediaType):
    
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


def getDownloadingItems(mode):
    with open(file, 'r') as dipFile:
        #load file contents to dict
        fileContent = dipFile.read()
        media = json.loads(fileContent)
        return media[PROGRAM_MODE_MAP[mode]]