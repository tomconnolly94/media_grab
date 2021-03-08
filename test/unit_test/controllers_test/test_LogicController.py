# external dependencies
import unittest
import mock
from unittest.mock import call

# internal dependencies 
from controllers import LogicController
from data_types.ProgramMode import PROGRAM_MODE

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


    @mock.patch("interfaces.DownloadsInProgressFileInterface.findNewDownload")
    @mock.patch("logging.info")
    @mock.patch("interfaces.TPBInterface.getTorrentRecords")
    @mock.patch("controllers.LogicController.findMediaInfoRecord")
    def test_getMediaInfoRecordsWithTorrents(self, findMediaInfoRecordMock, getTorrentRecordsMock, loggingInfoMock, findNewDownloadMock):
        
        fakeMediaSearchQueries = {
            "fakeMediaInfoName1": ["fakeMediaInfoName1Query1", "fakeMediaInfoName1Query2", "fakeMediaInfoName1Query3"],
            "fakeMediaInfoName2": ["fakeMediaInfoName2Query1", "fakeMediaInfoName2Query2", "fakeMediaInfoName2Query3"],
            "fakeMediaInfoName3": ["fakeMediaInfoName3Query1", "fakeMediaInfoName3Query2", "fakeMediaInfoName3Query3"]
        }              

        fakeTorrentRecords = [
            { "name": "fakeTorrentTitle1", "magnet": "fakeTorrentMagnetLink1", "seeders": 4 },
            { "name": "fakeTorrentTitle2", "magnet": "fakeTorrentMagnetLink2", "seeders": 6 },
            { "name": "fakeTorrentTitle3", "magnet": "fakeTorrentMagnetLink3", "seeders": 8 },
            { "name": "fakeTorrentTitle4", "magnet": "fakeTorrentMagnetLink4", "seeders": 10 }
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
        findMediaInfoRecordMock.side_effect = fakeMediaInfoRecords
        getTorrentRecordsMock.return_value = fakeTorrentRecords
        findNewDownloadMock.side_effect = ["fakeTorrentTitle1", None, "fakeTorrentTitle3"]

        # expected outputs
        #fakeMediaInfoRecords[0]["magnet"]
        expectedOutputMediaInfoRecords = [
            {
                'magnet': 'fakeTorrentMagnetLink1', 
                'name': 'fakeMediaInfoName1', 
                'torrentName': 'fakeTorrentTitle1',
                'typeSpecificData': 
                {
                    'latestEpisode': 1, 
                    'latestSeason': 1
                }
            },
            {
                'magnet': 'fakeTorrentMagnetLink3', 
                'name': 'fakeMediaInfoName3', 
                'torrentName': 'fakeTorrentTitle3',
                'typeSpecificData': 
                {
                    'latestEpisode': 1, 
                    'latestSeason': 1
                }
            }
        ]

        actualOutputMediaInfoRecords = LogicController.getMediaInfoRecordsWithTorrents(fakeMediaSearchQueries, fakeMediaInfoRecords)

        # asserts
        self.assertEqual(expectedOutputMediaInfoRecords, actualOutputMediaInfoRecords)
        findMediaInfoRecordCalls = [
            call(fakeMediaInfoRecords, "fakeMediaInfoName1"),
            call(fakeMediaInfoRecords, "fakeMediaInfoName2"),
            call(fakeMediaInfoRecords, "fakeMediaInfoName3")
        ]
        findMediaInfoRecordMock.has_calls(findMediaInfoRecordCalls)

        getTorrentRecordsCalls = [
            call(fakeMediaSearchQueries["fakeMediaInfoName1"], fakeMediaInfoRecords[0]),
            call(fakeMediaSearchQueries["fakeMediaInfoName2"], fakeMediaInfoRecords[1]),
            call(fakeMediaSearchQueries["fakeMediaInfoName3"], fakeMediaInfoRecords[2])
        ]
        getTorrentRecordsMock.has_calls(getTorrentRecordsCalls)

        loggingInfoCalls = [
            call("Selected torrent: fakeMediaInfoName1 - seeders: 2"),
            call("Selected torrent: fakeMediaInfoName3 - seeders: 8"),
        ]
        loggingInfoMock.has_calls(loggingInfoCalls)

        fakeTorrentRecordsNames = [ torrent["name"] for torrent in fakeTorrentRecords ]        
        findNewDownloadCalls = [
            call(fakeTorrentRecordsNames),
            call(fakeTorrentRecordsNames),
        ]
        findNewDownloadMock.has_calls(findNewDownloadCalls)


    @mock.patch("controllers.NewTorrentController.onSuccessfulTorrentAdd")
    @mock.patch("interfaces.QBittorrentInterface.initTorrentDownload")
    @mock.patch("controllers.LogicController.getMediaInfoRecordsWithTorrents")
    @mock.patch("controllers.CompletedDownloadsController.auditDumpCompleteDir")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.getDownloadingItems")
    @mock.patch("controllers.QueryGenerationController.generateTVEpisodeQueries")
    @mock.patch("interfaces.MediaIndexFileInterface.loadMediaFile")
    def test_runProgramLogic(self, loadMediaFileMock, generateTVEpisodeQueriesMock, getDownloadingItemsMock, auditDumpCompleteDirMock, getMediaInfoRecordsWithTorrentsMock, initTorrentDownloadMock, onSuccessfulTorrentAddMock):
        
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
        activeMode = PROGRAM_MODE.TV_EPISODES
        fakeDownloadingItems =  ["downloadingItem1", "downloadingItem2"]

        # add fake magnet links
        for mediaInfoRecord in fakeMediaInfoRecords:
            mediaInfoRecordWithTorrent = dict(mediaInfoRecord)
            mediaInfoRecordWithTorrent["magnet"] = "fakeMagnetLink"
            fakeMediaInfoRecordsWithTorrents.append(mediaInfoRecordWithTorrent)

        
        # config mocks
        generateTVEpisodeQueriesMock.return_value = fakeMediaSearchQueries
        getDownloadingItemsMock.return_value = fakeDownloadingItems
        getMediaInfoRecordsWithTorrentsMock.side_effect = [fakeMediaInfoRecordsWithTorrents, []]
        initTorrentDownloadMock.side_effect = [True, True, True, None]
        loadMediaFileMock.return_value = fakeMediaInfoRecords

        LogicController.runProgramLogic(activeMode)

        
        # mock asserts
        generateTVEpisodeQueriesMock.assert_called_with(fakeMediaInfoRecords)
        getDownloadingItemsMock.assert_called_with(activeMode)
        auditDumpCompleteDirMock.assert_called_with(activeMode, fakeDownloadingItems)
        getMediaInfoRecordsWithTorrentsMock.assert_called_with(fakeMediaSearchQueries, fakeMediaInfoRecords)
        
        calls = [ call(fakeMediaInfoRecordsWithTorrents[0]), call(fakeMediaInfoRecordsWithTorrents[1]), call(fakeMediaInfoRecordsWithTorrents[2]) ]
        initTorrentDownloadMock.assert_has_calls(calls)

        calls = [ 
            call(fakeMediaInfoRecordsWithTorrents[0], "latestEpisode", "fakeMagnetLink", activeMode), 
            call(fakeMediaInfoRecordsWithTorrents[1],"latestEpisode", "fakeMagnetLink", activeMode) ]
        onSuccessfulTorrentAddMock.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
