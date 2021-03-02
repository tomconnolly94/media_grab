#!/venv/bin/python

# external dependencies
import os
import logging
import re

# internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP, PROGRAM_MODE_MAP
from data_types.ProgramMode import PROGRAM_MODE
from interfaces import FolderInterface, MailInterface, DownloadsInProgressFileInterface

def extractShowName(fileName):
    
    try:
        showNameMatch = re.match(r"(.+?)(?:[^a-zA-Z]*(?:season|s|episode|e)+.\d+.*)*?\s*$", fileName, re.IGNORECASE) # extract show name using regex capturing group
        showName = showNameMatch.groups()[0]
        showName = re.sub(r"[^\w\s]", " ", showName) # replace all punctuation
        showName = showName.strip() # remove whitespace on left or right
        showName = " ".join(showName.split()) # remove any double spaces
        showName = showName.lower() # convert uppercase letters to lowercase
        if showName:
            return showName
        else:
            return None
    except:
        return None


def extractSeasonNumber(fileName):
    try:
        seasonNumber = re.match(r".*?(?:season|s)+?[ -_.,!\"'/$]*?(\d+)", fileName, re.IGNORECASE)
        seasonNumber = int(seasonNumber.groups()[0])
        if seasonNumber:
            return seasonNumber
        else:
            return None
    except:
        return None


def extractEpisodeNumber(fileName):
    try:
        episodeNumber = re.match(r".*?(?:episode|e)+?[ -_.,!\"'/$]?(\d+)", fileName, re.IGNORECASE)
        episodeNumber = int(episodeNumber.groups()[0])
        if episodeNumber:
            return episodeNumber
        else:
            return None
    except:
        return None


def extractExtension(fileName):
    return os.path.splitext(fileName)[1]


def reportItemAlreadyExists(newItemLocation, torrentName):
    errorString = f"Downloaded torrent: {torrentName} and attempted to move it to {newItemLocation} but this target already exists."
    logging.error(errorString)
    MailInterface.sendMail("Houston we have a problem", errorString)

    
def auditFiles(completedDownloadFiles, filteredDownloadingItems, targetDir):
    # deal with files
    for completedDownloadFile in completedDownloadFiles:
        completedDownloadFileName = completedDownloadFile.name

        if completedDownloadFileName in filteredDownloadingItems:
            # extract show name
            showName = extractShowName(completedDownloadFileName)
            tvShowDir = os.path.join(targetDir, showName)

            # create tv show directory if it does not exist
            if not FolderInterface.directoryExists(tvShowDir):
                FolderInterface.createDirectory(tvShowDir)

            seasonNumber = extractSeasonNumber(completedDownloadFileName)
            episodeNumber = extractEpisodeNumber(completedDownloadFileName)
            extension = extractExtension(completedDownloadFileName)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

            # create season directory if it does not exist
            if not FolderInterface.directoryExists(seasonDir):
                FolderInterface.createDirectory(seasonDir)

            prospectiveFile = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")
            
            if not FolderInterface.fileExists(prospectiveFile):
                # move file to season directory
                existingFile = f"{os.getenv('DUMP_COMPLETE_DIR')}{completedDownloadFileName}"
                os.rename(existingFile, prospectiveFile)
                DownloadsInProgressFileInterface.notifyDownloadFinished(completedDownloadFileName, PROGRAM_MODE_MAP[PROGRAM_MODE.TV_EPISODES])
                logging.info(f"Moved '{existingFile}' to '{prospectiveFile}'")

            else:
                # report problem
                reportItemAlreadyExists(prospectiveFile, completedDownloadFileName)


def auditDirectories(completedDownloadDirectories, filteredDownloadingItems, targetDir):
    # deal with directories
    for completedDownloadDirectory in completedDownloadDirectories:
        if completedDownloadDirectory in filteredDownloadingItems:
            # extract show name
            showName = extractShowName(completedDownloadDirectory)
            tvShowDir = os.path.join(targetDir, showName)

            # create tv show directory if it does not exist
            if not FolderInterface.directoryExists(tvShowDir):
                FolderInterface.createDirectory(tvShowDir)

            seasonNumber = extractSeasonNumber(completedDownloadDirectory)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")
            
            if not FolderInterface.directoryExists(seasonDir):
                # move file to season directory
                dump_complete_dir = os.getenv("DUMP_COMPLETE_DIR")
                os.rename(f"{dump_complete_dir}/{completedDownloadDirectory}", seasonDir)
            else:
                # report problem
                reportItemAlreadyExists(seasonDir, completedDownloadDirectory)


def auditDumpCompleteDir(mode, filteredDownloadingItems):

    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
    itemsFromDirectory = FolderInterface.getDirContents(os.getenv("DUMP_COMPLETE_DIR"))

    completedDownloadFiles = []
    completedDownloadDirectories = []

    for item in itemsFromDirectory:
        if item.is_file():
            completedDownloadFiles.append(item)
        else:
            completedDownloadDirectories.append(item)


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
    logging.info("filteredDownloadingItems:")
    logging.info(filteredDownloadingItems)
    auditFiles(completedDownloadFiles, filteredDownloadingItems, targetDir)
    # auditDirectories(completedDownloadDirectories, filteredDownloadingItems["tv-seasons"], targetDir)
