#!/venv/bin/python

# external dependencies
import os
import logging
import re
import shutil

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


def auditFileSystemItemsForEpisodes(mode, filteredDownloadingItems):
    
    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
    dumpCompleteDir = os.getenv("DUMP_COMPLETE_DIR")
    fileSystemItemsFromDirectory = FolderInterface.getDirContents(dumpCompleteDir)

    # deal with directories
    for fileSystemItem in fileSystemItemsFromDirectory:
        fileSystemItemName = fileSystemItem.name

        if fileSystemItemName in filteredDownloadingItems:
            # extract show name
            showName = extractShowName(fileSystemItemName).capitalize()
            tvShowDir = os.path.join(targetDir, showName)
            targetFile = fileSystemItem
            itemIsDirectory = FolderInterface.directoryExists(fileSystemItem.path)

            # create tv show directory if it does not exist
            if not FolderInterface.directoryExists(tvShowDir):
                FolderInterface.createDirectory(tvShowDir)
            
            seasonNumber = extractSeasonNumber(fileSystemItemName)
            episodeNumber = extractEpisodeNumber(fileSystemItemName)
            seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

            if itemIsDirectory:
                # if an episode number was extracted from the directory name we can safely assume that we have 
                # an episode file inside (probably the largest file)
                if episodeNumber:
                    targetFile = getLargestFileInDir(fileSystemItem.path)
                else:
                    # TODO: eventually we should deal with the download of a full season directoy, unnecessary at this point, for now we can assume that if no episode can be found
                    return None

            extension = extractExtension(targetFile.name)

            # create season directory if it does not exist
            if not FolderInterface.directoryExists(seasonDir):
                FolderInterface.createDirectory(seasonDir)

            prospectiveFile = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")
                        
            if not FolderInterface.fileExists(prospectiveFile):
                # move file to appropriate directory
                os.rename(targetFile.path, prospectiveFile)
                logging.info(f"Moved '{targetFile.path}' to '{prospectiveFile}'")
                DownloadsInProgressFileInterface.notifyDownloadFinished(fileSystemItemName, PROGRAM_MODE.TV_EPISODES)

                if itemIsDirectory:
                    # attempt to move the rest of the files to the recycle_bin folder so if the program made an error, it is recoverable
                    try:
                        shutil.move(fileSystemItem.path, os.getenv("RECYCLE_BIN_DIR"))
                    except OSError:
                        logging.error("Exception occurred", exc_info=True)

            else:
                # report problem
                reportItemAlreadyExists(prospectiveFile, fileSystemItemName)


def auditDumpCompleteDir(mode, filteredDownloadingItems):
    # look for episodes
    auditFileSystemItemsForEpisodes(mode, filteredDownloadingItems)
