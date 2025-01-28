#!/venv/bin/python

# external dependencies
import enum


class TorrentCategory(enum.Enum):
    TV_EPISODE = 1
    TV_SEASON = 2


class TorrentRecord:

    def __init__(
        self,
        name: str,
        torrentId: str,
        infoHash: str,
        size: int,
        seeders: int,
        leechers=None,
        category=None,
    ):
        self._name = name
        self._torrentId = torrentId
        self._infoHash = infoHash
        self._size = int(size)
        self._seeders = int(seeders)
        self._leechers = leechers
        self._category = category

    def getMagnet(self):
        return f"magnet:?xt=urn:btih:{self._infoHash}&dn={self._name}"

    def getName(self):
        return self._name

    def getId(self):
        return self._torrentId

    def getSize(self):
        return self._size

    def getSeeders(self):
        return self._seeders

    def getInfoHash(self):
        return self._infoHash

    def getCategory(self):
        return self._category

    def setCategory(self, category):
        self._category = category
