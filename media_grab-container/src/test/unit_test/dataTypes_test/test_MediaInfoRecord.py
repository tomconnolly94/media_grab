#!/venv/bin/python

# external dependencies
import unittest
import mock

# internal dependencies
from dataTypes.MediaInfoRecord import MediaInfoRecord
from dataTypes.TorrentRecord import TorrentCategory, TorrentRecord

class TestMediaInfoRecord(unittest.TestCase):

    def test_MediaInfoRecordInit(self):

        # fake input data
        fakeShowName = "fakeShowName"
        fakeLatestSeasonNumber = "1"
        fakeLatestEpisodeNumber = "2"
        fakeBlacklistTerms = ["blacklistTerm1", "blacklistTerm2" ]
        fakeMediaSearchQueries = [
            "mediaSearchQuery1",
            "mediaSearchQuery2", 
            "mediaSearchQuery3"
        ]
        fakeEpisodeTorrentRecord = TorrentRecord(
            "fakeEpisodeTorrentRecord", "fakeTorrentId", "fakeInfoHash", "fakeSeeders", "fakeLeechers", TorrentCategory.TV_EPISODE)
        fakeSeasonTorrentRecord = TorrentRecord(
            "fakeSeasonTorrentRecord", "fakeTorrentId", "fakeInfoHash", "fakeSeeders", "fakeLeechers", TorrentCategory.TV_SEASON)

        # create testable object
        mediaInfoRecord = MediaInfoRecord(
            fakeShowName, fakeLatestSeasonNumber, fakeLatestEpisodeNumber, fakeBlacklistTerms)

        # basic asserts 
        self.assertEqual(fakeShowName, mediaInfoRecord.getShowName())
        self.assertEqual(int(fakeLatestSeasonNumber),
                         mediaInfoRecord.getLatestSeasonNumber())
        self.assertEqual(int(fakeLatestEpisodeNumber),
                         mediaInfoRecord.getLatestEpisodeNumber())
        self.assertEqual(fakeBlacklistTerms,
                         mediaInfoRecord.getBlacklistTerms())
        self.assertEqual(None,
                         mediaInfoRecord.getMediaGrabId())
        self.assertEqual(None,
                         mediaInfoRecord.getMediaSearchQueries())
        self.assertEqual(None,
                         mediaInfoRecord.getTorrentRecord())

        # add mediaSearchQueries
        mediaInfoRecord.setMediaSearchQueries(fakeMediaSearchQueries)

        # mediaSearchQuery asserts
        self.assertEqual(fakeMediaSearchQueries,
                         mediaInfoRecord.getMediaSearchQueries())

        # add episode torrentRecord
        mediaInfoRecord.setTorrentRecord(fakeEpisodeTorrentRecord)

        # torrentRecord asserts
        self.assertEqual(fakeEpisodeTorrentRecord,
                         mediaInfoRecord.getTorrentRecord())
        self.assertEqual(
            f"{fakeShowName}--s{fakeLatestSeasonNumber}e{fakeLatestEpisodeNumber}", mediaInfoRecord.getMediaGrabId())

        # add season torrentRecord
        mediaInfoRecord.setTorrentRecord(fakeSeasonTorrentRecord)

        # torrentRecord asserts
        self.assertEqual(fakeSeasonTorrentRecord,
                         mediaInfoRecord.getTorrentRecord())
        self.assertEqual(
            f"{fakeShowName}--s{fakeLatestSeasonNumber}", mediaInfoRecord.getMediaGrabId())
