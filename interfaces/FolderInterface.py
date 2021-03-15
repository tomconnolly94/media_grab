#!/venv/bin/python

# external dependencies
import os
import logging
import re

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
