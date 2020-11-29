#!/venv/bin/python

# external dependencies
import os
import logging

#internal dependencies
from data_types.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP

def auditFolder(mode, filteredDownloadingItems):
    dumpCompleteDirPath = os.getenv("DUMP_COMPLETE_DIR")
    targetDir = os.getenv(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])

    directoryItems = os.scandir(dumpCompleteDirPath)
    completedDownloadFiles = [ directoryItem for directoryItem in directoryItems if os.path.isfile(directoryItem) ]
    completedDownloadDirectories = [ directoryItem for directoryItem in directoryItems if os.path.isdir(directoryItem) ]

    for completedDownloadFile in completedDownloadFiles:
        if completedDownloadFile in filteredDownloadingItems:
            os.rename(f"{dumpCompleteDirPath}{completedDownloadFile}", f"{targetDir}{completedDownloadFile}")


    # Rules:
    #
    # TV episodes:
    #   files - should find existing 

