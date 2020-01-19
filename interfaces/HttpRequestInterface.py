import requests
import json
import random

def getPBSite():

    proxyUrl = "https://piratebay-proxylist.se/api/v1/proxies"
    sites = list(requests.get(proxyUrl).json()["proxies"].values())
    #randomIndex = random.randint(0, len(sites) - 1)
    randomIndex = 0
    return sites[randomIndex]
    