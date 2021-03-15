# external dependencies
import unittest
import mock
from mock import MagicMock

# internal dependencies
from controllers import NewTorrentController
from dataTypes.ProgramMode import PROGRAM_MODE

class TestNewTorrentController(unittest.TestCase):

    @mock.patch('interfaces.DownloadsInProgressFileInterface.notifyDownloadStarted')
    @mock.patch('interfaces.MailInterface.getInstance')
    @mock.patch('interfaces.MediaIndexFileInterface.writeMediaFile')
    def test_onSuccessfulTorrentAdd(self, writeMediaFileMock, mailInterfaceGetInstanceMock, notifyDownloadStartedMock):

        # config fake values
        fakeQueryRecord = {
            "name": "RecordName",
            "typeSpecificData": {
                "latestSeason": 1,
                "latestEpisode": 1
            },
            "torrentName": "fakeTorrentName",
            "mediaGrabId": "fakeTorrentName--s1e1"
        }
        fakeUpdateableField = "latestSeason"
        fakeTorrentMagnetLink = "fakeTorrentMagnet"
        activeMode = PROGRAM_MODE.TV_SEASONS

        # config mocks
        # create mock for mailInterface instance
        mailInterfaceInstanceMock = MagicMock()
        # assign mocked MailInterface instance to return_vlue for mocked getInstance()
        mailInterfaceGetInstanceMock.return_value = mailInterfaceInstanceMock

        NewTorrentController.onSuccessfulTorrentAdd(fakeQueryRecord, fakeUpdateableField, fakeTorrentMagnetLink, activeMode)
        
        # mock function asserts
        writeMediaFileMock.assert_called_once_with(fakeQueryRecord, fakeUpdateableField)
        mailInterfaceInstanceMock.sendNewTorrentMail.assert_called_once_with(fakeQueryRecord['torrentName'], f"{fakeUpdateableField} {fakeQueryRecord['typeSpecificData']['latestSeason']}", fakeTorrentMagnetLink)
        notifyDownloadStartedMock.assert_called_once_with(fakeQueryRecord["mediaGrabId"], activeMode)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
