#!/venv/bin/python

# external dependencies
import os
import logging
import re

#internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP

def extractShowName(fileName):
    
    showName = re.match(r"(.*?)(?:season|s|episode|e).*\d*", fileName).groups[0] # extract show name using regex capturing group
    showName = re.sub(r"[^\w\s]", "", showName).strip() # replace all punctuation
    showName = " ".join(showName.split()) # remove any double spaces
    return showName


def extractSeasonNumber(fileName):
    return re.match(r".*?(?:season|s)+?[ -_.,!\"'/$]*?(\d+)", fileName).groups[0]


def createDirectory(newDirectoryName):
    os.mkdir(newDirectoryName)
    # log action
    logging.info(f"Created directory: {newDirectoryName}")


def auditFolder(mode, filteredDownloadingItems):
    dumpCompleteDirPath = os.getenv("DUMP_COMPLETE_DIR")
    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])

    directoryItems = os.scandir(dumpCompleteDirPath)
    completedDownloadFiles = [ directoryItem for directoryItem in directoryItems if os.path.isfile(directoryItem) ]
    completedDownloadDirectories = [ directoryItem for directoryItem in directoryItems if os.path.isdir(directoryItem) ]


    # Rules:
    #
    # TV episodes:
    #   files: 
    #       * ascertain whether Season directory for this show already exists from the show name found 
    #           in the DownloadsInProgress file
    #       * find the correct season using aregex on the torrent name S0X
    #   directory:
    #       * ascertain how many relevant media files are present in the directory, 
    #           * if only one, treat this file as above, move all other files and the directory itself 
    #               to the recycle directory
    #           * if there are multiple files, assume this directory is a full season and deposit the 
    #               full directory inside the directory that shares the same name as this show (found 
    #               in the DownloadsInProgress file), any non media file should be moved to the recycle 
    #               directory
    #       * logs are required for everything, what is moved where and the reason for that decision, 
    #               this will help with traceability of errors later

    
    # deal with files
    for completedDownloadFile in completedDownloadFiles:
        if completedDownloadFile in filteredDownloadingItems:
            # extract show name
            showName = extractShowName(completedDownloadFile)
            tvShowDir = os.path.join(targetDir, showName)

            # create tv show directory if it does not exist
            if not os.path.isdir(tvShowDir):
                createDirectory(tvShowDir)

            seasonNumber = extractSeasonNumber(completedDownloadFile)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

            # create season directory if it does not exist
            if not os.path.isdir(seasonDir):
                createDirectory(seasonDir)

            #move file to season directory
            os.rename(f"{dumpCompleteDirPath}{completedDownloadFile}", f"{seasonDir}{completedDownloadFile}")


    # deal with directories