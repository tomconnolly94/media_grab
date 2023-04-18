# external dependencies
import unittest
from unittest import mock
from unittest.mock import MagicMock

# internal dependencies
from src.interfaces.TheMovieDatabaseInterface import TheMovieDatabaseInterface

class TVShowMock():

    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title


class TestTheMovieDatabaseInterface(unittest.TestCase):

    @mock.patch("src.interfaces.TheMovieDatabaseInterface.TV")
    def test_getShowReccomendation(self, tvMock):

        # config fake values
        tvMagicMock = MagicMock()
        tvMagicMock.search.return_value = [
            TVShowMock(1, "fakeTVShowTitle1"),
            TVShowMock(2, "fakeTVShowTitle2")
        ]
        tvMagicMock.similar.return_value = [
            {
                "id": 3,
                "original_name": "fakeTVShowTitle3"
            },
            {
                "id": 4,
                "original_name": "fakeTVShowTitle4"
            }
        ]
        tvMock.return_value = tvMagicMock

        inputTVShow = "friends"

        theMovieDatabaseInterface = TheMovieDatabaseInterface()

        # call testable function
        tvShowReccomendations = theMovieDatabaseInterface.getShowReccomendations(inputTVShow)

        # asserts
        self.assertEqual(["fakeTVShowTitle3", "fakeTVShowTitle4"], tvShowReccomendations)
        tvMock.return_value.search.assert_called_with(inputTVShow)
        tvMock.return_value.similar.assert_called_with(1)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
