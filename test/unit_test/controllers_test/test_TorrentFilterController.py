import unittest
import json
from controllers import TorrentFilterController

class TestTorrentFilterController(unittest.TestCase):


    def test_filterEpisodeTorrentPageUrls(self):

        #`latestSeason` must be 2 to match the test data in 'test/unit_test/unit_test_resources/fakeTorrentData.json'
        mediaData = {
            "name": "Rick and morty",
            "typeSpecificData": {
                "latestSeason": "3",
                "latestEpisode": "2"
            }
        }

        torrentData = []
        
        with open('test/unit_test/unit_test_resources/fakeTorrentData.json', 'r') as file:
            jsonData = json.load(file) 
            torrentData = jsonData["episodeTorrentData"]


        filteredTorrents = TorrentFilterController.filterEpisodeTorrents(torrentData, mediaData)

        expectedFilteredTorrents = [ torrent for torrent in torrentData if torrent["passesFilter"] ]

        # assert the right number of torrents were kept from the data input
        self.assertEqual(len(expectedFilteredTorrents), len(filteredTorrents))
        # assert that the right number of torrents in the input have the "passesFilter" field set to true
        self.assertEqual(expectedFilteredTorrents, filteredTorrents)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
