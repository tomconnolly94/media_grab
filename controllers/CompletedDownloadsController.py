#!/venv/bin/python

# external dependencies
import os
import logging
import re

#internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP
from interfaces import FolderInterface, MailInterface

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


def reportItemAlreadyExists(item):
    errorString = f"Downloaded item {item} already exists."
    logging.error(errorString)
    MailInterface.sendMail("Houston we have a problem", errorString)


def auditFolder(mode, filteredDownloadingItems):
    # access env variables
    dumpCompleteDirPath = os.getenv("DUMP_COMPLETE_DIR")
    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])

    itemsFromDirectory = FolderInterface.getDirContents(dumpCompleteDirPath)
    completedDownloadFiles = [ item for item in itemsFromDirectory if FolderInterface.fileExists(item) ]
    completedDownloadDirectories = [ item for item in itemsFromDirectory if FolderInterface.directoryExists(item) ]


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
            if not FolderInterface.directoryExists(tvShowDir):
                createDirectory(tvShowDir)

            seasonNumber = extractSeasonNumber(completedDownloadFile)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

            # create season directory if it does not exist
            if not FolderInterface.directoryExists(seasonDir):
                createDirectory(seasonDir)
            
            if not FolderInterface.fileExists(seasonDir):
               #move file to season directory
                os.rename(f"{dumpCompleteDirPath}{completedDownloadFile}", f"{seasonDir}{completedDownloadFile}")
            else:
                # report problem
                reportItemAlreadyExists(f"{seasonDir}{completedDownloadFile}")


    # deal with directories
    for completedDownloadDirectory in completedDownloadDirectories:
        if completedDownloadDirectory in filteredDownloadingItems:
            # extract show name
            showName = extractShowName(completedDownloadDirectory)
            tvShowDir = os.path.join(targetDir, showName)

            # create tv show directory if it does not exist
            if not FolderInterface.directoryExists(tvShowDir):
                createDirectory(tvShowDir)

            seasonNumber = extractSeasonNumber(completedDownloadDirectory)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

            if not FolderInterface.directoryExists(seasonDir):
                # move file to season directory
                os.rename(f"{dumpCompleteDirPath}{completedDownloadDirectory}", f"{seasonDir}{completedDownloadDirectory}")
            else:
                # report problem
                reportItemAlreadyExists(f"{seasonDir}{completedDownloadDirectory}")
