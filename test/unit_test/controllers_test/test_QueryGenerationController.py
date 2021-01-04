import unittest
from controllers import QueryGenerationController

class TestQueryGenerationController(unittest.TestCase):

    def test_generateSeasonQueryGroup(self):

        mediaInfo = {
            "name": "rick and morty",
            "typeSpecificData": {
                "latestSeason": 1
            }
        }

        name = mediaInfo["name"]
        relevantSeason = int(mediaInfo["typeSpecificData"]["latestSeason"]) + 1

        expectedQueries = [
            "rick and morty s02",
            "rick and morty s 2",
            "rick and morty season02",
            "rick and morty season 2"
        ]

        seasonQueryGroup = QueryGenerationController.generateTVSeasonQueryGroup(name, relevantSeason)

        self.assertEqual(expectedQueries, seasonQueryGroup)

if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon