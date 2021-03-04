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


def getLargestFileInDir(directory):
    filesInDir = list(os.scandir(directory))
    filesInDir = sorted(filesInDir, key=lambda file: -1 * int(os.path.getsize(f"{directory}/{file.name}")))
    return filesInDir[0]

    
def auditFiles(completedDownloadFiles, filteredDownloadingItems, targetDir):
    # deal with files
    for completedDownloadFile in completedDownloadFiles:
        completedDownloadFileName = completedDownloadFile.name

        if completedDownloadFileName in filteredDownloadingItems:
            # extract show name
            showName = extractShowName(completedDownloadFileName).capitalize()
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
                existingFile = os.path.join(os.getenv('DUMP_COMPLETE_DIR'), completedDownloadFileName)
                os.rename(existingFile, prospectiveFile)
                DownloadsInProgressFileInterface.notifyDownloadFinished(completedDownloadFileName, PROGRAM_MODE_MAP[PROGRAM_MODE.TV_EPISODES])
                logging.info(f"Moved '{existingFile}' to '{prospectiveFile}'")

            else:
                # report problem
                reportItemAlreadyExists(prospectiveFile, completedDownloadFileName)


def auditDirectories(completedDownloadDirectories, filteredDownloadingItems, targetDir):

    dumpCompleteDir = os.getenv("DUMP_COMPLETE_DIR")

    # deal with directories
    for completedDownloadDirectory in completedDownloadDirectories:
        completedDownloadDirectoryName = completedDownloadDirectory.name

        if completedDownloadDirectoryName in filteredDownloadingItems:
            # extract show name
            showName = extractShowName(completedDownloadDirectoryName).capitalize()
            tvShowDir = os.path.join(targetDir, showName)
            episodeFile = ""

            # create tv show directory if it does not exist
            if not FolderInterface.directoryExists(tvShowDir):
                FolderInterface.createDirectory(tvShowDir)
            
            seasonNumber = extractSeasonNumber(completedDownloadDirectoryName)
            episodeNumber = extractEpisodeNumber(completedDownloadDirectoryName)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

            # if an episode number was extracted from the directory name we can safely assume that we have 
            # an episode file inside (probably the largest file)
            if episodeNumber:
                episodeFile = getLargestFileInDir(os.path.join(dumpCompleteDir, completedDownloadDirectoryName))
            else:
                # TODO: eventually we should deal with the download of a full season directoy, unnecessary at this point, for now we can assume that if no episode can be found
                return None

            extension = extractExtension(episodeFile)

            # create season directory if it does not exist
            if not FolderInterface.directoryExists(seasonDir):
                FolderInterface.createDirectory(seasonDir)

            prospectiveFile = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")
                        
            if not FolderInterface.fileExists(prospectiveFile):
                # move file to season directory
                originalFileLocation = os.path.join(dumpCompleteDir, completedDownloadDirectoryName, episodeFile.name)
                os.rename(originalFileLocation, prospectiveFile)
            else:
                # report problem
                reportItemAlreadyExists(prospectiveFile, completedDownloadDirectoryName)


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
    auditDirectories(completedDownloadDirectories, filteredDownloadingItems, targetDir)
