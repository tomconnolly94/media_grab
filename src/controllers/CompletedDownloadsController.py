#!/venv/bin/python

# external dependencies
import os
import logging
from datetime import datetime, timedelta

# internal dependencies
from src.strategies.AuditEpisodeStrategy import AuditEpisodeStrategy
from src.strategies.AuditSeasonStrategy import AuditSeasonStrategy
from src.interfaces import FolderInterface

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
    fileSystemItemsFromDirectory = FolderInterface.getDirContents(dumpCompleteDir)

    logging.info(
        f"Items in dump_complete directory: {[item.name for item in fileSystemItemsFromDirectory] }")

    # divide the directories into two lists, those initiated by mediaGrab and those initiated manually
    for fileSystemItem in fileSystemItemsFromDirectory:

        auditStrategies = [AuditEpisodeStrategy(), AuditSeasonStrategy()]

        for auditStrategy in auditStrategies:
            if auditStrategy.audit(fileSystemItem):
                break

    
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
