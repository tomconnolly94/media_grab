# external dependencies
import unittest
import mock
from unittest.mock import call
from mock import MagicMock
import copy

# internal dependencies 
from src.controllers import LogicController
from src.dataTypes.ProgramMode import PROGRAM_MODE
from src.dataTypes.TorrentRecord import TorrentRecord
from src.dataTypes.MediaInfoRecord import MediaInfoRecord

class TestLogicController(unittest.TestCase):

    @mock.patch("logging.info")
    @mock.patch("interfaces.TPBInterface.getTorrentRecords")
    def test_getMediaInfoRecordsWithTorrents(self, getTorrentRecordsMock, loggingInfoMock):      

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
        getTorrentRecordsMock.side_effect = [fakeTorrentRecords, [], fakeTorrentRecords[2:]]

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


    @mock.patch("controllers.NewTorrentController.onSuccessfulTorrentAdd")
    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    @mock.patch("controllers.LogicController.getMediaInfoRecordsWithTorrents")
    @mock.patch("controllers.CompletedDownloadsController.auditDumpCompleteDir")
    @mock.patch("controllers.QueryGenerationController.addTVEpisodeQueriesToMediaInfoRecords")
    @mock.patch("interfaces.MediaIndexFileInterface.loadMediaFile")
    def test_runProgramLogic(self, loadMediaFileMock, addTVEpisodeQueriesToMediaInfoRecordsMock, auditDumpCompleteDirMock, getMediaInfoRecordsWithTorrentsMock, qbittorrentInterfaceGetInstanceMock, onSuccessfulTorrentAddMock):
        
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
        activeMode = PROGRAM_MODE.TV
        
        # config mocks
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
        auditDumpCompleteDirMock.assert_called_with()

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
