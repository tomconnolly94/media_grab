#!/venv/bin/python

# external dependencies
from tmdbv3api import TMDb, TV, Season
import os

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
        tvShowSeason = season.details(tvShow.id, seasonIndex)

        if tvShowSeason:
            return len(tvShowSeason["episodes"])

    return None


if __name__== "__main__":
    init()
    print(getShowEpisodeCount("taskmaster", 1))
    pass
