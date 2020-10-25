# external dependencies
import unittest
import mock

# internal dependencies
from controllers import NewTorrentController

class TestNewTorrentController(unittest.TestCase):

    @mock.patch('logging.info')
    @mock.patch('interfaces.MailInterface.sendMail')
    @mock.patch('interfaces.MediaFileInterface.writeMediaFile')
    def test_onSuccessfulTorrentAdd(self, writeMediaFileMock, sendMailMock, infoMock):

        fakeQueryRecord = {
            "name": "RecordName",
            "typeSpecificData": {
                "latestSeason": 1,
                "latestEpisode": 1
            }
        }
        fakeUpdateableField = "latestSeason"
        fakeTorrentMagnetLink = "fakeTorrentMagnet"

        NewTorrentController.onSuccessfulTorrentAdd(fakeQueryRecord, fakeUpdateableField, fakeTorrentMagnetLink)

        expectedEmailText = "ADDED TORRENT: RecordName latestSeason 1 \n\n Magnet:fakeTorrentMagnet"

        # mock function asserts
        writeMediaFileMock.assert_called_once_with(fakeQueryRecord, fakeUpdateableField)
        sendMailMock.assert_called_once_with(expectedEmailText)
        infoMock.assert_called_once_with(expectedEmailText)       


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
