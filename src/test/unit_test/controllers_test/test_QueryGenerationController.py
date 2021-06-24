import unittest

# external dependencies
from mock import mock

# internal dependencies
from src.controllers import QueryGenerationController
from src.dataTypes.MediaInfoRecord import MediaInfoRecord


class TestQueryGenerationController(unittest.TestCase):

    @mock.patch("controllers.QueryGenerationController.generateTVSeasonQuery")
    @mock.patch("controllers.QueryGenerationController.generateTVEpisodeQueryGroup")
    def test_addTVEpisodeQueriesToMediaInfoRecords(self, generateTVEpisodeQueryGroupMock, generateTVSeasonQueryMock):

        # config fake data
        fakeMediaInfoRecords = [
            MediaInfoRecord("fakeMediaInfoShowName1", 1, 2),
            MediaInfoRecord("fakeMediaInfoShowName2", 3, 4),
            MediaInfoRecord("fakeMediaInfoShowName3", 5, 6),
            MediaInfoRecord("fakeMediaInfoShowName4", 1, 1)
        ]
        fakeEpisodeQueries = ["fakeEpisodeQueryUrl1",
                              "fakeEpisodeQueryUrl2", "fakeEpisodeQueryUrl3"]
        fakeSeasonQueries = ["fakeSeasonQueryUrl1",
                             "fakeSeasonQueryUrl2", "fakeSeasonQueryUrl3"]

        # config mocks
        generateTVEpisodeQueryGroupMock.return_value = fakeEpisodeQueries
        generateTVSeasonQueryMock.return_value = fakeSeasonQueries

        # run testable function
        QueryGenerationController.addTVEpisodeQueriesToMediaInfoRecords(
            fakeMediaInfoRecords)

        # expected values
        expectedQueryUrls = {
            "fakeMediaInfoShowName1": fakeEpisodeQueries,
            "fakeMediaInfoShowName2": fakeEpisodeQueries,
            "fakeMediaInfoShowName3": fakeEpisodeQueries,
            "fakeMediaInfoShowName4": fakeSeasonQueries + fakeEpisodeQueries
        }

        actualQueryUrls = {
            fakeMediaInfoRecord.getShowName(): fakeMediaInfoRecord.getMediaSearchQueries() for fakeMediaInfoRecord in fakeMediaInfoRecords
        }

        # asserts
        self.assertEqual(expectedQueryUrls, actualQueryUrls)


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


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
