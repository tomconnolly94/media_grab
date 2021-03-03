# external dependencies
import unittest
import mock
from unittest.mock import mock_open
import json

# internal dependencies
from interfaces import DownloadsInProgressFileInterface
from data_types.ProgramMode import PROGRAM_MODE
from data_types.ProgramModeMap import PROGRAM_MODE_MAP

# constants
openReadMockDataEmpty = '{ "tv-seasons": [], "tv-episodes": [] }'
openReadMockDataWithEntries = '{ "tv-seasons": [], "tv-episodes": ["fakeMediaName1", "fakeMediaName2"] }'
#fake data
fakeMediaName = "fakeMediaName"
fakeMediaType = PROGRAM_MODE.TV_EPISODES


class TestDownloadsInProgressFileInterface(unittest.TestCase):

    @mock.patch("interfaces.DownloadsInProgressFileInterface.updateFile")
    @mock.patch("os.path.exists")
    def test_notifyDownloadStarted(self, fileExistsMock, updateFileMock):

        #mock init
        fileExistsMock.return_value = True

        DownloadsInProgressFileInterface.notifyDownloadStarted(fakeMediaName, fakeMediaType)

        actualLambda = updateFileMock.call_args.args[0]
        media = { "tv-seasons": [], "tv-episodes": [] }
        actualLambda(media)

        self.assertEqual(1, len(media["tv-episodes"]))
        self.assertEqual(fakeMediaName, media["tv-episodes"][0])


    @mock.patch("interfaces.DownloadsInProgressFileInterface.updateFile")
    @mock.patch("os.path.exists")
    def test_notifyDownloadFinished(self, fileExistsMock, updateFileMock):

        #mock init
        fileExistsMock.return_value = True

        DownloadsInProgressFileInterface.notifyDownloadFinished(fakeMediaName, fakeMediaType)

        actualLambda = updateFileMock.call_args.args[0]
        media = { "tv-seasons": [], "tv-episodes": [fakeMediaName] }
        actualLambda(media)

        self.assertEqual(0, len(media["tv-episodes"]))


    @mock.patch("builtins.open", new_callable=mock_open, read_data=openReadMockDataEmpty)
    def test_updateFileAdd(self, openMock):

        typeKey = PROGRAM_MODE_MAP[fakeMediaType]

        # prepare injectable operation
        def operation(media, mediaName=fakeMediaName, typeKey=typeKey):
            media[typeKey].append(mediaName)
            return media

        # run testable function
        DownloadsInProgressFileInterface.updateFile(operation)

        expectedResultDict = { "tv-seasons": [], "tv-episodes": [fakeMediaName] }
        # get handle to mocked 'builtins.open' object 
        handle = openMock()

        handle.write.assert_called_once_with(json.dumps(expectedResultDict))


    @mock.patch("builtins.open", new_callable=mock_open, read_data=openReadMockDataWithEntries)
    def test_updateFileRemove(self, openMock):

        typeKey = PROGRAM_MODE_MAP[fakeMediaType]

        # prepare injectable operation
        def operation(media, mediaName="fakeMediaName1", typeKey=typeKey):
            media[typeKey].remove(mediaName)
            return media

        # run testable function
        DownloadsInProgressFileInterface.updateFile(operation)

        expectedResultDict = { "tv-seasons": [], "tv-episodes": ["fakeMediaName2"] }
        # get handle to mocked 'builtins.open' object 
        handle = openMock()

        handle.write.assert_called_once_with(json.dumps(expectedResultDict))


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
