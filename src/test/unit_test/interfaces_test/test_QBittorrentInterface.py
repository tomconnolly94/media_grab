# external dependencies
import unittest
import os
import mock
from mock import MagicMock

# internal dependencies
from src.interfaces.QBittorrentInterface import QBittorrentInterface
from src.dataTypes.TorrentRecord import TorrentCategory, TorrentRecord
from src.dataTypes.MediaInfoRecord import MediaInfoRecord

class TestQBittorrentInterface(unittest.TestCase):

    @mock.patch("logging.info")
    @mock.patch("os.getenv")
    def test_initTorrentDownload(self, getEnvMock, loggingInfoMock):

        # config fake values
        fakeTorrent = TorrentRecord("fakeTorrentName1", "id", "fakeInfoHash", 2, 3, TorrentCategory.TV_SEASON)
        fakeMediaInfoRecord = MediaInfoRecord("fakeShowName", 1, 2, [], fakeTorrent)
        fakeMediaInfoRecord.setTorrentRecord(fakeTorrent)
        fakeDumpCompleteDir = "/fake/dump/complete/dir"

        # create testable object and override the qb member
        getEnvMock.return_value = None # this prevents the qbittorrent client from reaching out to a server
        qBittorrentInterface = QBittorrentInterface(fakeDumpCompleteDir)
        fakeQBObject = MagicMock()
        fakeQBObject.download_from_link.return_value = "Ok."
        qBittorrentInterface.overrideQBObject(fakeQBObject)

        # call testable function
        torrentInitSuccess = qBittorrentInterface.initTorrentDownload(fakeMediaInfoRecord)

        # asserts
        self.assertTrue(torrentInitSuccess)
        expectedDownloadPath = os.path.join(fakeDumpCompleteDir, fakeMediaInfoRecord.getMediaGrabId())
        fakeQBObject.download_from_link.assert_called_with(
            fakeTorrent.getMagnet(), savepath=expectedDownloadPath)
        loggingInfoMock.assert_called_with(f"Torrent added: {fakeTorrent.getName()}")


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
