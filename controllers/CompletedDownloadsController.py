#!/venv/bin/python

# external dependencies
import os
import logging
import re
import shutil

# internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP, PROGRAM_MODE_MAP
from data_types.ProgramMode import PROGRAM_MODE
from interfaces import FolderInterface, MailInterface, DownloadsInProgressFileInterface, QBittorrentInterface
from controllers import ErrorController


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
        regexRaw = r"(?:S|Season)(\d{1,2})"        
        matches = re.search(regexRaw, fileName, re.IGNORECASE | re.MULTILINE)        
        seasonNumber = int(matches.groups()[0])
        
        if seasonNumber:
            return seasonNumber
        else:
            return None
    except Exception as exception:
        ErrorController.reportError("Exception occurred when extracting season number with regex", exception=exception, sendEmail=True)
        return None


def extractEpisodeNumber(fileName):
    try:
        regexRaw = r"(?:E|Episode)(\d{1,2})"        
        matches = re.search(regexRaw, fileName, re.IGNORECASE | re.MULTILINE)        
        episodeNumber = int(matches.groups()[0])        

        if episodeNumber:
            return episodeNumber
        else:
            return None
    except Exception as exception:
        ErrorController.reportError("Exception occurred when extracting episode number with regex", exception=exception, sendEmail=True)
        return None


def extractExtension(fileName):
    return os.path.splitext(fileName)[1]


def reportItemAlreadyExists(newItemLocation, torrentName):
    errorString = f"Downloaded torrent: {torrentName} and attempted to move it to {newItemLocation} but this target already exists."
    ErrorController.reportError(errorString, sendEmail=True)


def getLargestFileInDir(directory):
    filesInDir = list(os.scandir(directory))
    filesInDir = sorted(filesInDir, key=lambda file: -1 * int(os.path.getsize(f"{directory}/{file.name}")))
    if filesInDir:
        return filesInDir[0]
        
    logging.info(f"Tried to getLargestFileInDir from {directory} but a file cold not be located")
    return None

def auditFileSystemItemsForEpisodes(mode, filteredDownloadingItems):
    
    logging.info("File auditing started.")
    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
    dumpCompleteDir = os.getenv("DUMP_COMPLETE_DIR")
    fileSystemItemsFromDirectory = FolderInterface.getDirContents(dumpCompleteDir)
    logging.info(f"Items in dump_complete directory: {[item.name for item in fileSystemItemsFromDirectory] }")

    # deal with directories
    for fileSystemItem in fileSystemItemsFromDirectory:
        if fileSystemItem.name in filteredDownloadingItems:            
            #browse past the fake directory with the known name that we passed to qbittorrent
            fileSystemSubItems = list(os.scandir(fileSystemItem.path))
            itemId = fileSystemItem.name
            
            fileSystemItem = fileSystemSubItems[0]
            fileSystemItemName = fileSystemItem.name
            
            # attempt to pause torrent
            if QBittorrentInterface.pauseTorrent(fileSystemItem.name):
                logging.info(f"Paused torrent activity: ({fileSystemItem.name})")
            else:
                logging.info(f"Failed to pause torrent activity: ({fileSystemItem.name})")
            
            if not fileSystemSubItems:
                logging.info(f"Tried to browse past the directory created by qbittorrent ({fileSystemItem.path}) but nothing was found inside.")
                continue

            logging.info(f"{fileSystemItemName} has finished downloading and will be moved.")
            
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

                    if not targetFile:
                        continue
                    logging.info(f"{fileSystemItem.name} is a directory. The file {targetFile.name} has been extracted as the media item of interest.")
                else:
                    # TODO: eventually we should deal with the download of a full season directory, unnecessary at this point, for now we can assume that if no episode can be found
                    continue

            extension = extractExtension(targetFile.name)

            # create season directory if it does not exist
            if not FolderInterface.directoryExists(seasonDir):
                FolderInterface.createDirectory(seasonDir)

            prospectiveFile = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")
                        
            if not FolderInterface.fileExists(prospectiveFile):
                # move file to appropriate directory
                os.rename(targetFile.path, prospectiveFile)
                logging.info(f"Moved '{targetFile.path}' to '{prospectiveFile}'")
                DownloadsInProgressFileInterface.notifyDownloadFinished(itemId, PROGRAM_MODE.TV_EPISODES)

                if itemIsDirectory:
                    # attempt to move the rest of the files to the recycle_bin folder so if the program made an error, the downloaded content still might be recoverable
                    try:
                        recycle_bin_dir = os.getenv("RECYCLE_BIN_DIR")
                        shutil.move(fileSystemItem.path, recycle_bin_dir)
                        logging.info(f"Stored '{fileSystemItem.path}' in '{recycle_bin_dir}', in case it is needed. Please remember to delete items from here.")
                    except OSError as exception:
                        ErrorController.reportError("Exception occurred when moving residual files to the recycle bin dir", exception=exception, sendEmail=True)
                        continue
                
                
                # handle deletion of the container directory created by qbittorrent
                containerDir = os.path.dirname(fileSystemItem.path)
                os.rmdir(containerDir)

            else:
                # report problem
                reportItemAlreadyExists(prospectiveFile, fileSystemItem.path)


def auditDumpCompleteDir(mode, filteredDownloadingItems):
    # look for episodes
    auditFileSystemItemsForEpisodes(mode, filteredDownloadingItems)
