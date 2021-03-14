# external dependencies
import unittest
import os
import mock
from mock import MagicMock

# internal dependencies
from interfaces.QBittorrentInterface import QBittorrentInterface

class TestQBittorrentInterface(unittest.TestCase):

    @mock.patch("logging.info")
    def test_torrentDownload(self, loggingInfoMock):

        # config fake values
        torrentMagnet = "/torrent/18003297/Silicon_Valley_Season_4_S04_720p_AMZN_WEBRip_x265_HEVC_Complete"
        torrent = {
            "torrentName": "fakeTorrentName1",
            "magnet": torrentMagnet,
            "mediaGrabId": "fakeTorrentName1--s1e2"
        }
        fakeDumpCompleteDir = "/fake/dump/complete/dir"

        # create testable object and override the qb member
        qBittorrentInterface = QBittorrentInterface(fakeDumpCompleteDir)
        qBittorrentInterface.qb = MagicMock()
        qBittorrentInterface.qb.download_from_link.return_value = "Ok."

        # call testable function
        torrentInitSuccess = qBittorrentInterface.initTorrentDownload(torrent)

        # asserts
        self.assertTrue(torrentInitSuccess)
        expectedDownloadPath = os.path.join(fakeDumpCompleteDir, torrent["mediaGrabId"])
        qBittorrentInterface.qb.download_from_link.assert_called_with(torrent["magnet"], savepath=expectedDownloadPath)
        loggingInfoMock.assert_called_with(f"Torrent added: {torrent['torrentName']}")



if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
