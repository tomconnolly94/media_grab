#!/venv/bin/python

# external dependencies
import enum

class TorrentCategory(enum.Enum):
   TV_EPISODE = 1
   TV_SEASON = 2


class TorrentRecord():

    def __init__(self, name, torrentId, infoHash, seeders, leechers=None, category=None):
        self.__name = name
        self.__torrentId = torrentId
        self.__infoHash = infoHash
        self.__seeders = seeders
        self.__leechers = leechers
        self.__category = category


    def getMagnet(self):
        return f"magnet:?xt=urn:btih:{self.__infoHash}&dn={self.__name}"

    def getName(self):
        return self.__name

    def getId(self):
        return self.__name

    def getSeeders(self):
        return self.__seeders

    def getInfoHash(self):
        return self.__infoHash

    def getCategory(self):
        return self.__category

    def setCategory(self, category):
        self.__category = category
