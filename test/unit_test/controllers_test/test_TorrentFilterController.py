import unittest

from controllers import TorrentFilterController

class TestTorrentFilterController(unittest.TestCase):

    def test_filterSeasonTorrentPageUrls(self):

        mediaData = {
            "name": "fake_tv_show_name",
            "typeSpecificData": {
                "latestSeason": "1",
                "latestEpisode": "2"
            }
        }

        expectedSeason = str(int(mediaData["typeSpecificData"]["latestSeason"]) + 1)
        mediaName = mediaData["name"]
        fakeUrl = "http://fakeurl.com/"

        torrentPageUrls = [
            f'{fakeUrl}{mediaName}',
            f'{fakeUrl}{mediaName}-season',
            f'{fakeUrl}{mediaName}-Season',
            f'{fakeUrl}{mediaName}-episode',
            f'{fakeUrl}{mediaName}-irrelevant-word',
            f'{fakeUrl}{mediaName}-seasoning',
            f'{fakeUrl}{mediaName}-season-{expectedSeason}',
            f'{fakeUrl}{mediaName}-seasons-{expectedSeason}',
            f'{fakeUrl}{mediaName}-Season-{expectedSeason}',
            f'{fakeUrl}{mediaName}-season-{str(int(expectedSeason) + 1)}',
            f'{fakeUrl}{mediaName}-seasons-{str(int(expectedSeason) + 1)}'
        ]
        expectedFilteredTorrentPageUrls = [
            f'{fakeUrl}{mediaName}-season-{expectedSeason}',
            f'{fakeUrl}{mediaName}-Season-{expectedSeason}'
        ]

        actualFilteredTorrentPageUrls = TorrentFilterController.filterSeasonTorrentPageUrls(torrentPageUrls, mediaData)

        self.assertEqual(expectedFilteredTorrentPageUrls, actualFilteredTorrentPageUrls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
