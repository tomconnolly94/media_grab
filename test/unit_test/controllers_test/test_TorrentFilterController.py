import unittest
import json
from controllers import TorrentFilterController

class TestTorrentFilterController(unittest.TestCase):

    def test_filterSeasonTorrentPageUrls(self):

        #`latestSeason` must be 2 to match the test data in 'test/unit_test/unit_test_resources/fakeTorrentData.json'
        mediaData = {
            "name": "Rick and morty",
            "typeSpecificData": {
                "latestSeason": "2",
                "latestEpisode": "10"
            }
        }

        torrentData = []
        
        with open('test/unit_test/unit_test_resources/fakeTorrentData.json', 'r') as file:
            jsonData = json.load(file) 
            torrentData = jsonData["torrents"]
            
            for torrent in torrentData:
                torrent["itemPageLink"] = "fakePageLink"
                torrent["itemMagnetLink"] = "fakeMagnetLink"


        filteredTorrents = TorrentFilterController.filterSeasonTorrents(torrentData, mediaData)

        numOfTorrentsThatPassFilter = 27

        # assert the right number of torrents were kept from the data input
        self.assertEqual(numOfTorrentsThatPassFilter, len(filteredTorrents))

        # assert that the right number of torrents in the input have the "passesFilter" field set to true
        self.assertEqual(numOfTorrentsThatPassFilter, len([torrent for torrent in torrentData if torrent["passesFilter"]]))

        for torrent in filteredTorrents:
            self.assertTrue(torrent["passesFilter"])


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
