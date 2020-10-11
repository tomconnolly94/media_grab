from tpb import TPB
from tpb import CATEGORIES, ORDERS


def setDomain(domain):
    #define global tpb object
    global thPirateBay
    thPirateBay = TPB(domain) # create a TPB object with domain
    
def query(queryTerm):
    # search for 'public domain' in 'movies' category
    searchResult = thPirateBay.search(queryTerm, category=CATEGORIES.VIDEO.TV_SHOWS)

    
    # print all torrent descriptions
    for torrent in searchResult:
        print(torrent.info)

