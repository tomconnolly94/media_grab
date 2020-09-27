#!/venv/bin/python

# pip dependencies
import requests
from bs4 import BeautifulSoup

def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    #TODO: detlink and href are out of date and must be updated
    listItems = soup.findAll("li", {"class": "list-entry"})

    itemInfo = [
        { 
            "itemText": listItem.find("span", {"class": "item-title"}).find("a").contents[0],
            "itemPageLink": listItem.find("span", {"class": "item-title"}).find("a")["href"],
            "itemMagnetLink": listItem.find("span", {"class": "item-icons"}).find("a")["href"]
        }
        for listItem in listItems
    ]

    return itemInfo
