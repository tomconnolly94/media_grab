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
    global theMovieDatabaseInterface
    if not theMovieDatabaseInterface:
        theMovieDatabaseInterface = TheMovieDatabaseInterface()
    return theMovieDatabaseInterface


class TheMovieDatabaseInterface():

    def __init__(self):
        self.tmdbClient = TMDb()
        self.tmdbClient.api_key = os.getenv("THE_MOVIE_DATABASE_API_KEY")


    def getShowSeasonCount(self, tvShowName):
        tv = TV()
        tvShows = tv.search(tvShowName)

        if tvShows:
            tvShow = tvShows[0]
            tvShowDetails = tv.details(tvShow.id)
            if tvShowDetails:
                return tvShowDetails["number_of_seasons"]


    def getShowEpisodeCount(self, tvShowName, seasonIndex):
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


if __name__== "__main__":
    theMovieDatabaseInterface = TheMovieDatabaseInterface()
    print(theMovieDatabaseInterface.getShowEpisodeCount("planet earth", 2))
    pass
