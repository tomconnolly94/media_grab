# external dependencies
import unittest
import mock

# internal dependencies
from interfaces import MediaIndexFileInterface

class TestMediaIndexFileInterface(unittest.TestCase):

    @mock.patch("interfaces.TheMovieDatabaseInterface.getShowEpisodeCount")
    def test_incrementEpisode(self, getShowEpisodeCountMock):

        # config inputs        
        fakeMediaInfoRecords = [
            {
                "name": "fakeMediaInfoName1",
                "typeSpecificData": { "latestSeason": "1", "latestEpisode": "1" }
            },
            {
                "name": "fakeMediaInfoName2",
                "typeSpecificData": { "latestSeason": "1", "latestEpisode": "3" }
            },
            {
                "name": "fakeMediaInfoName3",
                "typeSpecificData": { "latestSeason": "1", "latestEpisode": "1" }
            }
        ]

        # config mocks
        getShowEpisodeCountMock.return_value = 3


        ##### Start test case 1 #####

        queryRecord = fakeMediaInfoRecords[0]

        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementEpisode(fakeMediaInfoRecords, queryRecord)

        self.assertEqual("1", updatedMedia[0]["typeSpecificData"]["latestSeason"])
        self.assertEqual("2", updatedMedia[0]["typeSpecificData"]["latestEpisode"])

        ##### End test case 1 #####

        ##### Start test case 2 #####

        queryRecord = fakeMediaInfoRecords[1]
        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementEpisode(fakeMediaInfoRecords, queryRecord)

        self.assertEqual("2", updatedMedia[1]["typeSpecificData"]["latestSeason"])
        self.assertEqual("1", updatedMedia[1]["typeSpecificData"]["latestEpisode"])

        ##### End test case 2 #####
        
        ##### Start test case 3 #####

        nonExistentRecord = {
            "name": "fakeMediaInfoName4",
            "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
        }

        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementEpisode(fakeMediaInfoRecords, nonExistentRecord)

        self.assertEqual(None, updatedMedia)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
