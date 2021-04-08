#!/venv/bin/python

# external dependencies
import os
import logging
import re
import shutil

#internal dependencies
from dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP
from controllers import ErrorController


def createDirectory(newDirectoryPath):
    """
    createDirectory attempts to create a directory using the absolute path passed in as a param
    :testedWith: None - too small to be necessary
    :param newDirectoryPath: absolute path of new directory
    :return: bool signalling the success of the operation
    """
    try:
        os.mkdir(newDirectoryPath)
        # log action
        logging.info(f"Created directory: {newDirectoryPath}")
        return True
    except FileExistsError:
        return False


def directoryExists(dirPath):
    """
    directoryExists checks if directory exists using the absolute path passed in as a param
    :testedWith: None - too small to be necessary
    :param newDirectoryPath: absolute path of directory
    :return: bool signalling whet
    """
    return os.path.isdir(dirPath)


def fileExists(filePath):
    """
    fileExists checks if file exists using the absolute path passed in as a param
    :testedWith: None - too small to be necessary
    :param newDirectoryPath: absolute path of file
    :return: bool signalling the success of the operation
    """
    return os.path.isfile(filePath)


def getDirContents(directoryPath):
    """
    getDirContents gets all sub-files and sub-directories of the absolute directory path passed in as a param 
    :testedWith: None - too small to be necessary
    :param directoryPath: absolute path of the directory
    :return: list of files and directories
    """
    try:
        return list(os.scandir(directoryPath))
    except OSError as exception:
        ErrorController.reportError(
            f"Failed to scan {directoryPath} drive is probably inaccessible.", exception, True)
        return []


def deleteDir(directoryPath):
    """
    deleteDir attempts to delete the directory using the absolute path passed in as a param
    :testedWith: None - too small to be necessary
    :param directoryPath: absolute path of the directory
    :return: bool signalling the success of the operation
    """
    try:
        shutil.rmtree(directoryPath)
        logging.info(f"Deleted '{directoryPath}'")
    except OSError as exception:
        ErrorController.reportError(f"Exception occurred whilst deleting residual directory `{directoryPath}`", exception=exception, sendEmail=True)
        return False


def deleteFile(filePath):
    """
    deleteFile attempts to delete the file using the absolute path passed in as a param
    :testedWith: None - too small to be necessary
    :param filePath: absolute path of the file
    :return: bool signalling the success of the operation
    """
    try:
        if os.path.exists(filePath):
            os.remove(filePath)
            logging.info(f"Deleted '{filePath}'")

    except OSError as exception:
        ErrorController.reportError(
            f"Exception occurred whilst deleting residual file `{filePath}`", exception=exception, sendEmail=True)
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
        if "RECYCLE_BIN_DIR" not in os.environ:
            logging.info(f"`RECYCLE_BIN_DIR` env value not specified in .env file so '{directoryPath}' cannot be recycled.")
            deleteDir(directoryPath)
            return True

        recycle_bin_dir = os.getenv("RECYCLE_BIN_DIR")
        shutil.move(directoryPath, recycle_bin_dir)
        logging.info(f"Stored '{directoryPath}' in '{recycle_bin_dir}', in case it is needed. Please remember to delete items from here.")
        return True
    except OSError as exception:
        ErrorController.reportError("Exception occurred whilst moving residual directory `{directoryPath}` to the recycle bin dir", exception=exception, sendEmail=True)
        return False
