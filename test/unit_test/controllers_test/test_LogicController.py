#external dependencies
import unittest
import mock
from unittest.mock import call

# internal dependencies 
from controllers import LogicController
from data_types.ProgramMode import ProgramMode

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


    @mock.patch("logging.info")
    @mock.patch("controllers.TorrentFilterController.filterSeasonTorrents")
    @mock.patch("controllers.LogicController.findMediaInfoRecord")
    @mock.patch("interfaces.TPBInterface.getTorrentRecords")
    def test_getMediaInfoRecordsWithTorrents(self, getTorrentRecordsMock, findMediaInfoRecordMock, filterSeasonTorrentsMock, loggingInfoMock):
        
        fakeMediaSearchQueries = {
            "fakeMediaInfoName1": ["fakeMediaInfoName1Query1", "fakeMediaInfoName1Query2", "fakeMediaInfoName1Query3"],
            "fakeMediaInfoName2": ["fakeMediaInfoName2Query1", "fakeMediaInfoName2Query2", "fakeMediaInfoName2Query3"],
            "fakeMediaInfoName3": ["fakeMediaInfoName3Query1", "fakeMediaInfoName3Query2", "fakeMediaInfoName3Query3"]
        }

        class TorrentRecordMock(object):
            def __init__(self, title, magnetLink):
                self.title = title
                self.magnet_link = magnetLink                

        fakeTorrentRecords = [
            TorrentRecordMock("fakeTorrentTitle1", "fakeTorrentMagnetLink1"),
            TorrentRecordMock("fakeTorrentTitle2", "fakeTorrentMagnetLink2"),
            TorrentRecordMock("fakeTorrentTitle3", "fakeTorrentMagnetLink3"),
            TorrentRecordMock("fakeTorrentTitle4", "fakeTorrentMagnetLink4")
        ]

        fakeMediaInfoRecords = [
            {
                "name": "fakeMediaInfoName1",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "fakeMediaInfoName2",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "fakeMediaInfoName3",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            }
        ]

        # configure mocks
        getTorrentRecordsMock.return_value = fakeTorrentRecords
        findMediaInfoRecordMock.side_effect = [fakeMediaInfoRecords[0], fakeMediaInfoRecords[1], fakeMediaInfoRecords[2]]
        filterSeasonTorrentsMock.side_effect = [["fakeTorrentTitle1", "fakeTorrentTitle3"], [], ["fakeTorrentTitle3"]]

        # expected outputs
        #fakeMediaInfoRecords[0]["magnet"]
        expectedOutputMediaInfoRecords = [
            {'magnet_link': 'fakeTorrentMagnetLink1', 'name': 'fakeMediaInfoName1', 'typeSpecificData': {'latestEpisode': 1, 'latestSeason': 1}},
            {'magnet_link': 'fakeTorrentMagnetLink3', 'name': 'fakeMediaInfoName3', 'typeSpecificData': {'latestEpisode': 1, 'latestSeason': 1}}
        ]

        actualOutputMediaInfoRecords = LogicController.getMediaInfoRecordsWithTorrents(fakeMediaSearchQueries, fakeMediaInfoRecords)

        # mock asserts
        calls = [ call(f'torrentInfo: {fakeTorrentRecords[0].magnet_link}'), call(f'torrentInfo: {fakeTorrentRecords[2].magnet_link}') ]
        loggingInfoMock.assert_has_calls(calls)

        #TODO: finish implementation of this test function
        self.assertEqual(expectedOutputMediaInfoRecords, actualOutputMediaInfoRecords)


    @mock.patch("controllers.NewTorrentController.onSuccessfulTorrentAdd")
    @mock.patch("controllers.BittorrentController.initTorrentDownload")
    @mock.patch("controllers.LogicController.getMediaInfoRecordsWithTorrents")
    @mock.patch("controllers.QueryGenerationController.generateTVSeasonQueries")
    def test_runProgramLogic(self, generateTVSeasonQueriesMock, getMediaInfoRecordsWithTorrentsMock, initTorrentDownloadMock, onSuccessfulTorrentAddMock):
        
        fakeMediaSearchQueries = {
            "fakeMediaInfoName1": ["fakeMediaInfoName1Query1", "fakeMediaInfoName1Query2", "fakeMediaInfoName1Query3"],
            "fakeMediaInfoName2": ["fakeMediaInfoName2Query1", "fakeMediaInfoName2Query2", "fakeMediaInfoName2Query3"],
            "fakeMediaInfoName3": ["fakeMediaInfoName3Query1", "fakeMediaInfoName3Query2", "fakeMediaInfoName3Query3"]
        }
        
        # config fake inputs
        fakeMediaInfoRecords = [
            {
                "name": "fakeMediaInfoName1",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "fakeMediaInfoName2",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "fakeMediaInfoName3",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            }
        ]

        # config fake data
        fakeMediaSearchQueries = ["fakeMediaSearchQuery1", "fakeMediaSearchQuery2", "fakeMediaSearchQuery3"]
        fakeMediaInfoRecordsWithTorrents = []

        # add fake magnet links
        for mediaInfoRecord in fakeMediaInfoRecords:
            mediaInfoRecordWithTorrent = dict(mediaInfoRecord)
            mediaInfoRecordWithTorrent["magnet_link"] = "fakeMagnetLink"
            fakeMediaInfoRecordsWithTorrents.append(mediaInfoRecordWithTorrent)

        
        # config mocks
        generateTVSeasonQueriesMock.return_value = fakeMediaSearchQueries
        getMediaInfoRecordsWithTorrentsMock.return_value = fakeMediaInfoRecordsWithTorrents
        initTorrentDownloadMock.side_effect = [True, True, True, None]

        LogicController.runProgramLogic(fakeMediaInfoRecords, ProgramMode.TV)

        
        # mock asserts
        generateTVSeasonQueriesMock.assert_called_with(fakeMediaInfoRecords)
        getMediaInfoRecordsWithTorrentsMock.assert_called_with(fakeMediaSearchQueries, fakeMediaInfoRecords)
        
        calls = [ call("fakeMagnetLink"), call("fakeMagnetLink"), call("fakeMagnetLink") ]
        initTorrentDownloadMock.assert_has_calls(calls)

        calls = [ call(fakeMediaInfoRecordsWithTorrents[0], "latestSeason", "fakeMagnetLink"), call(fakeMediaInfoRecordsWithTorrents[1],"latestSeason", "fakeMagnetLink") ]
        onSuccessfulTorrentAddMock.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
