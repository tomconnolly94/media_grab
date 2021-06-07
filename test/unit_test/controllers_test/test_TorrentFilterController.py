#!/venv/bin/python

# external dependencies
import unittest
import json

# internal dependencies
from controllers import TorrentFilterController
from dataTypes.MediaInfoRecord import MediaInfoRecord
from dataTypes.TorrentRecord import TorrentRecord, TorrentCategory

class TestTorrentFilterController(unittest.TestCase):


    def test_createBlacklistFilterFunc(self):

        # config fake data
        fakeBlacklistTerms = [
            "blacklistTerm1",
            "blacklistTerm2"
        ]
        fakeSearchableTerms = [
            "blacklistTerm1 file",
            "blacklistTerm3 file",
        ]

        blacklistFilterFunc = TorrentFilterController.createBlacklistFilterFunc(fakeBlacklistTerms)

        filteredTerms = list(filter(blacklistFilterFunc, fakeSearchableTerms))

        self.assertEqual([fakeSearchableTerms[1]], filteredTerms)


    def test_filterBySeason(self):

        name = r"Rick\D*and\D*Morty"
        relevantSeason = "03"

        torrentRecordsFailFilter = [
            # these should fail because they dont contain a season reference
            "Rick.and.morty",
            # these should fail because they dont contain an season reference
            "Rick.and.Morty.e01",
            "Rick.and.Morty.episode.1",
            # these should fail because they dont match the season numbers
            "Rick.and.Morty.S04.1080p.WEBRip.x264-STRiFE",
            "Rick.and.Morty.Season.5.1080p.WEBRip.x264-STRiFE",
            # these should fail because they contain a season and a episode number
            "Rick.and.Morty.S03E02.HDTV.x264-BATV",
            "Rick.and.Morty.S03E02.720p.HDTV.x264-BATV[ettv]",
            "Rick.and.Morty.S03E02.1080p.WEBRip.x264-STRiFE",
            " Rick and Morty S03E02 1080p PT-BR Subs Tocatoon ",
            "Rick....and Morty S03E02 1080p PT-BR Subs Tocatoon ",
            # these should fail because they contain a season and a episode number and the season is incorrect
            "Rick.and.Morty.S04E02.HDTV.x264-BATV"
        ]

        torrentRecordsPassFilter = [
            "Rick.and.Morty.Season.03",
            "Rick.and.Morty.Season.3",
            "Rick.and.Morty.S03",
            "Rick..and.Morty.Season.3"
        ]

        filteredFailedTorrents = TorrentFilterController.filterBySeason(
            torrentRecordsFailFilter, name, relevantSeason)
        filteredPassedTorrents = TorrentFilterController.filterBySeason(
            torrentRecordsPassFilter, name, relevantSeason)

        # assert the right number of torrents were kept from the data input
        self.assertEqual(0, len(filteredFailedTorrents))
        self.assertEqual(len(torrentRecordsPassFilter),
                         len(filteredPassedTorrents))
        # assert that the right number of torrents in the input have the "passesFilter" field set to true
        self.assertEqual(torrentRecordsPassFilter, filteredPassedTorrents)


    def test_filterByEpisode(self):

        name = r"Rick\D*and\D*Morty"
        relevantSeason = "03"
        relevantEpisode = "02"

        torrentRecordsFailFilter = [
            # these should fail because they dont contain a season or episode reference
            "Rick.and.morty",
            # these should fail because they dont contain an episode reference
            "Rick.and.Morty.Season.1",
            "Rick.and.Morty.episode.1",
            # these should fail because they dont contain an episode reference (even though the season number is correct)
            "Rick.and.Morty.Season.3",
            "Rick..and.Morty.Season.3",
            # these should fail because they dont match the season and episode numbers
            "Rick.and.Morty.S04E02.1080p.WEBRip.x264-STRiFE",
            "Rick.and.Morty.S03E03.1080p.WEBRip.x264-STRiFE"
        ]

        torrentRecordsPassFilter = [
            "Rick.and.Morty.S03E02.HDTV.x264-BATV",
            "Rick.and.Morty.S03E02.720p.HDTV.x264-BATV[ettv]",
            "Rick.and.Morty.S03E02.1080p.WEBRip.x264-STRiFE",
            " Rick and Morty S03E02 1080p PT-BR Subs Tocatoon ",
            "Rick....and Morty S03E02 1080p PT-BR Subs Tocatoon "
        ]

        filteredFailedTorrents = TorrentFilterController.filterByEpisode(
            torrentRecordsFailFilter, name, relevantSeason, relevantEpisode)
        filteredPassedTorrents = TorrentFilterController.filterByEpisode(
            torrentRecordsPassFilter, name, relevantSeason, relevantEpisode)

        # assert the right number of torrents were kept from the data input
        self.assertEqual(0, len(filteredFailedTorrents))
        self.assertEqual(len(torrentRecordsPassFilter),
                         len(filteredPassedTorrents))
        # assert that the right number of torrents in the input have the "passesFilter" field set to true
        self.assertEqual(torrentRecordsPassFilter, filteredPassedTorrents)


    def test_filterByBlacklist(self):

        mediaData = MediaInfoRecord("Rick and morty", 3, 2, ["blacklistTerm"])

        torrentRecordsFailFilter = [
            # these should fail because they include a term from the blacklist
            " Rick and Morty S03E02 1080p PT-BR Subs Tocatoon blacklistTerm",
            "Rick....and Morty S03E02 1080p PT-BR Subs TocatoonBlackListTerm"
        ]

        torrentRecordsPassFilter = [
            " Rick and Morty S03E02 1080p PT-BR Subs Tocatoon ",
            "Rick....and Morty S03E02 1080p PT-BR Subs Tocatoon"
        ]

        filteredFailedTorrents = TorrentFilterController.filterByBlacklist(
            mediaData, torrentRecordsFailFilter)
        filteredPassedTorrents = TorrentFilterController.filterByBlacklist(
            mediaData, torrentRecordsPassFilter)

        # assert the right number of torrents were kept from the data input
        self.assertEqual(0, len(filteredFailedTorrents))
        self.assertEqual(len(torrentRecordsPassFilter),
                         len(filteredPassedTorrents))
        # assert that the right number of torrents in the input have the "passesFilter" field set to true
        self.assertEqual(torrentRecordsPassFilter, filteredPassedTorrents)

    def test_filterTorrents(self):

        mediaData = MediaInfoRecord("Rick and morty", 3, 2, ["blacklistTerm"])

        torrentRecordsFailFilter = [
            # these should fail because they dont contain a season or episode reference
            TorrentRecord("Rick.and.morty", "fakeId", "fakeInfoHash", 2),
            # these should fail because they dont contain a season AND episode reference
            TorrentRecord("Rick.and.Morty.episode.1",
                          "fakeId", "fakeInfoHash", 2),
            # these should fail because they dont match the season and episode numbers
            TorrentRecord(
                "Rick.and.Morty.S04E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2),
            TorrentRecord(
                "Rick.and.Morty.S03E03.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2),
            # these should fail because they include a term from the blacklist
            TorrentRecord(
                " Rick and Morty S03E02 1080p PT-BR Subs Tocatoon blacklistTerm", "fakeId", "fakeInfoHash", 2),
            TorrentRecord(
                "Rick....and Morty S03E02 1080p PT-BR Subs TocatoonBlackListTerm", "fakeId", "fakeInfoHash", 2)

            #TODO: These should fail but I can't figure out a torrentFilter configuration that achieves that yet
            #TorrentRecord("Rick.and.Morty.the.movie.S03E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2),
            #TorrentRecord("Rick.and.Morty.fun day at the zoo.S03E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2)
        ]

        torrentRecordsPassFilter = [
            TorrentRecord("Rick.and.Morty.S03E02.HDTV.x264-BATV",
                          "fakeId", "fakeInfoHash", 2, None, TorrentCategory.TV_EPISODE),
            TorrentRecord(
                "Rick.and.Morty.S03E02.720p.HDTV.x264-BATV[ettv]", "fakeId", "fakeInfoHash", 2, None, TorrentCategory.TV_EPISODE),
            TorrentRecord(
                "Rick.and.Morty.S03E02.1080p.WEBRip.x264-STRiFE", "fakeId", "fakeInfoHash", 2, None, TorrentCategory.TV_EPISODE),
            TorrentRecord(
                " Rick and Morty S03E02 1080p PT-BR Subs Tocatoon ", "fakeId", "fakeInfoHash", 2, None, TorrentCategory.TV_EPISODE),
            TorrentRecord(
                "Rick....and Morty S03E02 1080p PT-BR Subs Tocatoon ", "fakeId", "fakeInfoHash", 2, None, TorrentCategory.TV_EPISODE),

            TorrentRecord("Rick.and.Morty.Season.3",
                          "fakeId", "fakeInfoHash", 2, None, TorrentCategory.TV_SEASON),
            TorrentRecord("Rick..and.Morty.Season.3",
                          "fakeId", "fakeInfoHash", 2, None, TorrentCategory.TV_SEASON)
        ]

        filteredFailedTorrents = TorrentFilterController.filterTorrents(
            torrentRecordsFailFilter, mediaData)
        filteredPassedTorrents = TorrentFilterController.filterTorrents(
            torrentRecordsPassFilter, mediaData)

        # assert the right number of torrents were kept from the data input
        self.assertEqual(0, len(filteredFailedTorrents))
        self.assertEqual(len(torrentRecordsPassFilter),
                         len(filteredPassedTorrents))
        
        for torrent in filteredPassedTorrents:
            self.assertTrue(torrent in torrentRecordsPassFilter)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
