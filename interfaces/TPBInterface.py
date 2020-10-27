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

    return [proxyRecord["domain"] for proxyRecord in list(proxyResponse["proxies"])]
    

def init():

    sites = getTPBProxySites()

    if os.getenv('ENVIRONMENT') == "production":
        randomIndex = randint(1, len(sites))
    else:
        randomIndex = 0 # set random number for dev purposes
    
    #define global tpb object
    global thePirateBay
    thePirateBay = TPB(sites[randomIndex]) # create a TPB object with domain
    
    
def query(queryTerm):
    return thePirateBay.search(queryTerm, category=CATEGORIES.VIDEO.TV_SHOWS).order(ORDERS.SEEDERS.ASC).page(1)
    

