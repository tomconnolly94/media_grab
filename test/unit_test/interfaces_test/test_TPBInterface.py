#!/venv/bin/python

# external dependencies
import unittest
import mock
from mock import call
import json

# internal dependencies
from interfaces import TPBInterface
from dataTypes.MediaInfoRecord import MediaInfoRecord
from dataTypes.TorrentRecord import TorrentRecord


class TestTPBInterface(unittest.TestCase):

    @mock.patch("controllers.TorrentFilterController.filterEpisodeTorrents")
    @mock.patch("logging.info")
    @mock.patch("interfaces.TPBInterface.queryAPI")
    def test_getTorrentRecords(self, queryMock, loggingInfoMock, filterEpisodeTorrentsMock):
        
        # config fake data
        fakeTPBQueryResponses = [
            [], 
            [
                TorrentRecord("torrent1", "id1", "fakeInfoHash", "5"),
                TorrentRecord("torrent2", "id1", "fakeInfoHash", "10"),
                TorrentRecord("torrent3", "id1", "fakeInfoHash", "0")
            ]
        ]
        queries = ["fakeQueryString1", "fakeQueryString2", "fakeQueryString3"]
        fakeMediaInfoRecord = MediaInfoRecord(
            "fakeShowName", 1, 2, mediaSearchQueries=queries)
        fakeFilteredTorrents = fakeTPBQueryResponses[1][:2]

        # config mocks
        queryMock.side_effect = fakeTPBQueryResponses
        filterEpisodeTorrentsMock.return_value = fakeFilteredTorrents

        # run testable function
        torrentRecords = TPBInterface.getTorrentRecords(fakeMediaInfoRecord)

        # asserts
        expectedTorrentRecords = fakeFilteredTorrents
        self.assertEqual(expectedTorrentRecords, torrentRecords)
        queryAPI = [
            call(queries[0]),
            call(queries[1]),
            call(queries[2])
        ]
        queryMock.has_calls(queryAPI)
        filterEpisodeTorrentsMock.assert_called_with(fakeTPBQueryResponses[1], fakeMediaInfoRecord)
        logCalls = [
            call(
                f"Torrent search performed for: '{queries[0]}' - {len(fakeTPBQueryResponses[0])} results."),
            call(
                f"Torrent search performed for: '{queries[1]}' - {len(fakeTPBQueryResponses[1])} results."),
            call(f"Torrent search performed for: '{queries[2]}' - {len(fakeTPBQueryResponses[1])} results.")
        ]
        loggingInfoMock.has_calls(logCalls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
