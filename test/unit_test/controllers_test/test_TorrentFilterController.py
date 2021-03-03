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
        torrentTitles = []
        
        with open('test/unit_test/unit_test_resources/fakeTorrentData.json', 'r') as file:
            jsonData = json.load(file) 
            torrentData = jsonData["episodeTorrentData"]
            torrentTitles = [torrent["itemText"] for torrent in torrentData]


        filteredTorrents = TorrentFilterController.filterEpisodeTorrents(torrentTitles, mediaData)

        expectedFilteredTorrents = [ torrent["itemText"] for torrent in torrentData if torrent["passesFilter"] ]


        # assert the right number of torrents were kept from the data input
        self.assertEqual(len(expectedFilteredTorrents), len(filteredTorrents))
        # assert that the right number of torrents in the input have the "passesFilter" field set to true
        self.assertEqual(expectedFilteredTorrents, filteredTorrents)


    # def test_filterSeasonTorrentPageUrls(self):

    #     #`latestSeason` must be 2 to match the test data in 'test/unit_test/unit_test_resources/fakeTorrentData.json'
    #     mediaData = {
    #         "name": "Rick and morty",
    #         "typeSpecificData": {
    #             "latestSeason": "2",
    #             "latestEpisode": "10"
    #         }
    #     }

    #     torrentData = []
    #     torrentTitles = []
        
    #     with open('test/unit_test/unit_test_resources/fakeTorrentData.json', 'r') as file:
    #         jsonData = json.load(file) 
    #         torrentData = jsonData["torrents"]
    #         torrentTitles = [torrent["itemText"] for torrent in torrentData]


    #     filteredTorrents = TorrentFilterController.filterSeasonTorrents(torrentTitles, mediaData)

    #     numOfTorrentsThatPassFilter = 5

    #     # assert the right number of torrents were kept from the data input
    #     self.assertEqual(numOfTorrentsThatPassFilter, len(filteredTorrents))

    #     expectedFilteredTorrents = [ torrent["itemText"] for torrent in torrentData if torrent["passesFilter"] ]

    #     # assert that the right number of torrents in the input have the "passesFilter" field set to true
    #     self.assertEqual(expectedFilteredTorrents, filteredTorrents)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
