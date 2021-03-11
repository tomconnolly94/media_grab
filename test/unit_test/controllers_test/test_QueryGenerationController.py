import unittest
from controllers import QueryGenerationController

class TestQueryGenerationController(unittest.TestCase):

    def test_generateEpisodeQueryGroup(self):

        mediaInfo = {
            "name": "rick and morty",
            "typeSpecificData": {
                "latestSeason": 1,
                "latestEpisode": 1
            }
        }

        name = mediaInfo["name"]
        relevantSeason = int(mediaInfo["typeSpecificData"]["latestSeason"]) 
        relevantEpisode= int(mediaInfo["typeSpecificData"]["latestEpisode"]) + 1

        expectedQueries = [
            "\"rick and morty\" s01e02",
            "\"rick and morty\" s 1 e 2",
            "\"rick and morty\" season01episode02",
            "\"rick and morty\" season 1 episode 2"
        ]

        seasonQueryGroup = QueryGenerationController.generateTVEpisodeQueryGroup(name, relevantSeason, relevantEpisode)

        self.assertEqual(expectedQueries, seasonQueryGroup)

if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon