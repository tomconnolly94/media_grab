#!/venv/bin/python


class TorrentRecord():


    def __init__(self, name, torrentId, infoHash, seeders, leechers=None):
        self.__name = name
        self.__torrentId = torrentId
        self.__infoHash = infoHash
        self.__seeders = seeders
        self.__leechers = leechers


    def getMagnet(self):
        return f"magnet:?xt=urn:btih:{self.__infoHash}&dn={self.__name}"


    def getName(self):
        return self.__name


    def getId(self):
        return self.__name


    def getSeeders(self):
        return self.__seeders
