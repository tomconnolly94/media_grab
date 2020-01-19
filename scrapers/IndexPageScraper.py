#!/venv/bin/python

#pip dependencies
import requests
import urllib.request
import time
from bs4 import BeautifulSoup

def scrape(url):
    print(url)
    # Connect to the URL
    response = requests.get(url)

    # Parse HTML and save to BeautifulSoup object¶
    soup = BeautifulSoup(response.text, "html.parser")

    print(soup.findAll("a", {"class": "detLink"}))

    anchors = soup.findAll("a", {"class": "detLink"})

    for anchor in anchors:
        print(anchors)
        print(anchor)
        print(anchor["href"])


    torrentMagnetLink = [ anchorTag["href"] for anchorTag in soup.findAll("a", {"class": "detLink"}) ]

    return torrentMagnetLink