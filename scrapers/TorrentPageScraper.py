#!/venv/bin/python

# pip dependencies
import requests
from bs4 import BeautifulSoup

def scrape(torrentPageURL):
    response = requests.get(torrentPageURL)
    soup = BeautifulSoup(response.text, "html.parser")
    anchor = soup.find("div", {"class": "download"}).find("a")
    return anchor["href"]