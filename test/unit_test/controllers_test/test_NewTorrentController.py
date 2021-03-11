# external dependencies
import unittest
import mock

# internal dependencies
from controllers import NewTorrentController
from data_types.ProgramMode import PROGRAM_MODE

class TestNewTorrentController(unittest.TestCase):

    @mock.patch('interfaces.DownloadsInProgressFileInterface.notifyDownloadStarted')
    @mock.patch('interfaces.MailInterface.sendNewTorrentMail')
    @mock.patch('interfaces.MediaIndexFileInterface.writeMediaFile')
    def test_onSuccessfulTorrentAdd(self, writeMediaFileMock, sendNewTorrentMailMock, notifyDownloadStartedMock):

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

        NewTorrentController.onSuccessfulTorrentAdd(fakeQueryRecord, fakeUpdateableField, fakeTorrentMagnetLink, activeMode)
        
        # mock function asserts
        writeMediaFileMock.assert_called_once_with(fakeQueryRecord, fakeUpdateableField)
        sendNewTorrentMailMock.assert_called_once_with(fakeQueryRecord['torrentName'], f"{fakeUpdateableField} {fakeQueryRecord['typeSpecificData']['latestSeason']}", fakeTorrentMagnetLink)
        notifyDownloadStartedMock.assert_called_once_with(fakeQueryRecord["mediaGrabId"], activeMode)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
