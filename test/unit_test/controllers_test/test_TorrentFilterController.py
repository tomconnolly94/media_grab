#!/venv/bin/python

# external dependencies
import unittest
import json

# internal dependencies
from controllers import TorrentFilterController
from dataTypes.MediaInfoRecord import MediaInfoRecord
from dataTypes.TorrentRecord import TorrentRecord

class TestTorrentFilterController(unittest.TestCase):

    def test_filterEpisodeTorrentPageUrls(self):

        mediaData = MediaInfoRecord("Rick and morty", 3, 2, ["blacklistTerm"])

        torrentRecordsFailFilter = [
            # these should fail because they dont contain a season or episode reference
            TorrentRecord("Rick.and.morty", "fakeId", "fakeInfoHash", 2),
            # these should fail because they dont contain an episode reference
            TorrentRecord("Rick.and.Morty.Season.1", "fakeId", "fakeInfoHash", 2),
            TorrentRecord("Rick.and.Morty.episode.1", "fakeId", "fakeInfoHash", 2),
            # these should fail because they dont contain an episode reference (even though the season number is correct)
            TorrentRecord("Rick.and.Morty.Season.3", "fakeId", "fakeInfoHash", 2),
            TorrentRecord("Rick..and.Morty.Season.3", "fakeId", "fakeInfoHash", 2),
            # these should fail because they dont match the season and episode numbers
            TorrentRecord("Rick.and.Morty.S04E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2),
            TorrentRecord("Rick.and.Morty.S03E03.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2),
            # these should fail because they include a term from the blacklist 
            TorrentRecord(" Rick and Morty S03E02 1080p PT-BR Subs Tocatoon blacklistTerm", "fakeId", "fakeInfoHash", 2),
            TorrentRecord("Rick....and Morty S03E02 1080p PT-BR Subs TocatoonBlackListTerm", "fakeId", "fakeInfoHash", 2)

            #TODO: These should fail but I can't figure out a torrentFilter configuration that achieves that yet
            #TorrentRecord("Rick.and.Morty.the.movie.S03E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2),
            #TorrentRecord("Rick.and.Morty.fun day at the zoo.S03E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2)
        ]

        torrentRecordsPassFilter = [
            TorrentRecord("Rick.and.Morty.S03E02.HDTV.x264-BATV", "fakeId", "fakeInfoHash", 2),
            TorrentRecord("Rick.and.Morty.S03E02.720p.HDTV.x264-BATV[ettv]", "fakeId", "fakeInfoHash", 2),
            TorrentRecord("Rick.and.Morty.S03E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2),
            TorrentRecord(" Rick and Morty S03E02 1080p PT-BR Subs Tocatoon ", "fakeId", "fakeInfoHash", 2),
            TorrentRecord("Rick....and Morty S03E02 1080p PT-BR Subs Tocatoon ", "fakeId", "fakeInfoHash", 2)
        ]

        filteredFailedTorrents = TorrentFilterController.filterEpisodeTorrents(torrentRecordsFailFilter, mediaData)
        filteredPassedTorrents = TorrentFilterController.filterEpisodeTorrents(torrentRecordsPassFilter, mediaData)

        # assert the right number of torrents were kept from the data input
        self.assertEqual(0, len(filteredFailedTorrents))
        self.assertEqual(len(torrentRecordsPassFilter), len(filteredPassedTorrents))
        # assert that the right number of torrents in the input have the "passesFilter" field set to true
        self.assertEqual(torrentRecordsPassFilter, filteredPassedTorrents)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
