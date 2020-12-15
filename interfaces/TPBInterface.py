#!/venv/bin/python

# external dependencies
from random import randint
import requests
import logging
import os

# internal dependencies
from tpb import TPB, CATEGORIES, ORDERS


def getTPBProxySites():
    proxyUrl = "https://piratebay-proxylist.se/api/v1/proxies"
    proxyResponse = dict(requests.get(proxyUrl).json())

    proxies = dict(proxyResponse["proxies"])
    domains = [ proxyRecord["domain"] for proxyRecord in proxies.values() ]
    return domains
    

def init():
    useProxyList = False

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
        chosenTPBBaseUrl = "https://thepiratebay0.org/"
    thePirateBay = TPB(chosenTPBBaseUrl) # create a TPB object with domain
    
    
def query(queryTerm):
    return thePirateBay.search(queryTerm, category=CATEGORIES.VIDEO.TV_SHOWS).order(ORDERS.SEEDERS.ASC).page(1)
    

def getTorrentRecords(queries):

    torrentRecords = []
    # make query for the mediaInfoRecord, if none are found, try the next query format
    for queryStr in queries:
        torrentQuery = query(queryStr)

        # this is necessary to force the TPB to make the http requests here and save the value
        # if this is not done then every time the torrentQuery object is used a new http 
        # request is made
        for torrent in torrentQuery:
            torrentRecords.append(torrent)
        
        #logging
        logging.info(f"Torrent search performed for: '{queryStr}' - {len(torrentRecords)} results.")

        #if we have some results then break the loop and return the torrentRecords
        if torrentRecords:
            break
    
    return torrentRecords
