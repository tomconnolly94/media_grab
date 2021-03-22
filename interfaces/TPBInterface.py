#!/venv/bin/python

# external dependencies
import requests
import logging
import json
from requests.exceptions import ChunkedEncodingError
from json.decoder import JSONDecodeError

# internal dependencies
from controllers import TorrentFilterController, ErrorController
from dataTypes.TorrentRecord import TorrentRecord

def sortTorrents(torrents):
    # order torrents by number of seeders
    return sorted(torrents, key=lambda torrent: -1 * torrent.getSeeders())


def getTorrentRecords(mediaInfoRecord):

    # make query for the mediaInfoRecord, if none are found, try the next query format
    for queryStr in mediaInfoRecord.getMediaSearchQueries():
        torrentRecords = queryAPI(queryStr)
        
        #logging
        logging.info(f"Torrent search performed for: '{queryStr}' - {len(torrentRecords)} results.")

        if not torrentRecords:
            continue

        filteredTorrents = TorrentFilterController.filterEpisodeTorrents(torrentRecords, mediaInfoRecord)
        logging.info(f"{len(torrentRecords)} torrents filtered down to {len(filteredTorrents)}")

        if not filteredTorrents:
            logging.info("No torrents survived the filter, trying the next query")
            continue

        # order torrents by number of seeders
        filteredSortedTorrents = sortTorrents(filteredTorrents)

        #if we have some results then break the loop and return the torrentRecords
        return filteredSortedTorrents

    return None


def queryAPI(queryTerm):
    
    # create query url
    queryUrl = f"https://apibay.org/q.php?q={queryTerm}"

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

    except (JSONDecodeError, ChunkedEncodingError) as exception:
        responsePrintout = response.content if response.content else response
        ErrorController.reportError(f"Problem with TPB API has occurred. Recevied: {response.content}", exception, True)
        return []
