#!/venv/bin/python

# external dependencies
import os
import logging
import re
import shutil

#internal dependencies
from dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP
from controllers import ErrorController

def createDirectory(newDirectoryName):
    try:
        os.mkdir(newDirectoryName)
        # log action
        logging.info(f"Created directory: {newDirectoryName}")
        return True
    except:
        return False


def directoryExists(dirName):
    return os.path.isdir(dirName)


def fileExists(fileName):
    return os.path.isfile(fileName)


def getDirContents(directory):
    try:
        return list(os.scandir(directory))
    except OSError as exception:
        ErrorController.reportError(f"Failed to scan {directory} drive is probably inaccessible.", exception, True)
        return []


def deleteDir(directoryPath):
    try:
        shutil.rmtree(directoryPath)
        logging.info(f"Deleted '{directoryPath}'")
    except OSError as exception:
        ErrorController.reportError(f"Exception occurred whilst deleting residual directory `{directoryPath}`", exception=exception, sendEmail=True)
        return False


def recycleOrDeleteDir(directoryPath):
    """
    recycleDir attempts to move the parent directory containing the rest of the downloaded files to the recycle_bin folder 
        so if the program made an error, the downloaded content still might be recoverable

    :testedWith: testCompletedDownloadsController:test_recycleDir

    :param fileSystemItem: the directory to be moved to the recycle bin
    :return: bool for success/failure of the move operation
    """
    try:
        # if user has not specified a RECYCLE_BIN_DIR in the .env file then the directory cannot be recycled, it is not critical so it will be deleted
        if os.getenv("RECYCLE_BIN_DIR") and None: # deactivated for now
            logging.info(f"`RECYCLE_BIN_DIR` env value not specified in .env file so '{directoryPath}' cannot be recycled.")
            deleteDir(directoryPath)

        recycle_bin_dir = os.getenv("RECYCLE_BIN_DIR")
        shutil.move(directoryPath, recycle_bin_dir)
        logging.info(f"Stored '{directoryPath}' in '{recycle_bin_dir}', in case it is needed. Please remember to delete items from here.")
        return True
    except OSError as exception:
        ErrorController.reportError("Exception occurred whilst moving residual directory `{directoryPath}` to the recycle bin dir", exception=exception, sendEmail=True)
        return False
