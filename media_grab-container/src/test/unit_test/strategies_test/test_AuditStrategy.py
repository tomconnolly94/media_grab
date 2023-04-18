# external dependencies
import os
import unittest
from unittest import mock
from unittest.mock import MagicMock
from src.dataTypes.ProgramMode import PROGRAM_MODE
from src.dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP

# internal dependencies
from src.strategies.AuditStrategy import AuditStrategy
from src.test.unit_test.testUtilities import FakeFileSystemItem


class TestAuditStrategy(unittest.TestCase):

    @mock.patch("logging.info")
    @mock.patch("os.scandir")
    def test_unWrapQBittorrentWrapperDir(self, osScandirMock, loggingInfoMock):

        # config fake values
        fakeFileSystemItem = FakeFileSystemItem("fakeDirPath", "fakeDirName")
        fakeFileSystemSubItems = [
            FakeFileSystemItem("fakeSubDir1Path", "fakeSubDir1Name")
        ]

        # config mocks
        osScandirMock.return_value = fakeFileSystemSubItems

        # call testable function - run 1
        auditStrategy = AuditStrategy()
        actualSubItem = auditStrategy.unWrapQBittorrentWrapperDir(
            fakeFileSystemItem)

        # asserts
        self.assertEqual(fakeFileSystemSubItems[0], actualSubItem)

        # reconfig mocks
        osScandirMock.return_value = []

        # call testable function - run 1
        auditStrategy = AuditStrategy()
        actualSubItem = auditStrategy.unWrapQBittorrentWrapperDir(
            fakeFileSystemItem)

        # asserts
        loggingInfoMock.assert_called_with(
            f"Tried to browse past the directory created by qbittorrent ({fakeFileSystemItem.path}) but nothing was found inside.")


    @mock.patch("logging.info")
    @mock.patch("src.controllers.ErrorController.reportError")
    @mock.patch("src.utilities.AuditUtilities.getLargestItemInDir")
    @mock.patch("src.interfaces.FolderInterface.directoryExists")
    def test_getTargetFile(self, directoryExistsMock, getLargestItemInDirMock, reportErrorMock, loggingInfoMock):

        # config fake values
        fakeFileSystemItem = FakeFileSystemItem("fakeDirName1", "fakePath1")
        fakeTargetFile = FakeFileSystemItem("fakeDirName2", "fakePath2")

        # config mocks
        directoryExistsMock.side_effect = [True, False, True]
        getLargestItemInDirMock.return_value = fakeTargetFile

        # call testable function - run 1: fileSystemItem is a directory and largest file is returned successfully
        auditStrategy = AuditStrategy()
        actualTargetFile = auditStrategy.getTargetFile(fakeFileSystemItem)

        # asserts
        directoryExistsMock.assert_called_with(fakeFileSystemItem.path)
        getLargestItemInDirMock.assert_called_with(fakeFileSystemItem.path)
        loggingInfoMock.assert_called_with(
            f"{fakeFileSystemItem.name} is a directory. The file {fakeTargetFile.name} has been extracted as the media item of interest.")
        reportErrorMock.assert_not_called()
        self.assertEqual(fakeTargetFile, actualTargetFile)

        # reset mocks
        getLargestItemInDirMock.reset_mock()
        loggingInfoMock.reset_mock()
        reportErrorMock.reset_mock()

        # call testable function - run 2: fileSystemItem is not a directory
        actualTargetFile = auditStrategy.getTargetFile(
            fakeFileSystemItem)

        # asserts
        directoryExistsMock.assert_called_with(fakeFileSystemItem.path)
        getLargestItemInDirMock.assert_not_called()
        loggingInfoMock.assert_not_called()
        reportErrorMock.assert_not_called()
        self.assertEqual(fakeFileSystemItem, actualTargetFile)

        # reset mocks
        getLargestItemInDirMock.reset_mock()
        getLargestItemInDirMock.return_value = None
        loggingInfoMock.reset_mock()
        reportErrorMock.reset_mock()

        # call testable function - run 3: targetFile could not be extracted from directory
        actualTargetFile = auditStrategy.getTargetFile(
            fakeFileSystemItem)

        # asserts
        directoryExistsMock.assert_called_with(fakeFileSystemItem.path)
        getLargestItemInDirMock.assert_called_with(fakeFileSystemItem.path)
        loggingInfoMock.assert_not_called()
        reportErrorMock.assert_called_with(
            f"The fileSystemItem: {fakeFileSystemItem.name} is a directory but a targetFile could not be extracted. Skipping...")
        self.assertEqual(None, actualTargetFile)


    @mock.patch("src.utilities.AuditUtilities.ensureDirStructureExists")
    @mock.patch("src.utilities.AuditUtilities.extractEpisodeNumber")
    @mock.patch("src.utilities.AuditUtilities.extractSeasonNumber")
    @mock.patch("src.utilities.AuditUtilities.extractShowName")
    @mock.patch("os.getenv")
    def test_getProspectiveFilePath(self, osGetenvMock, extractShowNameMock, extractSeasonNumberMock, extractEpisodeNumberMock, ensureDirStructureExistsMock):

        # config fake data
        fakeTargetTvDir = "fakeTargetTvDir"
        fakeShowName = "Fakeshowname"
        fakeSeasonNumber = 2
        fakeEpisodeNumber = 2
        fakeMediaGrabId = f"{fakeShowName}--s{fakeSeasonNumber}e{fakeEpisodeNumber}"
        mode = PROGRAM_MODE.TV
        fakeExtension = ".mp4"
        fakeSeasonDir = f"Season {fakeSeasonNumber}"

        # expected values
        expectedProspectiveFilePath = os.path.join(
            fakeTargetTvDir, fakeShowName, fakeSeasonDir, f"{fakeShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}{fakeExtension}")
        expectedTvShowDir = os.path.join(fakeTargetTvDir, fakeShowName)
        expectedSeasonDir = os.path.join(expectedTvShowDir, fakeSeasonDir)

        # config mocks
        osGetenvMock.return_value = fakeTargetTvDir
        extractShowNameMock.return_value = fakeShowName
        extractSeasonNumberMock.return_value = fakeSeasonNumber
        extractEpisodeNumberMock.return_value = fakeEpisodeNumber

        # run testable function - run 1: success
        auditStrategy = AuditStrategy()
        actualProspectiveFilePath = auditStrategy.getProspectiveFilePath(
            fakeMediaGrabId, mode, fakeExtension)

        # asserts
        self.assertEqual(expectedProspectiveFilePath,
                         actualProspectiveFilePath)
        osGetenvMock.assert_called_with(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
        extractShowNameMock.assert_called_with(fakeMediaGrabId)
        extractSeasonNumberMock.assert_called_with(fakeMediaGrabId)
        extractEpisodeNumberMock.assert_called_with(fakeMediaGrabId)
        ensureDirStructureExistsMock.assert_called_with(
            expectedTvShowDir, expectedSeasonDir)

        # reconfig mocks
        osGetenvMock.return_value = fakeTargetTvDir
        extractShowNameMock.return_value = fakeShowName
        extractSeasonNumberMock.return_value = None
        extractEpisodeNumberMock.return_value = fakeEpisodeNumber
        ensureDirStructureExistsMock.reset_mock()

        # run testable function - run 2: failure
        auditStrategy = AuditStrategy()
        actualProspectiveFilePath = auditStrategy.getProspectiveFilePath(
            fakeMediaGrabId, mode, fakeExtension)

        # asserts
        self.assertIsNone(actualProspectiveFilePath)
        osGetenvMock.assert_called_with(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
        extractShowNameMock.assert_called_with(fakeMediaGrabId)
        extractSeasonNumberMock.assert_called_with(fakeMediaGrabId)
        extractEpisodeNumberMock.assert_called_with(fakeMediaGrabId)
        ensureDirStructureExistsMock.assert_not_called()


    @mock.patch("logging.info")
    @mock.patch("src.interfaces.QBittorrentInterface.getInstance")
    def test_requestTorrentPause(self, qbittorrentInterfaceGetInstanceMock, loggingInfoMock):

        # config fake data
        fakeTorrentName = "fakeTorrentName"

        # config mocks
        qbittorrentInterfaceInstanceMock = MagicMock()  # create mock for instance
        # assign mocked instance to return_value for mocked getInstance()
        qbittorrentInterfaceGetInstanceMock.return_value = qbittorrentInterfaceInstanceMock
        qbittorrentInterfaceInstanceMock.pauseTorrent = MagicMock()
        qbittorrentInterfaceInstanceMock.pauseTorrent.side_effect = [
            True, False]

        # call testable function - run 1
        auditStrategy = AuditStrategy()
        auditStrategy.requestTorrentPause(fakeTorrentName)

        # asserts
        qbittorrentInterfaceGetInstanceMock.assert_called_with()
        qbittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(
            fakeTorrentName)
        loggingInfoMock.assert_called_with(
            f"Paused torrent activity: ({fakeTorrentName})")

        # reset mocks
        qbittorrentInterfaceGetInstanceMock.reset_mock()
        qbittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()
        loggingInfoMock.reset_mock()

        # call testable function - run 2
        auditStrategy = AuditStrategy()
        auditStrategy.requestTorrentPause(fakeTorrentName)

        # asserts
        qbittorrentInterfaceGetInstanceMock.assert_called_with()
        qbittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(
            fakeTorrentName)
        loggingInfoMock.assert_called_with(
            f"Failed to pause torrent activity: ({fakeTorrentName})")


    @mock.patch("os.rename")
    @mock.patch("src.interfaces.FolderInterface.fileExists")
    @mock.patch("src.strategies.AuditStrategy.AuditStrategy.getProspectiveFilePath")
    @mock.patch("src.utilities.AuditUtilities.extractExtension")
    @mock.patch("logging.info")
    def test_moveFile(self, loggingInfoMock, extractExtensionMock, getProspectiveFilePathMock, fileExistsMock, osRenameMock):

        # config fake values
        fakeFileSystemItem = FakeFileSystemItem(
            "fakeDir1Name", "fakePath1Name")
        fakeTargetFile = FakeFileSystemItem(
            "fakeTargetFileDir1Name", "fakeTargetFilePath1Name")
        fakeExtension = ".mp4"
        fakeProspectiveFile = "fakeProspectiveFile"

        # config mocks
        extractExtensionMock.return_value = fakeExtension
        getProspectiveFilePathMock.return_value = fakeProspectiveFile
        fileExistsMock.return_value = False

        # create testable class
        auditEpisodeStrategy = AuditStrategy()

        # run testable function - run 1: successful run
        auditEpisodeStrategy.moveFile(
            fakeTargetFile, fakeFileSystemItem, fakeFileSystemItem.name, fakeFileSystemItem.path)

        # asserts
        loggingInfoMock.assert_called_with(
            f"Moved '{fakeTargetFile.path}' to '{fakeProspectiveFile}'")
        extractExtensionMock.assert_called_with(fakeTargetFile.name)
        getProspectiveFilePathMock.assert_called_with(
            fakeFileSystemItem.name, PROGRAM_MODE.TV, fakeExtension)
        fileExistsMock.assert_called_with(fakeProspectiveFile)
        osRenameMock.assert_called_with(
            fakeTargetFile.path, fakeProspectiveFile)
