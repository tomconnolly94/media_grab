#!/venv/bin/python

# external
import logging

# internal dependencies
from src.strategies.AuditStrategy import AuditStrategy
from src.controllers import ErrorController
from src.utilities import AuditUtilities


class AuditSeasonStrategy(AuditStrategy):


    def audit(self, fileSystemItem):
        """
        auditMediaGrabItemForEpisode collates all the operations necessary to deal with a finished download (that was initiated by mediaGrab), move it to an organised file system location, and notifies the user
        :testedWith: TestCompletedDownloadsController:test_auditMediaGrabItemForEpisode
        :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
        :return: None
        """
        # capture the parent directory as the item's downloadId
        downloadId = fileSystemItem.name
        containerDir = fileSystemItem.path
        if AuditUtilities.downloadWasInitiatedByMediaGrab(downloadId):
            fileSystemItem = super(AuditSeasonStrategy,
                                   self).unWrapQBittorrentWrapperDir(fileSystemItem)

        if not fileSystemItem:
            return

        targetFiles = super(
            AuditSeasonStrategy, self).getTargetFiles(fileSystemItem)

        # if target files could not be extracted, skip this fileSystemItem
        if not targetFiles:
            return False

        # pause torrent to prevent unneccessary seeding
        super(AuditSeasonStrategy,
              self).requestTorrentPause(fileSystemItem.name)

        logging.info(
            f"{fileSystemItem.name} has finished downloading and will be moved.")

        for targetFile in targetFiles:
            episodeNumber = AuditUtilities.extractEpisodeNumber(
                targetFile.name)
            targetFileDownloadId = f"{downloadId}e{episodeNumber}"
            if not super(
                AuditSeasonStrategy, self).moveFile(
                    targetFile, fileSystemItem, targetFileDownloadId):
                return False

        if AuditUtilities.downloadWasInitiatedByMediaGrab(downloadId) and containerDir:
            # handle deletion of the container directory created by qbittorrent
            try:
                return super(
                    AuditSeasonStrategy, self).postMoveDirectoryCleanup(downloadId, targetFile,
                                                fileSystemItem, containerDir)
            except OSError as exception:
                ErrorController.reportError(
                    "Exception occurred when deleting season directory", exception=exception, sendEmail=True)
                return None
