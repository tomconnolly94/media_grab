#!/venv/bin/python


class MediaInfoRecord():


    def __init__(self, showName, latestSeasonNumber, latestEpisodeNumber, torrentRecord=None):
        self.__showName = showName
        self.__latestSeasonNumber = int(latestSeasonNumber)
        self.__latestEpisodeNumber = int(latestEpisodeNumber)
        self.__torrentRecord = torrentRecord

    ########## accessor functions start ##########

    def getMediaGrabId(self):
        return f"{self.__showName}--s{self.__latestSeasonNumber}e{self.__latestEpisodeNumber}"


    def getShowName(self):
        return self.__showName


    def getTorrentRecord(self):
        return self.__torrentRecord


    def getLatestSeasonNumber(self):
        return self.__latestSeasonNumber


    def getLatestEpisodeNumber(self):
        return self.__latestEpisodeNumber

    ########## accessor functions end ##########

    ########## mutator functions start ##########

    def setTorrentRecord(self, torrentRecord):
        self.__torrentRecord = torrentRecord


    def setLatestSeasonNumber(self, latestSeasonNumber):
        self.__latestSeasonNumber = latestSeasonNumber


    def setLatestEpisodeNumber(self, latestEpisodeNumber):
        self.__latestEpisodeNumber = latestEpisodeNumber

    ########## mutator functions end ##########

    def toDict(self):
        return {
            "name": self.__showName,
            "typeSpecificData": {
                "latestSeason": self.__latestSeasonNumber,
                "latestEpisode": self.__latestEpisodeNumber
            }
        }