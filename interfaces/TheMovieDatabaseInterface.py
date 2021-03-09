#!/venv/bin/python

# external dependencies
from tmdbv3api import TMDb, TV, Season
from tmdbv3api.exceptions import TMDbException
import os

# internal dependencies
from controllers import ErrorController

global tmdb

def init():
    tmdb = TMDb()
    tmdb.api_key = os.getenv("THE_MOVIE_DATABASE_API_KEY")


def getShowSeasonCount(tvShowName):
    tv = TV()
    tvShows = tv.search(tvShowName)

    if tvShows:
        tvShow = tvShows[0]
        tvShowDetails = tv.details(tvShow.id)
        if tvShowDetails:
            return tvShowDetails["number_of_seasons"]


def getShowEpisodeCount(tvShowName, seasonIndex):
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
    init()
    print(getShowEpisodeCount("planet earth", 2))
    pass
