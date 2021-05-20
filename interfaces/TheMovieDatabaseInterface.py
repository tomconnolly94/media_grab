#!/venv/bin/python

# external dependencies
from tmdbv3api import TMDb, TV, Season
from tmdbv3api.exceptions import TMDbException
import os

# internal dependencies
from controllers import ErrorController

global theMovieDatabaseInterface
theMovieDatabaseInterface = None

# implement singleton pattern


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
        self.tmdbClient = TMDb()
        self.tmdbClient.api_key = os.getenv("THE_MOVIE_DATABASE_API_KEY")

    def getShowSeasonCount(self, tvShowName):
        """
        getShowSeasonCount returns the number of seasons for a show referenced by the param tvShowName
        :param tvShowName the name of the tv show for which the show season count is requested
        :testedWith: None yet - must be tested eventually
        :return: number of seasons
        """
        tv = TV()
        tvShows = tv.search(tvShowName)

        if tvShows:
            tvShow = tvShows[0]
            tvShowDetails = tv.details(tvShow.id)
            if tvShowDetails:
                return tvShowDetails["number_of_seasons"]

    def getShowEpisodeCount(self, tvShowName, seasonIndex):
        """
        getShowEpisodeCount returns the number of episodes for a season of a show referenced by the params tvShowName and seasonIndex
        :param tvShowName the name of the tv show for which the show episode count is requested
        :param seasonIndex the season number for which the show episode count is requested
        :testedWith: None yet - must be tested eventually
        :return: number of episodes
        """
        tv = TV()
        tvShows = tv.search(tvShowName)

        if tvShows:
            tvShow = tvShows[0]
            season = Season()

            try:
                tvShowSeason = season.details(tvShow.id, seasonIndex)

                if tvShowSeason:
                    return len(tvShowSeason["episodes"])

            except TMDbException:
                ErrorController.reportError(message=f"Failed to get a result from The Movie Database for '{tvShowName}' for Season {seasonIndex}", exception=None, sendEmail=True)

        return None
