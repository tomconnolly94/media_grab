#!/venv/bin/python

# external dependencies
import unittest
from unittest import mock
from mock import call

# internal dependencies
from test.unit_test.testUtilities import FakeFileSystemItem
from strategies.AuditSeasonStrategy import AuditSeasonStrategy


class TestAuditSeasonStrategy(unittest.TestCase):

    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.postMoveDirectoryCleanup")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.moveFile")
    @mock.patch("src.utilities.AuditUtilities.extractEpisodeNumber")
    @mock.patch("logging.info")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.requestTorrentPause")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.getTargetFiles")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.unWrapQBittorrentWrapperDir")
    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_AuditSeasonStrategyAudit(self, downloadWasInitiatedByMediaGrabMock, unWrapQBittorrentWrapperDirMock, getTargetFilesMock, requestTorrentPauseMock, loggingInfoMock, extractEpisodeNumberMock, moveFileMock, postMoveDirectoryCleanupMock):

        # config fake values
        fakeFileSystemItemWrapper = FakeFileSystemItem(
            "fakeWrapperDir1Name--s1", "fakeWrapperPath1Name")
        fakeFileSystemItem = FakeFileSystemItem(
            "fakeDir1Name", "fakePath1Name")
        fakeTargetFiles = [
            FakeFileSystemItem("fakeTargetFileDir1Name", "fakeTargetFilePath1Name"),
            FakeFileSystemItem("fakeTargetFileDir2Name", "fakeTargetFilePath2Name"),
            FakeFileSystemItem("fakeTargetFileDir3Name", "fakeTargetFilePath3Name")
        ]
        fakeEpisodeNumbers = [1, 2, 3]

        # config mocks
        unWrapQBittorrentWrapperDirMock.return_value = fakeFileSystemItem
        getTargetFilesMock.return_value = fakeTargetFiles
        downloadWasInitiatedByMediaGrabMock.return_value = True
        moveFileMock.return_value = True
        postMoveDirectoryCleanupMock.return_value = True
        extractEpisodeNumberMock.side_effect = fakeEpisodeNumbers

        # create testable class
        auditSeasonStrategy = AuditSeasonStrategy()

        # run testable function - run 1: successful run
        result = auditSeasonStrategy.audit(
            fakeFileSystemItemWrapper)

        # asserts
        self.assertTrue(result)
        downloadWasInitiatedByMediaGrabMock.assert_called_with(
            fakeFileSystemItemWrapper.name)
        unWrapQBittorrentWrapperDirMock.assert_called_with(
            fakeFileSystemItemWrapper)
        getTargetFilesMock.assert_called_with(fakeFileSystemItem)
        requestTorrentPauseMock.assert_called_with(fakeFileSystemItem.name)
        loggingCalls = [
            call(
                f"{fakeFileSystemItem.name} has finished downloading and will be moved."),
        ]
        loggingInfoMock.assert_has_calls(loggingCalls)
        extractEpisodeNumberMockCalls = [
            call(fakeTargetFiles[0].name),
            call(fakeTargetFiles[1].name),
            call(fakeTargetFiles[2].name)
        ]
        extractEpisodeNumberMock.assert_has_calls(
            extractEpisodeNumberMockCalls)

        moveFileMockCalls = [
            call(fakeTargetFiles[0], fakeFileSystemItem,
                 f"{fakeFileSystemItemWrapper.name}e{fakeEpisodeNumbers[0]}"),
            call(fakeTargetFiles[1], fakeFileSystemItem,
                 f"{fakeFileSystemItemWrapper.name}e{fakeEpisodeNumbers[1]}"),
            call(fakeTargetFiles[2], fakeFileSystemItem,
                 f"{fakeFileSystemItemWrapper.name}e{fakeEpisodeNumbers[2]}")
        ]
        moveFileMock.assert_has_calls(moveFileMockCalls)
        postMoveDirectoryCleanupMock.assert_called_with(
            fakeFileSystemItemWrapper.name, None, fakeFileSystemItem, fakeFileSystemItemWrapper.path)
