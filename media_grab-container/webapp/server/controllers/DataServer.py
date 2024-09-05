#!/venv/bin/python

# external dependencies
import json
import os, sys
from os.path import dirname
import subprocess
import logging

rootDir = dirname(dirname(dirname(dirname(os.path.realpath(__file__)))))
sys.path.append(rootDir) # make root directory accessible

# internal dependencies
from server.interfaces.MediaIndexFileInterface import removeRecordFromMediaInfoFile, updateRecordInMediaInfoFile, writeNewRecordToMediaInfoFile
from server.interfaces import TheMovieDatabaseInterface
from src.interfaces.TPBInterface import queryAPI

def serveMediaInfo():
    file = open(os.getenv("MEDIA_INDEX_FILE_LOCATION"), "r")
    mediaIndexFile = json.loads(file.read())
    return mediaIndexFile


def submitMediaInfoRecord(data):

    logging.info(f"submitMediaInfoRecord input received: {data}")

    # extract data
    mediaName = data['mediaName']
    latestSeason = int(data['latestSeason'])
    latestEpisode = int(data['latestEpisode'])
    blacklistTerms = data['blacklistTerms']
    
    # very basic validation
    if not mediaName or not latestSeason or not latestEpisode:

        logging.error(f"submitMediaInfoRecord input is malformed. mediaName='{mediaName}' "
                     f"latestSeason={latestSeason} latestEpisode={latestEpisode} "
                     f"blacklistTerms='{blacklistTerms}'")
        return False

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

    subprocess.check_call(['python3', './Main.py'], cwd=mediaGrabDir)

    return True


def getSimilarShows(showTitle):
    return TheMovieDatabaseInterface.getInstance().getSimilarShowTitles(showTitle)


def getTorrentTitleList(searchTerm: str):
    # make req to torrent client
    torrentTitles = [ title.getName() for title in queryAPI(searchTerm) ]
    return torrentTitles
