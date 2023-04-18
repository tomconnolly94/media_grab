#!/venv/bin/python

# external dependencies
import unittest
from unittest import mock
from unittest.mock import call

# internal dependencies
from src.test.unit_test.testUtilities import FakeFileSystemItem
from src.strategies.AuditEpisodeStrategy import AuditEpisodeStrategy


class TestAuditEpisodeStrategy(unittest.TestCase):

    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.postMoveDirectoryCleanup")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.moveFile")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.getTargetFile")
    @mock.patch("logging.info")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.requestTorrentPause")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.unWrapQBittorrentWrapperDir")
    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_AuditEpisodeStrategyAudit(self, downloadWasInitiatedByMediaGrabMock, unWrapQBittorrentWrapperDirMock, requestTorrentPauseMock, loggingInfoMock, getTargetFileMock, moveFileMock, postMoveDirectoryCleanupMock):

        # config fake values
        fakeFileSystemItemWrapper = FakeFileSystemItem(
            "fakeWrapperDir1Name", "fakeWrapperPath1Name")
        fakeFileSystemItem = FakeFileSystemItem(
            "fakeDir1Name", "fakePath1Name")
        fakeTargetFile = FakeFileSystemItem(
            "fakeTargetFileDir1Name", "fakeTargetFilePath1Name")

        # config mocks
        unWrapQBittorrentWrapperDirMock.return_value = fakeFileSystemItem
        getTargetFileMock.return_value = fakeTargetFile
        downloadWasInitiatedByMediaGrabMock.return_value = True
        moveFileMock.return_value = True
        postMoveDirectoryCleanupMock.return_value = True

        # create testable class
        auditEpisodeStrategy = AuditEpisodeStrategy()

        # run testable function - run 1: successful run
        result = auditEpisodeStrategy.audit(
            fakeFileSystemItemWrapper)

        # asserts
        self.assertTrue(result)
        downloadWasInitiatedByMediaGrabMock.assert_called_with(
            fakeFileSystemItemWrapper.name)
        unWrapQBittorrentWrapperDirMock.assert_called_with(
            fakeFileSystemItemWrapper)
        getTargetFileMock.assert_called_with(fakeFileSystemItem)
        requestTorrentPauseMock.assert_called_with(fakeFileSystemItem.name)
        loggingCalls = [
            call(
                f"{fakeFileSystemItem.name} has finished downloading and will be moved."),
        ]
        loggingInfoMock.assert_has_calls(loggingCalls)
        moveFileMock.assert_called_with(
            fakeTargetFile, fakeFileSystemItem, fakeFileSystemItemWrapper.name, fakeFileSystemItemWrapper.path)
        postMoveDirectoryCleanupMock.assert_called_with(
            fakeFileSystemItemWrapper.name, fakeTargetFile, fakeFileSystemItem, fakeFileSystemItemWrapper.path)
