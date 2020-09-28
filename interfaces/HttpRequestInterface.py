import requests
import json
import random

def getPBSite():

    proxyUrl = "https://piratebay-proxylist.se/api/v1/proxies"
    proxyResponse = dict(requests.get(proxyUrl).json())

    sites = [proxyRecord["domain"] for proxyRecord in list(proxyResponse["proxies"])]
    randomIndex = 0
    return sites[randomIndex]
    