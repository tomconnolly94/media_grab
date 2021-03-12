#!/venv/bin/python

# external dependencies
from random import randint
import requests
import logging
import os
import json
from requests.exceptions import ChunkedEncodingError
from json.decoder import JSONDecodeError

# internal dependencies
from controllers import TorrentFilterController, ErrorController

def sortTorrents(torrents):
    # order torrents by number of seeders
    return sorted(torrents, key=lambda torrent: -1 * int(torrent["seeders"]))


def getTPBProxySites():
    proxyUrl = "https://piratebay-proxylist.se/api/v1/proxies"
    proxyResponse = dict(requests.get(proxyUrl).json())

    proxies = dict(proxyResponse["proxies"])
    domains = [ proxyRecord["domain"] for proxyRecord in proxies.values() ]
    return domains
    

def getTorrentRecords(queries, mediaInfoRecord):

    # make query for the mediaInfoRecord, if none are found, try the next query format
    for queryStr in queries:
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

        for torrent in torrents:
            torrent["magnet"] = f"magnet:?xt=urn:btih:{torrent.get('info_hash')}&dn={torrent.get('name')}"

        return torrents
    except (JSONDecodeError, ChunkedEncodingError) as exception:
        ErrorController.reportError("Problem with TPB API has occurred.", exception, True)
        return []
