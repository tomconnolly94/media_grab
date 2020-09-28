import unittest
from controllers import DataOrganisationController

class TestDataOrganisationController(unittest.TestCase):

    def test_generateSingleMediaQueryUrls(self):

        mediaInfo = {
            "name": "rick and morty",
            "typeSpecificData": {
                "latestSeason": 1
            }
        }



        fakePbDomain = "fakeDomain.net"
        name = mediaInfo["name"]
        relevantSeason = int(mediaInfo["typeSpecificData"]["latestSeason"]) + 1

        expectedQueryUrls = [
            "https://fakeDomain.net/search.php?q=rick+and+morty+s02&cat=0&page=0&orderby=99",
            "https://fakeDomain.net/search.php?q=rick+and+morty+season02&cat=0&page=0&orderby=99",
            "https://fakeDomain.net/search.php?q=rick+and+morty+season+02&cat=0&page=0&orderby=99",
        ]


        seasonIndexQueryURLs = DataOrganisationController.generateSeasonIndexQueryUrls(name, relevantSeason, fakePbDomain)

        self.assertEqual(expectedQueryUrls, seasonIndexQueryURLs)

if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon