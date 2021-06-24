#!/venv/bin/python

# external
import os
import logging
from src.controllers import ErrorController

# internal dependencies
from src.dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP
from src.dataTypes.ProgramMode import PROGRAM_MODE
from src.interfaces import FolderInterface, QBittorrentInterface
from src.utilities import AuditUtilities


class AuditStrategy:

    def __init__(self):
        pass


    def unWrapQBittorrentWrapperDir(self, fileSystemItem):
        """
        unWrapQBittorrentWrapperDir browses past the identifiable directory provided by qbittorrent to access the downloaded item
        :testedWith: TestCompletedDownloadsController:test_unWrapQBittorrentWrapperDir
        :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
        :return: the file system item, could be a file or directory which is the only contents of the input dir
        """
        fileSystemSubItems = list(os.scandir(fileSystemItem.path))

        # Assert that there is only one item inside the qBittorrent wrapper dir
        if len(fileSystemSubItems) != 1:
            logging.info(
                f"Tried to browse past the directory created by qbittorrent ({fileSystemItem.path}) but nothing was found inside.")
            return None

        return fileSystemSubItems[0]

    
    def getTargetFile(fileSystemItem):
        """
        getTargetFile gets the target media file of interest from a file system item, which could be the target file, or could be the directory that the target file is in
        :testedWith: TestCompletedDownloadsController:test_getTargetFile
        :param fileSystemItem: the file system item, it could be a directory or a file
        :return: the file system item if it is a file or if it is a directory then the largest file in that directory
        """
        if FolderInterface.directoryExists(fileSystemItem.path):  # check if the fileSystemItem is a directory or a file
            # we assume that the target file is the largest file
            targetFile = AuditUtilities.getLargestItemInDir(
                fileSystemItem.path)

            if targetFile:
                logging.info(
                    f"{fileSystemItem.name} is a directory. The file {targetFile.name} has been extracted as the media item of interest.")
                return targetFile

            ErrorController.reportError(
                f"The fileSystemItem: {fileSystemItem.name} is a directory but a targetFile could not be extracted. Skipping...")
            return None
        return fileSystemItem


    def getTargetFiles(self, fileSystemItem):
        """
        getTargetFile gets the target media file of interest from a file system item, which could be the target file, or could be the directory that the target file is in
        :testedWith: TestCompletedDownloadsController:test_getTargetFile
        :param fileSystemItem: the file system item, it could be a directory or a file
        :return: the file system item if it is a file or if it is a directory then the largest file in that directory
        """
        if FolderInterface.directoryExists(fileSystemItem.path):  # check if the fileSystemItem is a directory or a file
            # we assume that the target file is the largest file
            targetFiles = FolderInterface.getDirContents(fileSystemItem)

            if targetFiles:
                targetFiles = list(filter(lambda targetFile: 50000000 < int(
                    os.path.getsize(targetFile)), targetFiles))

                joinedTargetFileString = "\"" + \
                    "\n".join(
                        [targetFile.name for targetFile in targetFiles]) + "\n"

                logging.info(
                    f"{fileSystemItem.name} is a full season directory. The files: {joinedTargetFileString} have been extracted as the media items of interest. A filter of >50MB was applied.")
                return targetFiles

            ErrorController.reportError(
                f"The fileSystemItem: {fileSystemItem.name} is a directory but targetFiles could not be extracted. Skipping...")
            return None
        return None


    def getProspectiveFilePath(self, downloadId, mode, extension):
        """
        getProspectiveFilePath create the prospective file path by extracting the necessary info like the tv show name and season/episode numbers
        :testedWith: TestCompletedDownloadsController:test_getProspectiveFilepPath
        :param downloadId: the downloadId for the downloaded item
        :param mode: the mode of the program run
        :param extension: the extension of the downloaded file
        :return: the path of the file after it has been moved to its prospective location
        """

        dir_key = PROGRAM_MODE_DIRECTORY_KEY_MAP[mode]
        targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
        showName = AuditUtilities.extractShowName(
            downloadId).capitalize()  # name of the tv show
        # target path of the tv show directory
        tvShowDir = os.path.join(targetDir, showName)
        seasonNumber = AuditUtilities.extractSeasonNumber(
            downloadId)  # extract season number
        episodeNumber = AuditUtilities.extractEpisodeNumber(
            downloadId)  # extract episode number
        # target path for the relevant season directory of the tv show
        seasonDir = os.path.join(tvShowDir, f"Season {seasonNumber}")

        if not showName or not seasonNumber or not episodeNumber:
            return None

        AuditUtilities.ensureDirStructureExists(
            tvShowDir, seasonDir)
        prospectiveFile = os.path.join(
            seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")
        return prospectiveFile


    def moveFile(self, targetFile, fileSystemItem, downloadId, containerDir=None):

        extension = AuditUtilities.extractExtension(targetFile.name)

        # generate the prospective file path, ensuring all parent directories exist
        prospectiveFile = self.getProspectiveFilePath(
            downloadId, PROGRAM_MODE.TV, extension)

        if not prospectiveFile:
            return False

        # check if the prospective target file already exists
        if FolderInterface.fileExists(prospectiveFile):
            # report problem
            AuditUtilities.reportItemAlreadyExists(
                prospectiveFile, fileSystemItem.path)
            return False

        # move file to appropriate directory
        os.rename(targetFile.path, prospectiveFile)
        logging.info(f"Moved '{targetFile.path}' to '{prospectiveFile}'")

        return True


    def postMoveDirectoryCleanup(self, downloadId, targetFile, fileSystemItem, containerDir):

        try:
            # if fileSystemItem is a directory, then clean up the directory and the rest of the contents
            if targetFile != fileSystemItem and containerDir:
                if not FolderInterface.recycleOrDeleteDir(fileSystemItem.path):
                    return False

            if AuditUtilities.downloadWasInitiatedByMediaGrab(downloadId) and containerDir:
                # handle deletion of the container directory created by qbittorrent
                os.rmdir(containerDir)
            return True
        except Exception as exception:
            ErrorController.reportError(
                "Exception occurred when cleaning up directories", exception=exception, sendEmail=True)


    def requestTorrentPause(self, torrentName):
        """
        requestTorrentPause requests that the torrent client pauses the activity of the torrent
        :testedWith: TestCompletedDownloadsController:test_requestTorrentPause
        :param torrentName: the name of the torrent to be paused
        :return: None
        """
        qBittorrentInterfaceInstance = QBittorrentInterface.getInstance(
        )  # access singleton instance

        # attempt to pause torrent
        if qBittorrentInterfaceInstance.pauseTorrent(torrentName):
            logging.info(f"Paused torrent activity: ({torrentName})")
        else:
            logging.info(f"Failed to pause torrent activity: ({torrentName})")
