#!/venv/bin/python

# pip dependencies
import requests
from bs4 import BeautifulSoup

def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return [ anchorTag["href"] for anchorTag in soup.findAll("a", {"class": "detLink"}) ]
