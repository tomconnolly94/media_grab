# external dependencies
import unittest
import mock
from mock import MagicMock

# internal dependencies
from controllers import NewTorrentController
from dataTypes.ProgramMode import PROGRAM_MODE
from dataTypes.MediaInfoRecord import MediaInfoRecord
from dataTypes.TorrentRecord import TorrentRecord

class TestNewTorrentController(unittest.TestCase):

    @mock.patch('interfaces.DownloadsInProgressFileInterface.notifyDownloadStarted')
    @mock.patch('interfaces.MailInterface.getInstance')
    @mock.patch('interfaces.MediaIndexFileInterface.writeMediaFile')
    def test_onSuccessfulTorrentAdd(self, writeMediaFileMock, mailInterfaceGetInstanceMock, notifyDownloadStartedMock):

        # config fake values
        fakeTorrent = TorrentRecord("fakeTorrentName", "fakeId", "fakeInfoHash", "5")
        fakeMediaInfoRecord = MediaInfoRecord("fakeRecordName", 1, 1, fakeTorrent)
        expectedMediaGrabId = "fakeRecordName--s1e1"
        activeMode = PROGRAM_MODE.TV_EPISODES

        # config mocks
        # create mock for mailInterface instance
        mailInterfaceInstanceMock = MagicMock()
        # assign mocked MailInterface instance to return_vlue for mocked getInstance()
        mailInterfaceGetInstanceMock.return_value = mailInterfaceInstanceMock

        NewTorrentController.onSuccessfulTorrentAdd(fakeMediaInfoRecord, activeMode)
        
        # mock function asserts
        writeMediaFileMock.assert_called_once_with(fakeMediaInfoRecord)
        mailInterfaceInstanceMock.sendNewTorrentMail.assert_called_once_with(fakeTorrent.getName(),  f"Latest episode: {fakeMediaInfoRecord.getLatestEpisodeNumber()}", fakeTorrent.getMagnet())
        notifyDownloadStartedMock.assert_called_once_with(expectedMediaGrabId, activeMode)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
