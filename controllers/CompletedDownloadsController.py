#!/venv/bin/python

# external dependencies
import os
import logging
import re

# internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP
from interfaces import FolderInterface, MailInterface

# access env variables
dumpCompleteDirPath = os.getenv("DUMP_COMPLETE_DIR")

def extractShowName(fileName):
    
    showNameMatch = re.match(r"(.*?)(?:season|s|episode|e).*\d*", fileName) # extract show name using regex capturing group
    showName = showNameMatch.groups()[0]
    showName = re.sub(r"[^\w\s]", "", showName) # replace all punctuation
    showName = showName.strip()
    showName = " ".join(showName.split()) # remove any double spaces
    return showName


def extractSeasonNumber(fileName):
    return re.match(r".*?(?:season|s)+?[ -_.,!\"'/$]*?(\d+)", fileName).groups[0]


def extractEpisodeNumber(fileName):
    return re.match(r".*?(?:episode|e)+?[ -_.,!\"'/$]*?(\d+)", fileName).groups[0]


def createDirectory(newDirectoryName):
    os.mkdir(newDirectoryName)
    # log action
    logging.info(f"Created directory: {newDirectoryName}")


def reportItemAlreadyExists(newItemLocation, torrentName):
    errorString = f"Downloaded torrent: {torrentName} and attempted to move it to {newItemLocation} but this target already exists."
    logging.error(errorString)
    MailInterface.sendMail("Houston we have a problem", errorString)

    
def auditFiles(completedDownloadFiles, filteredDownloadingItems, targetDir):
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
            episodeNumber = extractEpisodeNumber(completedDownloadFile)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

            # create season directory if it does not exist
            if not FolderInterface.directoryExists(seasonDir):
                createDirectory(seasonDir)

            prospectiveFile = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}")
            
            if not FolderInterface.fileExists(prospectiveFile):
               #move file to season directory
                os.rename(f"{dumpCompleteDirPath}/{completedDownloadFile}", prospectiveFile)
            else:
                # report problem
                reportItemAlreadyExists(prospectiveFile, completedDownloadFile)


def auditDirectories(completedDownloadDirectories, filteredDownloadingItems, targetDir):
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
                os.rename(f"{dumpCompleteDirPath}/{completedDownloadDirectory}", seasonDir)
            else:
                # report problem
                reportItemAlreadyExists(seasonDir, completedDownloadDirectory)


def auditFolder(mode, filteredDownloadingItems):
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
    #   directories:
    #       * ascertain how many relevant media files are present in the directory, 
    #           * if only one, treat this file as above, move all other files and the directory itself 
    #               to the recycle directory
    #           * if there are multiple files, assume this directory is a full season and deposit the 
    #               full directory inside the directory that shares the same name as this show (found 
    #               in the DownloadsInProgress file), any non media file should be moved to the recycle 
    #               directory
    #       * logs are required for everything, what is moved where and the reason for that decision, 
    #               this will help with traceability of errors later


    # TODO: these functions are incredibly similar, find a way to aggregate the duplicate code
    auditFiles(completedDownloadFiles, filteredDownloadingItems, targetDir)
    auditDirectories(completedDownloadDirectories, filteredDownloadingItems, targetDir)
    



