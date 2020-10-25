#external dependencies
import unittest
import mock

# internal dependencies 
from controllers import LogicController

class TestLogicController(unittest.TestCase):


    def test_findMediaInfoRecord(self):

        relevantMediaInfoRecord = {
            "name": "infoRecordFakeName1",
            "typeSpecificData": {
                "latestSeason": 1,
                "latestEpisode": 1
            }
        }

        mediaInfoRecords = [
            {
                "name": "infoRecordFakeName2",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "infoRecordFakeName3",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "infoRecordFakeName4",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "infoRecordFakeName5",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            relevantMediaInfoRecord
        ]

        actualMediaInfoRecord = LogicController.findMediaInfoRecord(mediaInfoRecords, relevantMediaInfoRecord["name"])

        self.assertEqual(relevantMediaInfoRecord, actualMediaInfoRecord)


    @mock.patch("interfaces.TPBInterface.query")
    def test_getTorrentRecords(self, queryMock):
        TPBQueryResponses = [None, ["torrent1", "torrent2", "torrent3"]]
        queryMock.side_effect = TPBQueryResponses
        queries = ["fakeQueryString1", "fakeQueryString2", "fakeQueryString3"]

        torrentRecords = LogicController.getTorrentRecords(queries)

        self.assertEqual(TPBQueryResponses[1], torrentRecords)


    @mock.patch("controllers.LogicController.getTorrentRecords")
    @mock.patch("controllers.TorrentFilterController.filterSeasonTorrents")
    def test_getMediaInfoRecordsWithTorrents(self, filterSeasonTorrentsMock, getTorrentRecordsMock):
        
        fakeMediaSearchQueries = {
            "fakeMediaInfoName1": ["fakeMediaInfoName1Query1", "fakeMediaInfoName1Query2", "fakeMediaInfoName1Query3"],
            "fakeMediaInfoName2": ["fakeMediaInfoName2Query1", "fakeMediaInfoName2Query2", "fakeMediaInfoName2Query3"] 
        }

        fakeMediaInfoRecords = [
            {
                "name": "infoRecordFakeName2",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "infoRecordFakeName3",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "infoRecordFakeName4",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "infoRecordFakeName5",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
        ]

        actualMediaInfoRecords = LogicController.getMediaInfoRecordsWithTorrents(fakeMediaSearchQueries, fakeMediaInfoRecords)

        #TODO: finish implementation of this test function
        self.assertTrue(True)




if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
