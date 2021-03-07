# external dependencies
import unittest
import mock

# internal dependencies
from interfaces import QBittorrentInterface

class TestQBittorrentInterface(unittest.TestCase):

    def test_torrentDownload(self):

        class qbMock():
            def __init__(self):
                pass

            def login(self, username, password):
                return True

            def download_from_link(self, torrentMagnet, savepath):
                return "Ok."


        QBittorrentInterface.qb = qbMock()

        torrentMagnet = "/torrent/18003297/Silicon_Valley_Season_4_S04_720p_AMZN_WEBRip_x265_HEVC_Complete"
        torrent = {
            "torrentName": "fakeTorrentName1",
            "magnet": torrentMagnet
        }

        self.assertTrue(QBittorrentInterface.initTorrentDownload(torrent))


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
