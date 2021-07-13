# external dependencies
import unittest
import mock
from mock import MagicMock

# internal dependencies
from src.controllers import NewTorrentController
from src.dataTypes.ProgramMode import PROGRAM_MODE
from src.dataTypes.MediaInfoRecord import MediaInfoRecord
from src.dataTypes.TorrentRecord import TorrentRecord
from src.dataTypes.MailItem import MailItemType

class TestNewTorrentController(unittest.TestCase):

    @mock.patch('src.interfaces.MailInterface.getInstance')
    @mock.patch('src.interfaces.MediaIndexFileInterface.writeMediaFile')
    def test_onSuccessfulTorrentAdd(self, writeMediaFileMock, mailInterfaceGetInstanceMock):

        # config fake values
        fakeTorrent = TorrentRecord("fakeTorrentName", "fakeId", "fakeInfoHash", "5")
        fakeMediaInfoRecord = MediaInfoRecord("fakeRecordName", 1, 1, [], fakeTorrent)
        expectedMediaGrabId = "fakeRecordName--s1e1"
        activeMode = PROGRAM_MODE.TV

        # config mocks
        # create mock for mailInterface instance
        mailInterfaceInstanceMock = MagicMock()
        # assign mocked MailInterface instance to return_vlue for mocked getInstance()
        mailInterfaceGetInstanceMock.return_value = mailInterfaceInstanceMock

        NewTorrentController.onSuccessfulTorrentAdd(fakeMediaInfoRecord, activeMode)
        
        # mock function asserts
        writeMediaFileMock.assert_called_once_with(fakeMediaInfoRecord)
        mailInterfaceInstanceMock.pushMail.assert_called_once_with(
            "ADDED TORRENT: fakeTorrentName Latest episode: 1 \n\n Magnet:magnet:?xt=urn:btih:fakeInfoHash&dn=fakeTorrentName", MailItemType.NEW_TORRENT)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
