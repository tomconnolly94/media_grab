import requests
import json
import random

def getPBSite():

    proxyUrl = "https://piratebay-proxylist.se/api/v1/proxies"
    sites = requests.get(proxyUrl).json()["proxies"]
    randomIndex = random.randint(0, len(sites))

    return sites[randomIndex]
    