#!/venv/bin/python

# external dependencies
from random import randint
import requests
import logging
import os

# internal dependencies
from tpb import TPB, CATEGORIES, ORDERS

def init():
    proxyUrl = "https://piratebay-proxylist.se/api/v1/proxies"
    proxyResponse = dict(requests.get(proxyUrl).json())

    sites = [proxyRecord["domain"] for proxyRecord in list(proxyResponse["proxies"])]

    if os.getenv('ENVIRONMENT') == "production":
        randomIndex = randint(1, len(sites))
    else:
        randomIndex = 0 # set random number for dev purposes
    
    #define global tpb object
    global thePirateBay
    thePirateBay = TPB(sites[randomIndex]) # create a TPB object with domain
    
def query(queryTerm):
    # search for 'public domain' in 'movies' category
    return thePirateBay.search(queryTerm, category=CATEGORIES.VIDEO.TV_SHOWS).order(ORDERS.SEEDERS.ASC).page(1)
    
