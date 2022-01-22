# external dependencies
import unittest
import os
import mock
from mock import MagicMock

# internal dependencies
from src.interfaces.TheMovieDatabaseInterface import TheMovieDatabaseInterface

class TVMock():

    def __init__(self):
        pass

    def search(self):
        return [
            {
                "id": 1,
                "title": "fakeTVShowTitle1"
            },
            {
                "id": 2,
                "title": "fakeTVShowTitle2"
            }
        ]

    def similar(self):
        return [
            {
                "id": 3,
                "title": "fakeTVShowTitle3"
            },
            {
                "id": 4,
                "title": "fakeTVShowTitle4"
            }
        ]

class TestTheMovieDatabaseInterface(unittest.TestCase):

    @mock.patch("tmdbv3api.TV")
    def test_getShowReccomendation(self, tvMock):

        # config fake values
        tvMock.return_value = TVMock()
        inputTVShow = "friends"

        theMovieDatabaseInterface = TheMovieDatabaseInterface()

        # call testable function
        tvShowReccomendations = theMovieDatabaseInterface.getShowReccomendations(inputTVShow)

        # asserts
        self.assertEqual(["fakeTVShowTitle3", "fakeTVShowTitle4"], tvShowReccomendations)
        tvMock.search.assert_called_with(inputTVShow)
        tvMock.similar.assert_called_with(3)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
