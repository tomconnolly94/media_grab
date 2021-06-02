#!/venv/bin/python

# external dependencies
import requests
import logging
import json
from requests.exceptions import ChunkedEncodingError, ConnectionError
from json.decoder import JSONDecodeError

# internal dependencies
from controllers import TorrentFilterController, ErrorController
from dataTypes.TorrentRecord import TorrentRecord


def sortTorrents(torrents):
    """
    sortTorrents sorts a list of torrentRecord object based on whom has the most seeders
    :param torrents: list of torrents
    :testedWith: TestTPBInterface:test_getTorrentRecords
    :return: sorted list of torrents
    """
    return sorted(torrents, key=lambda torrent: -1 * torrent.getSeeders())


def getTorrentRecords(mediaInfoRecord):
    """
    getTorrentRecords attempts to find a torrentRecord for the mediaInfoRecord passed in 
    :param mediaInfoRecord: mediaInfoRecord for which torrent records should be found
    :testedWith: TestTPBInterface:test_getTorrentRecords
    :return: sorted and filtered list of torrents
    """
    # make query for the mediaInfoRecord, if none are found, try the next query format
    for queryStr in mediaInfoRecord.getMediaSearchQueries():
        torrentRecords = queryAPI(queryStr)
        
        #logging
        logging.info(f"Torrent search performed for: '{queryStr}' - {len(torrentRecords)} results.")

        if not torrentRecords:
            continue

        filteredTorrents = TorrentFilterController.filterTorrents(torrentRecords, mediaInfoRecord)
        logging.info(f"{len(torrentRecords)} torrents filtered down to {len(filteredTorrents)}")

        if not filteredTorrents:
            logging.info("No torrents survived the filter, trying the next query")
            continue

        # order torrents by number of seeders
        filteredSortedTorrents = sortTorrents(filteredTorrents)

        #if we have some results then break the loop and return the torrentRecords
        return filteredSortedTorrents

    return None


def reportAPIError(response, exception, sendEmail, extraErrorMessage=""):
    """
    reportAPIError reports an APIError offering configuration options in the reporting
    :param response: the response from the http request
    :param exception: the python exception that was thrown
    :param sendEmail: bool, whether to send an email for the error
    :param extraErrorMessage: any extra error info that should be added to the error reports
    :testedWith: None yet, must be tested
    :return: empty list
    """
    errorString = f"Problem with TPB API has occurred. {extraErrorMessage} \n"

    if response and response.content:
        errorString += f" Received: {response.content}"
    ErrorController.reportError(errorString, exception, sendEmail)
    return []


def queryAPI(queryTerm):
    """
    queryAPI queries the torrent api with the queryTerm passed in
    :param queryTerm: the text to be queried for
    :testedWith: None yet, must be tested
    :return: all matching torrents as torrentRecords
    """
    # create query url
    queryUrl = f"https://apibay.org/q.php?q={queryTerm}"
    response = None

    try:
        # make query and load json data
        response = requests.get(queryUrl)
        torrents = json.loads(response.content)

        # handle no response returned garcefully
        if len(torrents) == 1 and torrents[0]["id"] == "0":
            return []

        torrentRecords = []

        for torrentData in torrents:
            torrentRecords.append(TorrentRecord(torrentData["name"], torrentData["id"], torrentData["info_hash"], torrentData["seeders"], torrentData["leechers"]))

        return torrentRecords

    except (ChunkedEncodingError, JSONDecodeError) as exception:
        return reportAPIError(response, exception, True)

    except (ConnectionError) as exception:
        extraErrorString = "Torrent API seems down at the moment."
        return reportAPIError(response, exception, False, extraErrorString)

