#!/venv/bin/python

# external dependencies
from random import randint
import requests
import logging
import os
import json


def getTPBProxySites():
    proxyUrl = "https://piratebay-proxylist.se/api/v1/proxies"
    proxyResponse = dict(requests.get(proxyUrl).json())

    proxies = dict(proxyResponse["proxies"])
    domains = [ proxyRecord["domain"] for proxyRecord in proxies.values() ]
    return domains
    

def init(useProxyList):

    if useProxyList:
        sites = getTPBProxySites()

        if os.getenv('ENVIRONMENT') == "production":
            randomIndex = randint(1, len(sites))
        else:
            randomIndex = 0 # set random number for dev purposes
        
        #define global tpb object
        global thePirateBay
        chosenTPBBaseUrl = sites[randomIndex]
    else:
        chosenTPBBaseUrl = "https://thepiratebay33.org/"
    

def getTorrentRecords(queries):

    torrents = []
    # make query for the mediaInfoRecord, if none are found, try the next query format
    for queryStr in queries:
        torrents = queryAPI(queryStr)
        
        #logging
        logging.info(f"Torrent search performed for: '{queryStr}' - {len(torrents)} results.")

        #if we have some results then break the loop and return the torrentRecords
        if torrents:
            break
    
    return torrents


def queryAPI(queryTerm):
    
    # create query url
    queryUrl = f"https://apibay.org/q.php?q={queryTerm}"

    # make query and load json data
    response = requests.get(queryUrl)
    torrents = json.loads(response.content)

    for torrent in torrents:
        torrent["magnet"] = f"magnet:?xt=urn:btih:{torrent.get('info_hash')}&dn={torrent.get('name')}"

    return torrents