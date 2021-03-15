import unittest
from controllers import QueryGenerationController

# external dependencies
from mock import mock

# internal dependencies
from dataTypes.MediaInfoRecord import MediaInfoRecord


class TestQueryGenerationController(unittest.TestCase):

    def test_generateEpisodeQueryGroup(self):

        mediaInfoRecord = MediaInfoRecord("rick and morty", 1, 1)

        name = mediaInfoRecord.getShowName()
        relevantSeason = mediaInfoRecord.getLatestSeasonNumber() 
        relevantEpisode= mediaInfoRecord.getLatestEpisodeNumber() + 1

        expectedQueries = [
            "\"rick and morty\" s01e02",
            "\"rick and morty\" s 1 e 2",
            "\"rick and morty\" season01episode02",
            "\"rick and morty\" season 1 episode 2"
        ]

        seasonQueryGroup = QueryGenerationController.generateTVEpisodeQueryGroup(name, relevantSeason, relevantEpisode)

        self.assertEqual(expectedQueries, seasonQueryGroup)


    @mock.patch("controllers.QueryGenerationController.generateTVEpisodeQueryGroup")
    def test_generateTVEpisodeQueries(self, generateTVEpisodeQueryGroupMock):

        # config fake data
        fakeMediaInfoRecords = [
            MediaInfoRecord("fakeMediaInfoShowName1", 1, 2),
            MediaInfoRecord("fakeMediaInfoShowName2", 3, 4),
            MediaInfoRecord("fakeMediaInfoShowName3", 5, 6)
        ]
        fakeQueries = ["fakeQueryUrl1", "fakeQueryUrl2", "fakeQueryUrl3"]

        # config mocks
        generateTVEpisodeQueryGroupMock.return_value = fakeQueries

        # run testable function
        actualQueryUrls = QueryGenerationController.generateTVEpisodeQueries(fakeMediaInfoRecords)

        # expected values
        expectedQueryUrls = {
            "fakeMediaInfoShowName1": fakeQueries,
            "fakeMediaInfoShowName2": fakeQueries,
            "fakeMediaInfoShowName3": fakeQueries,
        }

        # asserts
        self.assertEqual(expectedQueryUrls, actualQueryUrls)



if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon