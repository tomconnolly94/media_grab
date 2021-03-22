# external dependencies
import unittest
import mock
from unittest.mock import call
from mock import MagicMock
import copy

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

        # run testable function
        actualOutputMediaInfoRecords = LogicController.getMediaInfoRecordsWithTorrents(fakeMediaInfoRecords)

        # asserts
        self.assertEqual(expectedFakeMediaInfoRecords, actualOutputMediaInfoRecords)
        findMediaInfoRecordCalls = [
            call(fakeMediaInfoRecords, "fakeMediaInfoName1"),
            call(fakeMediaInfoRecords, "fakeMediaInfoName2"),
            call(fakeMediaInfoRecords, "fakeMediaInfoName3")
        ]
        findMediaInfoRecordMock.has_calls(findMediaInfoRecordCalls)

        getTorrentRecordsCalls = [
            call(fakeMediaInfoRecords[0]),
            call(fakeMediaInfoRecords[1]),
            call(fakeMediaInfoRecords[2])
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
    @mock.patch("controllers.QueryGenerationController.addTVEpisodeQueriesToMediaInfoRecords")
    @mock.patch("interfaces.MediaIndexFileInterface.loadMediaFile")
    def test_runProgramLogic(self, loadMediaFileMock, addTVEpisodeQueriesToMediaInfoRecordsMock, getDownloadingItemsMock, auditDumpCompleteDirMock, getMediaInfoRecordsWithTorrentsMock, qbittorrentInterfaceGetInstanceMock, onSuccessfulTorrentAddMock):
        
        fakeMediaInfoRecord1 = MediaInfoRecord("fakeMediaInfoName1", 1, 1)
        fakeMediaInfoRecord2 = MediaInfoRecord("fakeMediaInfoName2", 1, 1)
        fakeMediaInfoRecord3 = MediaInfoRecord("fakeMediaInfoName3", 1, 1)
        
        # config fake inputs
        fakeMediaInfoRecordsOriginalFull = [
            fakeMediaInfoRecord1,
            fakeMediaInfoRecord2,
            fakeMediaInfoRecord3
        ]

        # mocked from getMediaInfoRecordsWithTorrents (first run)
        fakeMediaInfoRecord1Copy = copy.deepcopy(fakeMediaInfoRecord1)
        fakeMediaInfoRecord1Copy.setTorrentRecord(TorrentRecord(
            f"{fakeMediaInfoRecord1.getShowName()}-torrentName", "fakeTorrentId", "fakeInfoHash", 10))
        fakeMediaInfoRecord2Copy = copy.deepcopy(fakeMediaInfoRecord2)
        fakeMediaInfoRecord2Copy.setTorrentRecord(TorrentRecord(
            f"{fakeMediaInfoRecord2.getShowName()}-torrentName", "fakeTorrentId", "fakeInfoHash", 10))
        fakeMediaInfoRecordsWithTorrentsFiltered = [
            fakeMediaInfoRecord1Copy, fakeMediaInfoRecord2Copy]

        # config fake data
        activeMode = PROGRAM_MODE.TV_EPISODES
        fakeDownloadingItems =  ["downloadingItem1", "downloadingItem2"]
        
        # config mocks
        getDownloadingItemsMock.return_value = fakeDownloadingItems
        getMediaInfoRecordsWithTorrentsMock.side_effect = [
            fakeMediaInfoRecordsWithTorrentsFiltered,
            []
        ]
        loadMediaFileMock.return_value = fakeMediaInfoRecordsOriginalFull
        # create mock for mailInterface instance
        qbittorrentInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        qbittorrentInterfaceGetInstanceMock.return_value = qbittorrentInterfaceInstanceMock        
        qbittorrentInterfaceInstanceMock.initTorrentDownload.side_effect = [True, False]
        
        # run testable function
        LogicController.runProgramLogic(activeMode)
        
        # mock asserts

        addTVEpisodeQueriesToMediaInfoRecordsMockCalls = [
            call(fakeMediaInfoRecordsOriginalFull),
            call(fakeMediaInfoRecordsOriginalFull),
        ]
        addTVEpisodeQueriesToMediaInfoRecordsMock.assert_has_calls(addTVEpisodeQueriesToMediaInfoRecordsMockCalls)
        getDownloadingItemsMock.assert_called_with(activeMode)
        auditDumpCompleteDirMock.assert_called_with(activeMode, fakeDownloadingItems)

        getMediaInfoRecordsWithTorrentsMockCalls = [
            call(fakeMediaInfoRecordsOriginalFull),
            call([ fakeMediaInfoRecord1, fakeMediaInfoRecord1 ])
        ]
        
        initTorrentDownloadCalls = [
            call(fakeMediaInfoRecordsWithTorrentsFiltered[0]),
            call(fakeMediaInfoRecordsWithTorrentsFiltered[1])
        ]
        qbittorrentInterfaceInstanceMock.initTorrentDownload.assert_has_calls(
            initTorrentDownloadCalls)

        onSuccessfulTorrentAddMock.assert_called_with(
            fakeMediaInfoRecordsWithTorrentsFiltered[0], activeMode)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
