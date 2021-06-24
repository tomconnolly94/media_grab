#!/venv/bin/python

# external dependencies
import os
import logging
import re

# internal dependencies
from src.controllers import ErrorController
from src.interfaces import FolderInterface

def downloadWasInitiatedByMediaGrab(downloadId):
    """
    downloadWasInitiatedByMediaGrab checks if a download was initiated by mediaGrab using a regex
    :testedWith: TestCompletedDownloadsController:test_downloadWasInitiatedByMediaGrab
    :param downloadId: the downloadId of the download
    :param downloadIsEpisode: download is an episode, this determines which regex to use
    :return: the tv show name or `None` if one cannot be found
    """
    try:
        relevantRegexes = [r"[ \w]+--s\d+e\d+", r"[ \w]+--s\d+(?![es])"]

        for regexRaw in relevantRegexes:
            match = re.search(regexRaw, downloadId,
                              re.IGNORECASE | re.MULTILINE)
            if match:
                return True
        return False
    except Exception as exception:
        ErrorController.reportError(
            "Exception occurred when checking if a download was initiated by mediaGrab using a regex", exception=exception, sendEmail=True)
        return False


def extractShowName(downloadId):
    """
    extractShowName extracts the show name from the downloadId, using a different method depending on whether the download was initiated by mediaGrab or not
    :testedWith: TestCompletedDownloadsController:test_extractShowName
    :param downloadId: the downloadId of the download
    :return: the tv show name or `None` if one cannot be found
    """

    if downloadWasInitiatedByMediaGrab(downloadId):
        splitId = downloadId.split("--")
        if splitId and splitId[0]:
            return splitId[0]
        return None
    else:
        try:
            # extract show name using regex capturing group
            showNameMatch = re.match(
                r"(.+?)(?:[^a-zA-Z]*(?:season|s|episode|e)+.\d+.*)*?\s*$", downloadId, re.IGNORECASE)
            showName = showNameMatch.groups()[0]
            # replace all punctuation
            showName = re.sub(r"[^\w\s]", " ", showName)
            showName = showName.strip()  # remove whitespace on left or right
            showName = " ".join(showName.split())  # remove any double spaces
            showName = showName.lower()  # convert uppercase letters to lowercase
            if showName:
                return showName
            else:
                return None
        except Exception as exception:
            ErrorController.reportError(
                "Exception occurred when extracting season number with regex", exception=exception, sendEmail=True)
            return None


def extractSeasonNumber(downloadId):
    """
    extractSeasonNumber extracts the season number from the downloadId, using a different regex depending on whether the download was initiated by mediaGrab or not
    :testedWith: TestCompletedDownloadsController:test_extractSeasonNumber
    :param downloadId: the downloadId of the download
    :return: the season number or `None` if one cannot be found
    """
    try:
        regexRaw = ""
        if downloadWasInitiatedByMediaGrab(downloadId):
            regexRaw = r"--s(\d+)"
        else:
            regexRaw = r"(?:S|Season)(\d{1,2})"

        matches = re.search(regexRaw, downloadId, re.IGNORECASE | re.MULTILINE)

        if matches and matches.groups() and matches.groups()[0]:
            seasonNumber = int(matches.groups()[0])

            if seasonNumber:
                return seasonNumber
        return None
    except Exception as exception:
        ErrorController.reportError(
            "Exception occurred when extracting season number with regex", exception=exception, sendEmail=True)
        return None


def extractEpisodeNumber(downloadId):
    """
    extractEpisodeNumber extracts the episode number from the downloadId, using a different regex depending on whether the download was initiated by mediaGrab or not
    :testedWith: TestCompletedDownloadsController:test_extractEpisodeNumber
    :param downloadId: the downloadId of the download
    :return: the episode number or `None` if one cannot be found
    """
    try:
        regexRaw = ""
        if downloadWasInitiatedByMediaGrab(downloadId):
            regexRaw = r"--s\d+e(\d+)"
        else:
            regexRaw = r"(?:E|Episode)(\d{1,2})"

        matches = re.search(regexRaw, downloadId, re.IGNORECASE | re.MULTILINE)

        if matches and matches.groups() and matches.groups()[0]:
            episodeNumber = int(matches.groups()[0])

            if episodeNumber:
                return episodeNumber
        return None
    except Exception as exception:
        ErrorController.reportError(
            "Exception occurred when extracting episode number with regex", exception=exception, sendEmail=True)
        return None


def extractExtension(fileName):
    """
    extractExtension extracts the extension from a file name.
    :testedWith: TestCompletedDownloadsController:test_extractExtension
    :param fileName: the full name of the file
    :return: the file extension or an empty string if none can be found
    """
    return os.path.splitext(fileName)[1]


def reportItemAlreadyExists(newItemLocation, downloadName):
    """
    reportItemAlreadyExists reports that the item already exists in the file system
    :testedWith: TestCompletedDownloadsController:test_reportItemAlreadyExists
    :param newItemLocation: the prospective location of the finished download
    :param downloadName: the original name of the download
    """
    errorString = f"Downloaded torrent: {downloadName} and attempted to move it to {newItemLocation} but this target already exists."
    ErrorController.reportError(errorString, sendEmail=True)


def getLargestItemInDir(directory):
    """
    getLargestItemInDir finds the largest item inside the given directory
    :testedWith: TestCompletedDownloadsController:test_getLargestItemInDir
    :param directory: the directory to be explored
    :return: the largest item in the drectory or `None` if the directory is empty
    """
    filesInDir = list(os.scandir(directory))
    if filesInDir:
        filesInDir = sorted(filesInDir, key=lambda file: -
                            1 * int(os.path.getsize(f"{directory}/{file.name}")))
        return filesInDir[0]

    logging.info(
        f"Tried to getLargestItemInDir from {directory} but a file cold not be located")
    return None


def ensureDirStructureExists(tvShowDirPath, seasonDirPath):
    """
    ensureDirStructureExists explores the file system to ensure that the directory structure required as a target for the download exists
    :testedWith: TestCompletedDownloadsController:test_ensureDirStructureExists
    :param tvShowDirPath: the name of the tv show from the download
    :param seasonDirPath: the number of the season from the download
    :return: the success or failure of the file system manipulation
    """
    try:
        # create tv show directory if it does not exist
        if not FolderInterface.directoryExists(tvShowDirPath):
            FolderInterface.createDirectory(tvShowDirPath)

        # create season directory if it does not exist
        if not FolderInterface.directoryExists(seasonDirPath):
            FolderInterface.createDirectory(seasonDirPath)

        return True
    except Exception as exception:
        ErrorController.reportError(
            "Directory structure could not be completed", exception=exception, sendEmail=True)
        return None
