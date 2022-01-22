#!/venv/bin/python

# external dependencies
import json
import os
import subprocess

# internal dependencies
from server.interfaces.MediaIndexFileInterface import removeRecordFromMediaInfoFile, updateRecordInMediaInfoFile, writeNewRecordToMediaInfoFile
from server.interfaces.TheMovieDatabaseInterface import TheMovieDatabaseInterface


def serveMediaInfo():
    f = open(os.getenv("MEDIA_INDEX_FILE_LOCATION"), "r")
    theMovieDatabaseInterface = TheMovieDatabaseInterface()
    mediaIndexFileContentWithReccomendations = theMovieDatabaseInterface.addShowReccomendationsToMediaIndexContent(f.read())
    return mediaIndexFileContentWithReccomendations


def submitMediaInfoRecord(data):

    # extract data
    mediaName = data['mediaName']
    latestSeason = int(data['latestSeason'])
    latestEpisode = int(data['latestEpisode'])
    blacklistTerms = data['blacklistTerms']

    blacklistTerms = [ term.replace(" ", "") for term in blacklistTerms.split(",") if len(term) > 0]

    success = writeNewRecordToMediaInfoFile(mediaName, latestSeason, latestEpisode, blacklistTerms)

    return success


def deleteMediaInfoRecord(recordIndex):
    return removeRecordFromMediaInfoFile(recordIndex)


def updateMediaInfoRecord(newMediaIndexRecord, recordIndex):
    newMediaIndexRecord = json.loads(newMediaIndexRecord)

    return updateRecordInMediaInfoFile(newMediaIndexRecord, recordIndex)


def runMediaGrab():
    mediaGrabDir = os.getenv("MEDIA_GRAB_DIRECTORY")

    subprocess.check_call(['python3', 'Main.py'], cwd=mediaGrabDir)

    return True
