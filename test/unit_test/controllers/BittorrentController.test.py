import unittest
from controllers import BittorrentController

class TestBittorrent(unittest.TestCase):

    def test_UnmockedTorrentDownload(self):

        torrentMagnet = "/torrent/18003297/Silicon_Valley_Season_4_S04_720p_AMZN_WEBRip_x265_HEVC_Complete"

        BittorrentController.initTorrent(torrentMagnet)


if __name__ == '__main__':
    unittest.main()