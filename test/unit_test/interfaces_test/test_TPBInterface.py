# external dependencies
import unittest
import mock
from mock import call
import json

# internal dependencies
from interfaces import TPBInterface

class TestTPBInterface(unittest.TestCase):

    @mock.patch("controllers.TorrentFilterController.filterEpisodeTorrents")
    @mock.patch("logging.info")
    @mock.patch("interfaces.TPBInterface.queryAPI")
    def test_getTorrentRecords(self, queryMock, loggingInfoMock, filterEpisodeTorrentsMock):
        
        # config fake data
        fakeTPBQueryResponses = [[], [{"name": "torrent1", "seeders": "5"}, {"name": "torrent2", "seeders": "10"}, {"name": "torrent3", "seeders": "0"}]]
        queries = ["fakeQueryString1", "fakeQueryString2", "fakeQueryString3"]
        fakeMediaInfoRecord = "fakeMediaInfoRecord"
        fakeFilteredTorrents = fakeTPBQueryResponses[1][:2]

        # config mocks
        queryMock.side_effect = fakeTPBQueryResponses
        filterEpisodeTorrentsMock.return_value = fakeFilteredTorrents

        # run testable function
        torrentRecords = TPBInterface.getTorrentRecords(queries, fakeMediaInfoRecord)

        # asserts
        expectedTorrentRecords = [ fakeFilteredTorrents[1], fakeFilteredTorrents[0] ]
        self.assertEqual(expectedTorrentRecords, torrentRecords)
        queryAPI = [
            call(queries[0]),
            call(queries[1])
        ]
        queryMock.has_calls(queryAPI)
        filterEpisodeTorrentsMock.assert_called_with(fakeTPBQueryResponses[1], fakeMediaInfoRecord)
        logCalls = [
            call(f"Torrent search performed for: '{queries[0]}' - {len(fakeTPBQueryResponses[0])} results."),
            call(f"Torrent search performed for: '{queries[1]}' - {len(fakeTPBQueryResponses[1])} results."),
            call(f"{len(fakeTPBQueryResponses[1])} torrents filtered down to {len(fakeFilteredTorrents)}")
        ]
        loggingInfoMock.has_calls(logCalls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
