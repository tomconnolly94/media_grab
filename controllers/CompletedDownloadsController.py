#!/venv/bin/python

# external dependencies
import os
import logging
import re
import shutil
from datetime import datetime, timedelta

# internal dependencies
from dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP, PROGRAM_MODE_MAP
from dataTypes.ProgramMode import PROGRAM_MODE
from interfaces import FolderInterface, QBittorrentInterface
from controllers import ErrorController


def downloadWasInitiatedByMediaGrab(downloadId):
    """
    downloadWasInitiatedByMediaGrab checks if a download was initiated by mediaGrab using a regex

    :testedWith: testCompletedDownloadsController:test_downloadWasInitiatedByMediaGrab

    :param downloadId: the downloadId of the download
    :return: the tv show name or `None` if one cannot be found
    """

    try:
        regexRaw = r"[ \w]+--s\d+e\d+"
        match = re.search(regexRaw, downloadId,
                            re.IGNORECASE | re.MULTILINE)
        if match:
            return True
        return False
    except Exception as exception:
        ErrorController.reportError(
            "Exception occurred when checking if a download was initiated by mediaGrab using a regex", exception=exception, sendEmail=True)
        return False


def extractShowName(downloadId):
    """
    extractShowName extracts the show name from the downloadId, using a different method depending on whether the download was initiated by mediaGrab or not

    :testedWith: testCompletedDownloadsController:test_extractShowName

    :param downloadId: the downloadId of the download
    :return: the tv show name or `None` if one cannot be found
    """

    if downloadWasInitiatedByMediaGrab(downloadId):
        splitId = downloadId.split("--")
        if splitId and splitId[0]:
            return splitId[0]
        return None
    else:
        try:
            # extract show name using regex capturing group
            showNameMatch = re.match(
                r"(.+?)(?:[^a-zA-Z]*(?:season|s|episode|e)+.\d+.*)*?\s*$", downloadId, re.IGNORECASE)
            showName = showNameMatch.groups()[0]
            showName = re.sub(r"[^\w\s]", " ", showName)  # replace all punctuation
            showName = showName.strip()  # remove whitespace on left or right
            showName = " ".join(showName.split())  # remove any double spaces
            showName = showName.lower()  # convert uppercase letters to lowercase
            if showName:
                return showName
            else:
                return None
        except Exception as exception:
            ErrorController.reportError(
                "Exception occurred when extracting season number with regex", exception=exception, sendEmail=True)
            return None


def extractSeasonNumber(downloadId):
    """
    extractSeasonNumber extracts the season number from the downloadId, using a different regex depending on whether the download was initiated by mediaGrab or not

    :testedWith: testCompletedDownloadsController:test_extractSeasonNumber

    :param downloadId: the downloadId of the download
    :return: the season number or `None` if one cannot be found
    """
    try:
        regexRaw = ""
        if downloadWasInitiatedByMediaGrab(downloadId):
            regexRaw = r"--s(\d+)"
        else:
            regexRaw = r"(?:S|Season)(\d{1,2})"

        matches = re.search(regexRaw, downloadId, re.IGNORECASE | re.MULTILINE)
        
        if matches and matches.groups() and matches.groups()[0]:
            seasonNumber = int(matches.groups()[0])
            
            if seasonNumber:
                return seasonNumber
        return None
    except Exception as exception:
        ErrorController.reportError("Exception occurred when extracting season number with regex", exception=exception, sendEmail=True)
        return None


def extractEpisodeNumber(downloadId):
    """
    extractEpisodeNumber extracts the episode number from the downloadId, using a different regex depending on whether the download was initiated by mediaGrab or not

    :testedWith: testCompletedDownloadsController:test_extractEpisodeNumber

    :param downloadId: the downloadId of the download
    :return: the episode number or `None` if one cannot be found
    """
    try:
        regexRaw = ""
        if downloadWasInitiatedByMediaGrab(downloadId):
            regexRaw = r"--s\d+e(\d+)"
        else:
            regexRaw = r"(?:E|Episode)(\d{1,2})"

        matches = re.search(regexRaw, downloadId, re.IGNORECASE | re.MULTILINE)

        if matches and matches.groups() and matches.groups()[0]:
            episodeNumber = int(matches.groups()[0])        

            if episodeNumber:
                return episodeNumber
        return None
    except Exception as exception:
        ErrorController.reportError("Exception occurred when extracting episode number with regex", exception=exception, sendEmail=True)
        return None


def extractExtension(fileName):
    """
    extractExtension extracts the extension from a file name.

    :testedWith: testCompletedDownloadsController:test_extractExtension

    :param fileName: the full name of the file
    :return: the file extension or an empty string if none can be found
    """    
    return os.path.splitext(fileName)[1]


def reportItemAlreadyExists(newItemLocation, downloadName):
    """
    reportItemAlreadyExists reports that the item already exists in the file system

    :testedWith: testCompletedDownloadsController:test_reportItemAlreadyExists

    :param newItemLocation: the prospective location of the finished download
    :param downloadName: the original name of the download
    """
    errorString = f"Downloaded torrent: {downloadName} and attempted to move it to {newItemLocation} but this target already exists."
    ErrorController.reportError(errorString, sendEmail=True)


def getLargestItemInDir(directory):
    """
    getLargestItemInDir finds the largest item inside the given directory

    :testedWith: testCompletedDownloadsController:test_getLargestItemInDir

    :param directory: the directory to be explored
    :return: the largest item in the drectory or `None` if the directory is empty
    """
    filesInDir = list(os.scandir(directory))
    if filesInDir:
        filesInDir = sorted(filesInDir, key=lambda file: -1 * int(os.path.getsize(f"{directory}/{file.name}")))
        return filesInDir[0]
        
    logging.info(f"Tried to getLargestItemInDir from {directory} but a file cold not be located")
    return None


def requestTorrentPause(torrentName):
    """
    requestTorrentPause requests that the torrent client pauses the activity of the torrent

    :testedWith: testCompletedDownloadsController:test_requestTorrentPause

    :param torrentName: the name of the torrent to be paused
    """
    qBittorrentInterfaceInstance = QBittorrentInterface.getInstance() # access singleton instance

    # attempt to pause torrent
    if qBittorrentInterfaceInstance.pauseTorrent(torrentName):
        logging.info(f"Paused torrent activity: ({torrentName})")
    else:
        logging.info(f"Failed to pause torrent activity: ({torrentName})")


def ensureDirStructureExists(tvShowDirPath, seasonDirPath):
    """
    ensureDirStructureExists explores the file system to ensure that the directory structure
        required as a target for the download exists

    :testedWith: testCompletedDownloadsController:test_ensureDirStructureExists

    :param tvShowDirPath: the name of the tv show from the download
    :param seasonDirPath: the number of the season from the download
    :return: the success or failure of the file system manipulation
    """
    try:
        # create tv show directory if it does not exist
        if not FolderInterface.directoryExists(tvShowDirPath):
            FolderInterface.createDirectory(tvShowDirPath)

        # create season directory if it does not exist
        if not FolderInterface.directoryExists(seasonDirPath):
            FolderInterface.createDirectory(seasonDirPath)
            
        return True
    except Exception as exception:
        ErrorController.reportError("Directory structure could not be completed", exception=exception, sendEmail=True)
        return None


def getTargetFile(fileSystemItem):
    """
    getTargetFile gets the target media file of interest from a file system item, which could be the target file, or could be the directory that the target file is in

    :testedWith: testCompletedDownloadsController:test_getTargetFile

    :param fileSystemItem: the file system item, it could be a directory or a file
    :return: the file system item if it is a file or if it is a directory then the largest file in that directory
    """
    if FolderInterface.directoryExists(fileSystemItem.path): # check if the fileSystemItem is a directory or a file
        targetFile = getLargestItemInDir(fileSystemItem.path) # we assume that the target file is the largest file

        if targetFile:
            logging.info(f"{fileSystemItem.name} is a directory. The file {targetFile.name} has been extracted as the media item of interest.")
            return targetFile

        ErrorController.reportError(f"The fileSystemItem: {fileSystemItem.name} is a directory but a targetFile could not be extracted. Skipping...")
        return None
    return fileSystemItem


def getProspectiveFilePath(downloadId, mode, extension):
    """
    getProspectiveFilePath create the prospective file path by extracting the necessary info like the tv show name and season/episode numbers

    :testedWith: testCompletedDownloadsController:test_getProspectiveFilepPath

    :param downloadId: the downloadId for the downloaded item
    :param mode: the mode of the program run
    :param extension: the extension of the downloaded file
    :return: the path of the file after it has been moved to its prospective location
    """
    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
    showName = extractShowName(downloadId).capitalize() # name of the tv show
    tvShowDir = os.path.join(targetDir, showName) # target path of the tv show directory
    seasonNumber = extractSeasonNumber(downloadId) # extract season number
    episodeNumber = extractEpisodeNumber(downloadId) # extract episode number
    seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}") # target path for the relevant season directory of the tv show

    if not showName or not seasonNumber or not episodeNumber:
        return None

    ensureDirStructureExists(tvShowDir, seasonDir)
    prospectiveFile = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")
    return prospectiveFile


def unWrapQBittorrentWrapperDir(fileSystemItem):
    """
    unWrapQBittorrentWrapperDir browses past the identifiable directory provided by qbittorrent to access the downloaded item  

    :testedWith: testCompletedDownloadsController:test_unWrapQBittorrentWrapperDir

    :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
    :return: the file system item, could be a file or directory which is the only contents of the input dir
    """
    fileSystemSubItems = list(os.scandir(fileSystemItem.path))

    # Assert that there is only one item inside the qBittorrent wrapper dir
    if len(fileSystemSubItems) != 1:
        logging.info(f"Tried to browse past the directory created by qbittorrent ({fileSystemItem.path}) but nothing was found inside.")
        return None
    
    return fileSystemSubItems[0]


def auditFileSystemItemForEpisode(fileSystemItem):
    """
    auditMediaGrabItemForEpisode collates all the operations necessary to deal with a finished 
        download (that was initiated by mediaGrab), move it to an organised file system location, and notifies the user

    :testedWith: testCompletedDownloadsController:test_auditMediaGrabItemForEpisode

    :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
    """
    # capture the parent directory as the item's downloadId
    downloadId = fileSystemItem.name
    containerDir = fileSystemItem.path
    if downloadWasInitiatedByMediaGrab(downloadId):
        fileSystemItem = unWrapQBittorrentWrapperDir(fileSystemItem)
    
    if not fileSystemItem:
        return
    
    targetFile = getTargetFile(fileSystemItem)

    # if target file could not be extracted, skip this fileSystemItem
    if not targetFile:
        return

    extension = extractExtension(targetFile.name)
    
    # generate the prosepctive file path, ensuring all parent directories exist
    prospectiveFile = getProspectiveFilePath(
        downloadId, PROGRAM_MODE.TV_EPISODES, extension)

    if not prospectiveFile:
        return

    # pause torrent to prevent unneccessary seeding
    requestTorrentPause(fileSystemItem.name)

    logging.info(
        f"{fileSystemItem.name} has finished downloading and will be moved.")

    # check if the prospective target file already exists
    if FolderInterface.fileExists(prospectiveFile):
        # report problem
        reportItemAlreadyExists(prospectiveFile, fileSystemItem.path)
        return

    # move file to appropriate directory
    os.rename(targetFile.path, prospectiveFile)
    logging.info(f"Moved '{targetFile.path}' to '{prospectiveFile}'")

    # if fileSystemItem is a directory, then clean up the directory and the rest of the contents
    if targetFile != fileSystemItem: 
        FolderInterface.recycleOrDeleteDir(fileSystemItem.path)

    if downloadWasInitiatedByMediaGrab(downloadId):
        # handle deletion of the container directory created by qbittorrent
        os.rmdir(containerDir)


def auditFileSystemItemsForEpisodes():
    """
    auditFileSystemItemsForEpisodes handles the extraction and filtering of items in the dump_complete
        directory

    :testedWith: testCompletedDownloadsController:test_auditFileSystemItemsForEpisodes

    """
    # auditing is not necessary if the optional env "TV_TARGET_DIR" is not provided
    if "TV_TARGET_DIR" not in os.environ:
        return

    logging.info("File auditing started.")
    dumpCompleteDir = os.getenv("DUMP_COMPLETE_DIR")
    fileSystemItemsFromDirectory = FolderInterface.getDirContents(dumpCompleteDir)
    logging.info(f"Items in dump_complete directory: {[item.name for item in fileSystemItemsFromDirectory] }")

    mediaGrabInitiatedDownloads = []
    manuallyInitiatedDownloads = []

    # divide the directories into two lists, those initiated by mediaGrab and those initiated manually
    for fileSystemItem in fileSystemItemsFromDirectory:
        auditFileSystemItemForEpisode(fileSystemItem)


def auditDumpCompleteDir():
    # look for episodes
    auditFileSystemItemsForEpisodes()
    # deal with expired recycled items and logs
    permanentlyDeleteExpiredItems()


def permanentlyDeleteExpiredItems():
    # delete recycled directories older than 4 weeks
    recycleBinDir = os.getenv("RECYCLE_BIN_DIR")
    recycledFileSystemDirs = FolderInterface.getDirContents(
        recycleBinDir)

    fourWeekTimeThreshold = datetime.now() - timedelta(weeks=4)
    oneWeekTimeThreshold = datetime.now() - timedelta(weeks=1)

    for directoryItem in recycledFileSystemDirs:
        fileAge = datetime.fromtimestamp(os.path.getctime(directoryItem.path))

        if fileAge < fourWeekTimeThreshold:
            FolderInterface.deleteDir(directoryItem.path)

    # get log files from logs dir
    logFiles = FolderInterface.getDirContents("logs")

    for logFile in logFiles:
        fileAge = datetime.fromtimestamp(os.path.getctime(logFile.path))

        if fileAge < oneWeekTimeThreshold:
            FolderInterface.deleteFile(logFile.path)
