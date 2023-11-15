#!/venv/bin/python

# external dependencies
import logging

from src.controllers import ErrorController


# internal dependencies
from src.strategies.AuditStrategy import AuditStrategy
from src.utilities import AuditUtilities
from src.exceptions.AuditingHiddenFileException import AuditingHiddenFileException


class AuditEpisodeStrategy(AuditStrategy):


    def audit(self, fileSystemItem):
        """
        audit collates all the operations necessary to deal with a finished episode download (that was initiated by mediaGrab), move it to an organised file system location, and notifies the user
        :testedWith: TestCompletedDownloadsController:test_auditMediaGrabItemForEpisode
        :param fileSystemItem: the file system item, it shall be a directory sharing the same name as the downloadId
        :return: True if the fileSystemItem was handled correctly and completed, false if not
        """
        # capture the item's top-level root directory as the item's downloadId
        downloadId = fileSystemItem.name
        containerDir = fileSystemItem.path

        if downloadId.startswith("."):
            ErrorController.reportError(f"AuditEpisodeStrategy.audit({fileSystemItem.name}) called but item starts with a '.' indicating it is a hidden item. Hidden items cannot be processed.", sendEmail=True)
            return False

        if AuditUtilities.downloadWasInitiatedByMediaGrab(downloadId):
            fileSystemItem = super().unWrapQBittorrentWrapperDir(fileSystemItem)

        if not fileSystemItem:
            return False

        targetFile = super().getTargetFile(fileSystemItem)

        # if target file could not be extracted, skip this fileSystemItem
        if not targetFile:
            return False

        # pause torrent to prevent unneccessary seeding
        super().requestTorrentPause(fileSystemItem.name)

        logging.info(f"{fileSystemItem.name} has finished downloading and will be moved.")

        if not super().moveFile(targetFile, fileSystemItem, downloadId, containerDir):
            return False

        if not super().postMoveDirectoryCleanup(downloadId, targetFile, fileSystemItem, containerDir):
            return False

        return True
