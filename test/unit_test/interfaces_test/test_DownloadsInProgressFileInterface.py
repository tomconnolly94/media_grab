# external dependencies
import unittest
import mock
from unittest.mock import mock_open

# internal dependencies
from interfaces import DownloadsInProgressFileInterface


# constants
openReadMockDataEmpty = '{ "tv_seasons": [], "tv_episodes": [], "fakeMediaType": [] }'
openReadMockDataWithEntries = '{ "tv_seasons": [], "tv_episodes": [], "fakeMediaType": ["fakeMediaName1", "fakeMediaName2"] }'
#fake data
fakeMediaName = "fakeMediaName"
fakeMediaType = "fakeMediaType"


class TestDownloadsInProgressFileInterface(unittest.TestCase):

    @mock.patch("interfaces.DownloadsInProgressFileInterface.updateFile")
    @mock.patch("os.path.exists")
    def test_notifyDownloadStarted(self, fileExistsMock, updateFileMock):

        #mock init
        fileExistsMock.return_value = True

        DownloadsInProgressFileInterface.notifyDownloadStarted(fakeMediaName, fakeMediaType)

        actualLambda = updateFileMock.call_args.args[0]
        media = { "tv_seasons": [], "tv_episodes": [], fakeMediaType: [] }
        actualLambda(media)

        self.assertEqual(1, len(media[fakeMediaType]))
        self.assertEqual(fakeMediaName, media[fakeMediaType][0])


    @mock.patch("interfaces.DownloadsInProgressFileInterface.updateFile")
    @mock.patch("os.path.exists")
    def test_notifyDownloadFinished(self, fileExistsMock, updateFileMock):

        #mock init
        fileExistsMock.return_value = True

        DownloadsInProgressFileInterface.notifyDownloadFinished(fakeMediaName, fakeMediaType)

        actualLambda = updateFileMock.call_args.args[0]
        media = { "tv_seasons": [], "tv_episodes": [], fakeMediaType: [fakeMediaName] }
        actualLambda(media)

        self.assertEqual(0, len(media[fakeMediaType]))


    @mock.patch("builtins.open", new_callable=mock_open, read_data=openReadMockDataEmpty)
    def test_updateFileAdd(self, openMock):

        # prepare injectable operation
        def operation(media, mediaName=fakeMediaName, mediaType=fakeMediaType):
            media[mediaType].append(mediaName)
            return media

        # run testable function
        DownloadsInProgressFileInterface.updateFile(operation)

        expectedResultDict = { "tv_seasons": [], "tv_episodes": [], fakeMediaType: [fakeMediaName] }
        # get handle to mocked 'builtins.open' object 
        handle = openMock()

        handle.write.assert_called_once_with(expectedResultDict)


    @mock.patch("builtins.open", new_callable=mock_open, read_data=openReadMockDataWithEntries)
    def test_updateFileRemove(self, openMock):

        # prepare injectable operation
        def operation(media, mediaName="fakeMediaName1", mediaType=fakeMediaType):
            media[mediaType].remove(mediaName)
            return media

        # run testable function
        DownloadsInProgressFileInterface.updateFile(operation)

        expectedResultDict = { "tv_seasons": [], "tv_episodes": [], fakeMediaType: ["fakeMediaName2"] }
        # get handle to mocked 'builtins.open' object 
        handle = openMock()

        handle.write.assert_called_once_with(expectedResultDict)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
