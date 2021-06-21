#!/venv/bin/python

# external dependencies
import os
import logging
import re
from datetime import datetime, timedelta

# internal dependencies
from dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP
from dataTypes.ProgramMode import PROGRAM_MODE
from interfaces import FolderInterface, QBittorrentInterface
from controllers import ErrorController
from controllers import CompletedDownloadsControllerUtilities as Utilities


def requestTorrentPause(torrentName):
    """
    requestTorrentPause requests that the torrent client pauses the activity of the torrent
    :testedWith: TestCompletedDownloadsController:test_requestTorrentPause
    :param torrentName: the name of the torrent to be paused
    :return: None
    """
    qBittorrentInterfaceInstance = QBittorrentInterface.getInstance() # access singleton instance

    # attempt to pause torrent
    if qBittorrentInterfaceInstance.pauseTorrent(torrentName):
        logging.info(f"Paused torrent activity: ({torrentName})")
    else:
        logging.info(f"Failed to pause torrent activity: ({torrentName})")


def getTargetFile(fileSystemItem):
    """
    getTargetFile gets the target media file of interest from a file system item, which could be the target file, or could be the directory that the target file is in
    :testedWith: TestCompletedDownloadsController:test_getTargetFile
    :param fileSystemItem: the file system item, it could be a directory or a file
    :return: the file system item if it is a file or if it is a directory then the largest file in that directory
    """
    if FolderInterface.directoryExists(fileSystemItem.path): # check if the fileSystemItem is a directory or a file
        targetFile = Utilities.getLargestItemInDir(
            fileSystemItem.path)  # we assume that the target file is the largest file

        if targetFile:
            logging.info(f"{fileSystemItem.name} is a directory. The file {targetFile.name} has been extracted as the media item of interest.")
            return targetFile

        ErrorController.reportError(f"The fileSystemItem: {fileSystemItem.name} is a directory but a targetFile could not be extracted. Skipping...")
        return None
    return fileSystemItem


def getTargetFiles(fileSystemItem):
    """
    getTargetFile gets the target media file of interest from a file system item, which could be the target file, or could be the directory that the target file is in
    :testedWith: TestCompletedDownloadsController:test_getTargetFile
    :param fileSystemItem: the file system item, it could be a directory or a file
    :return: the file system item if it is a file or if it is a directory then the largest file in that directory
    """
    if FolderInterface.directoryExists(fileSystemItem.path): # check if the fileSystemItem is a directory or a file
        targetFiles = FolderInterface.getDirContents(fileSystemItem) # we assume that the target file is the largest file

        if targetFiles:
            targetFiles = list(filter(lambda targetFile: 50000000 < int(os.path.getsize(targetFile)), targetFiles))

            joinedTargetFileString = "\"" + "\n".join([ targetFile.name for targetFile in targetFiles ]) + "\n"
            
            logging.info(
                f"{fileSystemItem.name} is a full season directory. The files: {joinedTargetFileString} have been extracted as the media items of interest. A filter of >50MB was applied.")
            return targetFiles

        ErrorController.reportError(f"The fileSystemItem: {fileSystemItem.name} is a directory but targetFiles could not be extracted. Skipping...")
        return None
    return None


def getProspectiveFilePath(downloadId, mode, extension):
    """
    getProspectiveFilePath create the prospective file path by extracting the necessary info like the tv show name and season/episode numbers
    :testedWith: TestCompletedDownloadsController:test_getProspectiveFilepPath
    :param downloadId: the downloadId for the downloaded item
    :param mode: the mode of the program run
    :param extension: the extension of the downloaded file
    :return: the path of the file after it has been moved to its prospective location
    """
    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
    showName = Utilities.extractShowName(
        downloadId).capitalize()  # name of the tv show
    tvShowDir = os.path.join(targetDir, showName) # target path of the tv show directory
    seasonNumber = Utilities.extractSeasonNumber(
        downloadId)  # extract season number
    episodeNumber = Utilities.extractEpisodeNumber(
        downloadId)  # extract episode number
    seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}") # target path for the relevant season directory of the tv show

    if not showName or not seasonNumber or not episodeNumber:
        return None

    Utilities.ensureDirStructureExists(
        tvShowDir, seasonDir)
    prospectiveFile = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")
    return prospectiveFile


def unWrapQBittorrentWrapperDir(fileSystemItem):
    """
    unWrapQBittorrentWrapperDir browses past the identifiable directory provided by qbittorrent to access the downloaded item
    :testedWith: TestCompletedDownloadsController:test_unWrapQBittorrentWrapperDir
    :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
    :return: the file system item, could be a file or directory which is the only contents of the input dir
    """
    fileSystemSubItems = list(os.scandir(fileSystemItem.path))

    # Assert that there is only one item inside the qBittorrent wrapper dir
    if len(fileSystemSubItems) != 1:
        logging.info(f"Tried to browse past the directory created by qbittorrent ({fileSystemItem.path}) but nothing was found inside.")
        return None
    
    return fileSystemSubItems[0]


def auditFileSystemItemForSeason(fileSystemItem):
    """
    auditMediaGrabItemForEpisode collates all the operations necessary to deal with a finished download (that was initiated by mediaGrab), move it to an organised file system location, and notifies the user
    :testedWith: TestCompletedDownloadsController:test_auditMediaGrabItemForEpisode
    :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
    :return: None
    """
    # capture the parent directory as the item's downloadId
    downloadId = fileSystemItem.name
    containerDir = fileSystemItem.path
    if Utilities.downloadWasInitiatedByMediaGrab(downloadId):
        fileSystemItem = unWrapQBittorrentWrapperDir(fileSystemItem)

    if not fileSystemItem:
        return

    targetFiles = getTargetFiles(fileSystemItem)

    # if target files could not be extracted, skip this fileSystemItem
    if not targetFiles:
        return False

    # pause torrent to prevent unneccessary seeding
    requestTorrentPause(fileSystemItem.name)

    logging.info(
        f"{fileSystemItem.name} has finished downloading and will be moved.")

    for targetFile in targetFiles:
        episodeNumber = Utilities.extractEpisodeNumber(targetFile.name)
        targetFileDownloadId = f"{downloadId}e{episodeNumber}"
        if not moveFile(
                targetFile, fileSystemItem, targetFileDownloadId):
            return False

    if Utilities.downloadWasInitiatedByMediaGrab(downloadId) and containerDir:
        # handle deletion of the container directory created by qbittorrent
        try:
            return postMoveDirectoryCleanup(downloadId, targetFile,
                                        fileSystemItem, containerDir)
        except OSError as exception:
            ErrorController.reportError(
                "Exception occurred when deleting season directory", exception=exception, sendEmail=True)
            return None


def auditFileSystemItemForEpisode(fileSystemItem):
    """
    auditMediaGrabItemForEpisode collates all the operations necessary to deal with a finished download (that was initiated by mediaGrab), move it to an organised file system location, and notifies the user
    :testedWith: TestCompletedDownloadsController:test_auditMediaGrabItemForEpisode
    :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
    :return: None
    """
    # capture the parent directory as the item's downloadId
    downloadId = fileSystemItem.name
    containerDir = fileSystemItem.path
    if Utilities.downloadWasInitiatedByMediaGrab(downloadId):
        fileSystemItem = unWrapQBittorrentWrapperDir(fileSystemItem)
    
    if not fileSystemItem:
        return False
    
    targetFile = getTargetFile(fileSystemItem)

    # if target file could not be extracted, skip this fileSystemItem
    if not targetFile:
        return False

    # pause torrent to prevent unneccessary seeding
    requestTorrentPause(fileSystemItem.name)

    logging.info(
        f"{fileSystemItem.name} has finished downloading and will be moved.")

    
    if(moveFile(targetFile, fileSystemItem, downloadId, containerDir)):
        return postMoveDirectoryCleanup(downloadId, targetFile,
                             fileSystemItem, containerDir)
    return False


def moveFile(targetFile, fileSystemItem, downloadId, containerDir=None):

    extension = Utilities.extractExtension(targetFile.name)
    
    # generate the prospective file path, ensuring all parent directories exist
    prospectiveFile = getProspectiveFilePath(
        downloadId, PROGRAM_MODE.TV, extension)

    if not prospectiveFile:
        return False

    # check if the prospective target file already exists
    if FolderInterface.fileExists(prospectiveFile):
        # report problem
        Utilities.reportItemAlreadyExists(prospectiveFile, fileSystemItem.path)
        return False

    # move file to appropriate directory
    os.rename(targetFile.path, prospectiveFile)
    logging.info(f"Moved '{targetFile.path}' to '{prospectiveFile}'")
    
    return True    


def postMoveDirectoryCleanup(downloadId, targetFile, fileSystemItem, containerDir):
    
    try:
        # if fileSystemItem is a directory, then clean up the directory and the rest of the contents
        if targetFile != fileSystemItem and containerDir:
            if not FolderInterface.recycleOrDeleteDir(fileSystemItem.path):
                return False

        if Utilities.downloadWasInitiatedByMediaGrab(downloadId) and containerDir:
            # handle deletion of the container directory created by qbittorrent
            os.rmdir(containerDir)
        return True
    except Exception as exception:
        ErrorController.reportError(
            "Exception occurred when cleaning up directories", exception=exception, sendEmail=True)
    

def auditDumpCompleteDir():
    """
    auditDumpCompleteDir wrapper, entry function to this module to collate all operations necessary for download directory auditing
    :testedWith: TestCompletedDownloadsController:test_auditFilesWithFileSystem
    :return: None
    """

    # auditing is not necessary if the optional env "TV_TARGET_DIR" is not provided
    if "TV_TARGET_DIR" not in os.environ:
        return

    logging.info("File auditing started.")
    dumpCompleteDir = os.getenv("DUMP_COMPLETE_DIR")
    fileSystemItemsFromDirectory = FolderInterface.getDirContents(
        dumpCompleteDir)
    logging.info(
        f"Items in dump_complete directory: {[item.name for item in fileSystemItemsFromDirectory] }")

    # divide the directories into two lists, those initiated by mediaGrab and those initiated manually
    for fileSystemItem in fileSystemItemsFromDirectory:
        if(auditFileSystemItemForEpisode(fileSystemItem)):
            continue

        if(auditFileSystemItemForSeason(fileSystemItem)):
            continue

    
    # deal with expired recycled items and logs
    permanentlyDeleteExpiredItems()


def permanentlyDeleteExpiredItems():
    """
    permanentlyDeleteExpiredItems performs a sub audit of the recycle_bin directory and the log directory, in order to delete any files or directories that are deemed too old
    :testedWith: TestCompletedDownloadsController:test_permanentlyDeleteExpiredItems
    :return: None
    """
    # delete recycled directories older than 4 weeks
    recycleBinDir = os.getenv("RECYCLE_BIN_DIR")
    recycledFileSystemDirs = FolderInterface.getDirContents(
        recycleBinDir)

    dateFourWeeksAgo = datetime.now() - timedelta(weeks=4)
    dateOneWeekAgo = datetime.now() - timedelta(weeks=1)

    for directoryItem in recycledFileSystemDirs:
        fileCreationDate = datetime.fromtimestamp(os.path.getctime(directoryItem.path))

        if fileCreationDate < dateFourWeeksAgo:
            FolderInterface.deleteDir(directoryItem.path)

    # get log files from logs dir
    logFiles = FolderInterface.getDirContents("logs")

    for logFile in logFiles:
        fileCreationDate = datetime.fromtimestamp(os.path.getctime(logFile.path))

        if fileCreationDate < dateOneWeekAgo:
            FolderInterface.deleteFile(logFile.path)
