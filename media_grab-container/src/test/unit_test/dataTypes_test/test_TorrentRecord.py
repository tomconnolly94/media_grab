#!/venv/bin/python

# external dependencies
import unittest

# internal dependencies
from src.dataTypes.MediaInfoRecord import MediaInfoRecord
from src.dataTypes.TorrentRecord import TorrentCategory, TorrentRecord


class TestTorrentRecord(unittest.TestCase):

    def test_TorrentRecordInit(self):

        # input data
        fakeEpisodeTorrentRecord = TorrentRecord(
            "fakeEpisodeTorrentRecord",
            "fakeTorrentId",
            "fakeInfoHash",
            "fakeSize",
            "1",
            "fakeLeechers",
            TorrentCategory.TV_EPISODE,
        )
        fakeSeasonTorrentRecord = TorrentRecord(
            "fakeSeasonTorrentRecord",
            "fakeTorrentId",
            "fakeInfoHash",
            "fakeSize",
            2,
            "fakeLeechers",
            TorrentCategory.TV_SEASON,
        )

        # torrentRecord asserts
        self.assertEqual(
            "fakeEpisodeTorrentRecord", fakeEpisodeTorrentRecord.getName()
        )
        self.assertEqual("fakeTorrentId", fakeEpisodeTorrentRecord.getId())
        self.assertEqual("fakeInfoHash", fakeEpisodeTorrentRecord.getInfoHash())
        self.assertEqual("fakeSize", fakeEpisodeTorrentRecord.getSize())
        self.assertEqual(1, fakeEpisodeTorrentRecord.getSeeders())
        self.assertEqual(
            TorrentCategory.TV_EPISODE, fakeEpisodeTorrentRecord.getCategory()
        )

        self.assertEqual(
            "fakeSeasonTorrentRecord", fakeSeasonTorrentRecord.getName()
        )
        self.assertEqual("fakeTorrentId", fakeSeasonTorrentRecord.getId())
        self.assertEqual("fakeInfoHash", fakeSeasonTorrentRecord.getInfoHash())
        self.assertEqual("fakeSize", fakeSeasonTorrentRecord.getSize())
        self.assertEqual(2, fakeSeasonTorrentRecord.getSeeders())
        self.assertEqual(
            TorrentCategory.TV_SEASON, fakeSeasonTorrentRecord.getCategory()
        )
