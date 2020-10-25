# external dependencies
import unittest
import mock

# internal dependencies
from controllers import BittorrentController

class TestBittorrentController(unittest.TestCase):

    @mock.patch('controllers.BittorrentController.Client')
    @mock.patch('controllers.BittorrentController.getQbittorentClient')
    def test_UnmockedTorrentDownload(self, getQbittorentClientMock, qbittorrentClientMock):

        qbittorrentClientMock.download_from_link.return_value = "Ok."
        getQbittorentClientMock.return_value = qbittorrentClientMock


        torrentMagnet = "/torrent/18003297/Silicon_Valley_Season_4_S04_720p_AMZN_WEBRip_x265_HEVC_Complete"

        self.assertTrue(BittorrentController.initTorrentDownload(torrentMagnet))


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
