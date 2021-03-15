# external dependencies
import unittest
import mock
from unittest.mock import call
from mock import MagicMock

# internal dependencies 
from controllers import LogicController
from dataTypes.ProgramMode import PROGRAM_MODE
from dataTypes.TorrentRecord import TorrentRecord
from dataTypes.MediaInfoRecord import MediaInfoRecord

class TestLogicController(unittest.TestCase):

    def test_findMediaInfoRecord(self):

        relevantMediaInfoRecord = MediaInfoRecord("infoRecordFakeName1", 1, 1)

        mediaInfoRecords = [
            MediaInfoRecord("infoRecordFakeName2", 1, 1),
            MediaInfoRecord("infoRecordFakeName3", 1, 1),
            MediaInfoRecord("infoRecordFakeName4", 1, 1),
            MediaInfoRecord("infoRecordFakeName5", 1, 1),
            relevantMediaInfoRecord
        ]

        actualMediaInfoRecord = LogicController.findMediaInfoRecord(mediaInfoRecords, relevantMediaInfoRecord.getShowName())

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
            TorrentRecord("fakeTorrentTitle1", "id1", "fakeInfoHash1", "4", "3"),
            TorrentRecord("fakeTorrentTitle2", "id2", "fakeInfoHash2", "6", "5"),
            TorrentRecord("fakeTorrentTitle3", "id3", "fakeInfoHash3", "8", "7"),
            TorrentRecord("fakeTorrentTitle4", "id4", "fakeInfoHash4", "10", "9")
        ]

        fakeMediaInfoRecords = [
            MediaInfoRecord("fakeMediaInfoName1", 1, 1),
            MediaInfoRecord("fakeMediaInfoName2", 1, 1),
            MediaInfoRecord("fakeMediaInfoName3", 1, 1)
        ]

        # configure mocks
        findMediaInfoRecordMock.side_effect = fakeMediaInfoRecords
        getTorrentRecordsMock.return_value = fakeTorrentRecords
        findNewDownloadMock.side_effect = ["fakeTorrentTitle1", None, "fakeTorrentTitle3"]

        # expected outputs
        expectedFakeMediaInfoRecords = []
        for index, fakeMediaInfoRecord in enumerate(fakeMediaInfoRecords):
            if index in [0, 2]:
                fakeMediaInfoRecord.setTorrentRecord(fakeTorrentRecords[index])
                expectedFakeMediaInfoRecords.append(fakeMediaInfoRecord)

        actualOutputMediaInfoRecords = LogicController.getMediaInfoRecordsWithTorrents(fakeMediaSearchQueries, fakeMediaInfoRecords)

        # asserts
        self.assertEqual(expectedFakeMediaInfoRecords, actualOutputMediaInfoRecords)
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

        fakeTorrentRecordsNames = [ torrent.getName() for torrent in fakeTorrentRecords ]        
        findNewDownloadCalls = [
            call(fakeTorrentRecordsNames),
            call(fakeTorrentRecordsNames),
        ]
        findNewDownloadMock.has_calls(findNewDownloadCalls)


    @mock.patch("controllers.NewTorrentController.onSuccessfulTorrentAdd")
    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    @mock.patch("controllers.LogicController.getMediaInfoRecordsWithTorrents")
    @mock.patch("controllers.CompletedDownloadsController.auditDumpCompleteDir")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.getDownloadingItems")
    @mock.patch("controllers.QueryGenerationController.generateTVEpisodeQueries")
    @mock.patch("interfaces.MediaIndexFileInterface.loadMediaFile")
    def test_runProgramLogic(self, loadMediaFileMock, generateTVEpisodeQueriesMock, getDownloadingItemsMock, auditDumpCompleteDirMock, getMediaInfoRecordsWithTorrentsMock, qbittorrentInterfaceGetInstanceMock, onSuccessfulTorrentAddMock):
        
        fakeMediaSearchQueries = {
            "fakeMediaInfoName1": ["fakeMediaInfoName1Query1", "fakeMediaInfoName1Query2", "fakeMediaInfoName1Query3"],
            "fakeMediaInfoName2": ["fakeMediaInfoName2Query1", "fakeMediaInfoName2Query2", "fakeMediaInfoName2Query3"],
            "fakeMediaInfoName3": ["fakeMediaInfoName3Query1", "fakeMediaInfoName3Query2", "fakeMediaInfoName3Query3"]
        }
        
        # config fake inputs
        fakeMediaInfoRecords = [
            MediaInfoRecord("fakeMediaInfoName1", 1, 1),
            MediaInfoRecord("fakeMediaInfoName2", 1, 1),
            MediaInfoRecord("fakeMediaInfoName3", 1, 1)
        ]
        
        # config fake inputs
        fakeMediaInfoRecordsWithTorrents = [
            MediaInfoRecord("fakeMediaInfoName1", 1, 1, TorrentRecord("fakeTorrent1", "id1", "fakeInfoHash", "5")),
            MediaInfoRecord("fakeMediaInfoName2", 1, 1, TorrentRecord("fakeTorrent2", "id2", "fakeInfoHash", "5")),
            MediaInfoRecord("fakeMediaInfoName3", 1, 1, TorrentRecord("fakeTorrent3", "id3", "fakeInfoHash", "5"))
        ]

        # config fake data
        fakeMediaSearchQueries = ["fakeMediaSearchQuery1", "fakeMediaSearchQuery2", "fakeMediaSearchQuery3"]
        activeMode = PROGRAM_MODE.TV_EPISODES
        fakeDownloadingItems =  ["downloadingItem1", "downloadingItem2"]
        
        # config mocks
        generateTVEpisodeQueriesMock.return_value = fakeMediaSearchQueries
        getDownloadingItemsMock.return_value = fakeDownloadingItems
        getMediaInfoRecordsWithTorrentsMock.side_effect = [fakeMediaInfoRecordsWithTorrents, []]
        loadMediaFileMock.return_value = fakeMediaInfoRecords
        # create mock for mailInterface instance
        qbittorrentInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        qbittorrentInterfaceGetInstanceMock.return_value = qbittorrentInterfaceInstanceMock        
        qbittorrentInterfaceInstanceMock.initTorrentDownload.side_effect = [True, False, True]
        
        # call testable function
        LogicController.runProgramLogic(activeMode)
        
        # mock asserts
        generateTVEpisodeQueriesMock.assert_called_with(fakeMediaInfoRecords)
        getDownloadingItemsMock.assert_called_with(activeMode)
        auditDumpCompleteDirMock.assert_called_with(activeMode, fakeDownloadingItems)
        getMediaInfoRecordsWithTorrentsMock.assert_called_with(fakeMediaSearchQueries, fakeMediaInfoRecords)
        
        calls = [ call(fakeMediaInfoRecordsWithTorrents[0]), call(fakeMediaInfoRecordsWithTorrents[1]), call(fakeMediaInfoRecordsWithTorrents[2]) ]
        qbittorrentInterfaceInstanceMock.initTorrentDownload.assert_has_calls(calls)

        calls = [ 
            call(fakeMediaInfoRecordsWithTorrents[0], "latestEpisode", "magnet:?xt=urn:btih:fakeInfoHash&dn=fakeTorrent1", activeMode), 
            call(fakeMediaInfoRecordsWithTorrents[2],"latestEpisode", "magnet:?xt=urn:btih:fakeInfoHash&dn=fakeTorrent3", activeMode) ]
        onSuccessfulTorrentAddMock.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
