#!/venv/bin/python

# external dependencies
import os
import logging
import re

#internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP

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
    return os.scandir(directory)