#!/venv/bin/python


class MediaInfoRecord():

    def __init__(self, showName, latestSeasonNumber, latestEpisodeNumber, blacklistTerms=[], torrentRecord=None, mediaSearchQueries=None):
        self.__showName = showName
        self.__latestSeasonNumber = int(latestSeasonNumber)
        self.__latestEpisodeNumber = int(latestEpisodeNumber)
        self.__torrentRecord = torrentRecord
        self.__mediaSearchQueries = mediaSearchQueries
        self.__blacklistTerms = blacklistTerms

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


    def getMediaSearchQueries(self):
        return self.__mediaSearchQueries


    def getBlacklistTerms(self):
        return self.__blacklistTerms

    ########## accessor functions end ##########

    ########## mutator functions start ##########

    def setTorrentRecord(self, torrentRecord):
        self.__torrentRecord = torrentRecord


    def setLatestSeasonNumber(self, latestSeasonNumber):
        self.__latestSeasonNumber = latestSeasonNumber


    def setLatestEpisodeNumber(self, latestEpisodeNumber):
        self.__latestEpisodeNumber = latestEpisodeNumber


    def setMediaSearchQueries(self, queries):
        self.__mediaSearchQueries = queries


    ########## mutator functions end ##########

    def toDict(self):
        return {
            "name": self.__showName,
            "typeSpecificData": {
                "latestSeason": self.__latestSeasonNumber,
                "latestEpisode": self.__latestEpisodeNumber
            },
            "blacklistTerms": self.__blacklistTerms
        }
