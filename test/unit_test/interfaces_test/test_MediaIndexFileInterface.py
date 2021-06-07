# external dependencies
import unittest
import mock
from mock import MagicMock

# internal dependencies
from interfaces import MediaIndexFileInterface
from dataTypes.MediaInfoRecord import MediaInfoRecord

class TestMediaIndexFileInterface(unittest.TestCase):

    def test_incrementSeason(self):

        # config inputs
        fakeMediaInfoRecords = [
            MediaInfoRecord("fakeMediaInfoName1", 1, 1),
            MediaInfoRecord("fakeMediaInfoName2", 5, 3),
            MediaInfoRecord("fakeMediaInfoName3", 9, 5)
        ]

        ##### Start test case 1 #####

        queryRecord = fakeMediaInfoRecords[0]

        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementSeason(
            fakeMediaInfoRecords, queryRecord)

        self.assertEqual(2, updatedMedia[0].getLatestSeasonNumber())
        self.assertEqual(1, updatedMedia[0].getLatestEpisodeNumber())
        self.assertEqual(5, updatedMedia[1].getLatestSeasonNumber())
        self.assertEqual(3, updatedMedia[1].getLatestEpisodeNumber())
        self.assertEqual(9, updatedMedia[2].getLatestSeasonNumber())
        self.assertEqual(5, updatedMedia[2].getLatestEpisodeNumber())

        # reset mocks
        updatedMedia[0].setLatestSeasonNumber(1)

        ##### End test case 1 #####

        ##### Start test case 2 #####

        queryRecord = fakeMediaInfoRecords[1]
        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementSeason(
            fakeMediaInfoRecords, queryRecord)

        self.assertEqual(1, updatedMedia[0].getLatestSeasonNumber())
        self.assertEqual(1, updatedMedia[0].getLatestEpisodeNumber())
        self.assertEqual(6, updatedMedia[1].getLatestSeasonNumber())
        self.assertEqual(1, updatedMedia[1].getLatestEpisodeNumber())
        self.assertEqual(9, updatedMedia[2].getLatestSeasonNumber())
        self.assertEqual(5, updatedMedia[2].getLatestEpisodeNumber())

        ##### End test case 2 #####

        ##### Start test case 3 #####

        nonExistentRecord = MediaInfoRecord("fakeMediaInfoName4", 1, 1)

        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementSeason(
            fakeMediaInfoRecords, nonExistentRecord)

        self.assertEqual(None, updatedMedia)

    @mock.patch("interfaces.TheMovieDatabaseInterface.getInstance")
    def test_incrementEpisode(self, theMovieDatabaseInterfaceGetInstanceMock):

        # config inputs
        fakeMediaInfoRecords = [
            MediaInfoRecord("fakeMediaInfoName1", 1, 1),
            MediaInfoRecord("fakeMediaInfoName2", 1, 3),
            MediaInfoRecord("fakeMediaInfoName3", 1, 1)
        ]

        # config mocks
        # create mock for instance
        theMovieDatabaseInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        theMovieDatabaseInterfaceGetInstanceMock.return_value = theMovieDatabaseInterfaceInstanceMock
        theMovieDatabaseInterfaceInstanceMock.getShowEpisodeCount.return_value = 3

        ##### Start test case 1 #####

        queryRecord = fakeMediaInfoRecords[0]

        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementEpisode(
            fakeMediaInfoRecords, queryRecord)

        self.assertEqual(1, updatedMedia[0].getLatestSeasonNumber())
        self.assertEqual(2, updatedMedia[0].getLatestEpisodeNumber())
        self.assertEqual(1, updatedMedia[1].getLatestSeasonNumber())
        self.assertEqual(3, updatedMedia[1].getLatestEpisodeNumber())
        self.assertEqual(1, updatedMedia[2].getLatestSeasonNumber())
        self.assertEqual(1, updatedMedia[2].getLatestEpisodeNumber())

        # reset mock
        updatedMedia[0].setLatestEpisodeNumber(1)

        ##### End test case 1 #####

        ##### Start test case 2 #####

        queryRecord = fakeMediaInfoRecords[1]
        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementEpisode(
            fakeMediaInfoRecords, queryRecord)

        self.assertEqual(1, updatedMedia[0].getLatestSeasonNumber())
        self.assertEqual(1, updatedMedia[0].getLatestEpisodeNumber())
        self.assertEqual(2, updatedMedia[1].getLatestSeasonNumber())
        self.assertEqual(1, updatedMedia[1].getLatestEpisodeNumber())
        self.assertEqual(1, updatedMedia[2].getLatestSeasonNumber())
        self.assertEqual(1, updatedMedia[2].getLatestEpisodeNumber())

        ##### End test case 2 #####

        ##### Start test case 3 #####

        nonExistentRecord = MediaInfoRecord("fakeMediaInfoName4", 1, 1)

        # called testable method
        updatedMedia = MediaIndexFileInterface.incrementEpisode(
            fakeMediaInfoRecords, nonExistentRecord)

        self.assertEqual(None, updatedMedia)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
