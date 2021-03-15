#!/venv/bin/python

# external dependencies
import json
import os
import logging

# internal dependencies
from dataTypes.ProgramModeMap import PROGRAM_MODE_MAP
from dataTypes.ProgramMode import PROGRAM_MODE
from controllers import ErrorController


def notifyDownloadStarted(mediaName, mediaType):

    dipFileLocation = os.getenv("DOWNLOADS_IN_PROGRESS_FILE")
    
    if not os.path.exists(dipFileLocation):
        createDownloadsInProgressFile(dipFileLocation)

    typeKey = PROGRAM_MODE_MAP[mediaType]

    def operation(media, mediaName=mediaName, typeKey=typeKey):
        if mediaName in media[typeKey]:
            ErrorController.reportError(f"Failed to add {mediaName} to {typeKey} list in data/DownloadsInProgress.json {media[typeKey]} because the list already contains this value.")
            return media

        logging.info(f"Adding {mediaName} to {typeKey} list in data/DownloadsInProgress.json {media[typeKey]}")
        media[typeKey].append(mediaName)
        return media

    updateFile(operation)


def createDownloadsInProgressFile(fileLocation):
    initialFileDict = {
        "tv_seasons": [],
        "tv_episodes": []
    }
    
    initialFileContent = json.dumps(initialFileDict, sort_keys=False)
    
    with open(fileLocation, 'x') as dipFile:
        dipFile.write(initialFileContent)


def notifyDownloadFinished(mediaName, mediaType):
    
    dipFileLocation = os.getenv("DOWNLOADS_IN_PROGRESS_FILE")
    
    if not os.path.exists(dipFileLocation):
        return

    typeKey = PROGRAM_MODE_MAP[mediaType]

    def operation(media, mediaName=mediaName, typeKey=typeKey):
        if mediaName not in media[typeKey]:
            ErrorController.reportError(f"Failed to remove {mediaName} from {typeKey} list in data/DownloadsInProgress.json {media[typeKey]} because the list does not contain this value.")
            return media
        logging.info(f"Removing {mediaName} from {typeKey} list in data/DownloadsInProgress.json {media[typeKey]}")
        media[typeKey].remove(mediaName)
        return media

    updateFile(operation)


def updateFile(operation):
    dipFileLocation = os.getenv("DOWNLOADS_IN_PROGRESS_FILE")
    
    with open(dipFileLocation, 'r+') as dipFile:
        #load file contents to dict
        fileContent = dipFile.read()
        media = json.loads(fileContent)

        #add new data to dict
        operation(media)

        #write new contents of file
        dipFile.seek(0)
        dipFile.write(json.dumps(media))
        dipFile.truncate()


def getDownloadingItems(mode):
    dipFileLocation = os.getenv("DOWNLOADS_IN_PROGRESS_FILE")
    
    logging.info(f"DownloadsInProgress File: {dipFileLocation}")
    with open(dipFileLocation, 'r') as dipFile:
        #load file contents to dict
        fileContent = dipFile.read()
        media = json.loads(fileContent)
        return media[PROGRAM_MODE_MAP[mode]]


def findNewDownload(downloadIds):

    downloadingItems = getDownloadingItems(PROGRAM_MODE.TV_EPISODES)

    for downloadId in downloadIds:
        if downloadId not in downloadingItems:
            return downloadId

    return None
