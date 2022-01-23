#!/venv/bin/python

# external dependencies
from tmdbv3api import TMDb, TV
import os
import json

# internal dependencies

# implement singleton pattern
global theMovieDatabaseInterface
theMovieDatabaseInterface = None


def getInstance():
    """
    getInstance creates/accesses the singleton instance of TheMovieDatabaseInterface
    :testedWith: None - glue code
    :return: singleton instance of TheMovieDatabaseInterface
    """
    global theMovieDatabaseInterface
    if not theMovieDatabaseInterface:
        theMovieDatabaseInterface = TheMovieDatabaseInterface()
    return theMovieDatabaseInterface


class TheMovieDatabaseInterface():

    def __init__(self):
        """
        __init__ initialises a TheMovieDatabaseInterface, creating the TMDb client and setting the api key
        :testedWith: None yet - must be tested eventually
        :return: None
        """
        tmdbApiKey = os.getenv('THE_MOVIE_DATABASE_API_KEY')


        if tmdbApiKey:
            self.tmdbClient = TMDb() 
            self.tmdbClient.api_key = tmdbApiKey


    def addShowReccomendationsToMediaIndexContent(self, mediaIndexFileContent):
        """
        getShowReccomendation returns the number of episodes for a season of a show referenced by the params tvShowName and seasonIndex
        :param tvShowName the name of the tv show for which the show episode count is requested
        :param seasonIndex the season number for which the show episode count is requested
        :testedWith: None yet - must be tested eventually
        :return: number of episodes
        """
        
        mediaIndexFileContent = json.loads(mediaIndexFileContent)

        for mediaIndexRecord in mediaIndexFileContent["media"]:
            tv = TV()
            tvShows = tv.search(mediaIndexRecord["name"])
 
            if tvShows:
                tvShow = tvShows[0]
                similarShows = tv.similar(tvShow.id)

                similarShowTitles = [ show["original_name"] for show in similarShows ]
            
                mediaIndexRecord["similarShows"] = similarShowTitles

        return mediaIndexFileContent
