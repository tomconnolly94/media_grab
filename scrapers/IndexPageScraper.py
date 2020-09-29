#!/venv/bin/python

# pip dependencies
import requests
from bs4 import BeautifulSoup

def scrape(url):
    response = requests.get(url)

    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        print(response.text)
        
        listItems = soup.findAll("li", {"class": "list-entry"})

        # itemInfo = [
        #     { 
        #         "itemText": listItem.find("span", {"class": "item-title"}).find("a").contents[0],
        #         "itemPageLink": listItem.find("span", {"class": "item-title"}).find("a")["href"],
        #         "itemMagnetLink": listItem.find("span", {"class": "item-icons"}).find("a")["href"]
        #     }
        #     for listItem in listItems
        # ]

        itemInfo = []

        for listItem in listItems:

            listItemText = listItem.find("span", {"class": "item-title"}).find("a").contents[0]
            listItemPageLink = listItem.find("span", {"class": "item-title"}).find("a").contents[0]
            listItemMagnetLink = listItem.find("span", {"class": "item-title"}).find("a").contents[0]

            itemInfo.append({ 
                "itemText": listItem.find("span", {"class": "item-title"}).find("a").contents[0],
                "itemPageLink": listItem.find("span", {"class": "item-title"}).find("a")["href"],
                "itemMagnetLink": listItem.find("span", {"class": "item-icons"}).find("a")["href"]
            })

        return itemInfo
    return []
