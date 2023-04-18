# external dependencies
import unittest
import os
from unittest.mock import call
import shutil
from unittest import mock

# internal dependencies
from src.utilities import AuditUtilities
from src.test.unit_test.controllers_test.test_CompletedDownloadsController import FakeFileSystemItem

# fake directories for use across multiple tests
fakeTargetTvDir = "test/dummy_directories/tv"
fakeDumpCompleteDir = "test/dummy_directories/dump_complete"
fakeRecycleBinDir = "test/dummy_directories/recycle_bin"

def cleanUpDirs(directories, downloadingItems):
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                os.remove(os.path.join(root, file))

            for directory in dirs:
                shutil.rmtree(os.path.join(root, directory))


class TestAuditUtilities(unittest.TestCase):

    def test_downloadWasInitiatedByMediaGrab(self):

        passingValues = [
            "showName--s1e1",
            "showName-s1e2--s1e2",
            "showName--s1"
        ]

        failingValues = [
            "showName--s1er",
            "showName-s1e2",
            "s1e2",
            "--s1e2",
            ".--s1e2",
            "showName2--s1s2"
            "showName-s1e2--s2e"
        ]

        for value in passingValues:
            success = AuditUtilities.downloadWasInitiatedByMediaGrab(
                value)
            self.assertTrue(success)

        for value in failingValues:
            success = AuditUtilities.downloadWasInitiatedByMediaGrab(
                value)
            self.assertFalse(success)

    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_extractShowNameMediaGrabDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedFakeShowName = "fake show"
        fakeShowName = "fake show--s1e1"

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = True

        actualFakeShowName = AuditUtilities.extractShowName(
            fakeShowName)
        self.assertEqual(expectedFakeShowName, actualFakeShowName)

        # check empty string
        self.assertEqual(
            None, AuditUtilities.extractShowName(""))

    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_extractShowNameManualDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedFakeShowName = "fake show"
        fakeShowNamesSuccessful = [
            "fake.Show ",
            "fake Show - S01",
            "fake.Show - S01E01",
            "fake.Show -   S01E01",
            "fake.Show.S01E01",
            "fake.Show.S01.E01",
            "Fake.Show.S01.E01",
            "fake.Show.S01"
        ]

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = False

        for fakeShowName in fakeShowNamesSuccessful:
            actualFakeShowName = AuditUtilities.extractShowName(
                fakeShowName)
            self.assertEqual(expectedFakeShowName, actualFakeShowName)

    @mock.patch("src.controllers.ErrorController.reportError")
    @mock.patch("re.match")
    def test_extractShowNameManualDownloadFails(self, reMatchMock, reportErrorMock):

        # config fake data
        fakeException = AttributeError("fakeException")

        # config mocks
        reMatchMock.side_effect = fakeException

        # check empty string
        self.assertEqual(
            None, AuditUtilities.extractShowName(""))
        reportErrorMock.assert_called_with(
            "Exception occurred when extracting season number with regex", exception=fakeException, sendEmail=True)

    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_extractSeasonNumberMediaGrabDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedSeasonNumber = 2
        fakeShowName = "fake show--s2e1"

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = True

        actualFakeSeasonNumber = AuditUtilities.extractSeasonNumber(
            fakeShowName)
        self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(
            None, AuditUtilities.extractSeasonNumber(""))

    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_extractSeasonNumberManualDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedSeasonNumber = 1
        fakeShowNamesSuccessful = [
            "fakeShow - S01",
            "fakeShow - S01E01",
            "fakeShow -   S01E01",
            "fakeShow.S01E01",
            "fakeShow.S01.E01",
            "FakeShow.S01.E01",
            "fakeShow.S01"
        ]

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = False

        for fakeShowName in fakeShowNamesSuccessful:
            actualFakeSeasonNumber = AuditUtilities.extractSeasonNumber(
                fakeShowName)
            self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(
            None, AuditUtilities.extractSeasonNumber(""))

    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_extractEpisodeNumberMediaGrabDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedSeasonNumber = 3
        fakeShowName = "fake show--s1e3"

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = True

        actualFakeSeasonNumber = AuditUtilities.extractEpisodeNumber(
            fakeShowName)
        self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(
            None, AuditUtilities.extractSeasonNumber(""))

    @mock.patch("src.utilities.AuditUtilities.downloadWasInitiatedByMediaGrab")
    def test_extractEpisodeNumberManualDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedSeasonNumber = 2
        fakeShowNamesSuccessful = [
            "fakeShow - S01E02",
            "fakeShow -   S01E02",
            "fakeShow.S01E02",
            "fakeShow.S01.E02",
            "FakeShow.S01.E02",
        ]
        fakeShowNamesUnsuccessful = [
            "fakeShow - S01",
            "fakeShow.S01"
        ]

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = False

        for fakeShowName in fakeShowNamesSuccessful:
            actualFakeSeasonNumber = AuditUtilities.extractEpisodeNumber(
                fakeShowName)
            self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        for fakeShowName in fakeShowNamesUnsuccessful:
            actualFakeSeasonNumber = AuditUtilities.extractEpisodeNumber(
                fakeShowName)
            self.assertEqual(None, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(
            None, AuditUtilities.extractSeasonNumber(""))

    def test_extractExtension(self):
        expectedExtension = ".mp4"
        testFileNames = [
            f"filename1{expectedExtension}",
            f"filename1.fakeext{expectedExtension}",
            f"filename1.mp3{expectedExtension}",
            f"filename1.jpg{expectedExtension}",
            f"x{expectedExtension}",
            f" {expectedExtension}"
        ]

        for fileName in testFileNames:
            actualExtension = AuditUtilities.extractExtension(
                fileName)
            self.assertEqual(expectedExtension, actualExtension)

    @mock.patch("src.controllers.ErrorController.reportError")
    def test_reportItemAlreadyExists(self, reportErrorMock):
        fakeNewItemLocation = "fakeNewItemLocation"
        fakeTorrentName = "fakeTorrentName"

        AuditUtilities.reportItemAlreadyExists(
            fakeNewItemLocation, fakeTorrentName)

        expectedErrorString = f"Downloaded torrent: {fakeTorrentName} and attempted to move it to {fakeNewItemLocation} but this target already exists."

        reportErrorMock.assert_called_with(expectedErrorString, sendEmail=True)

    @mock.patch("logging.info")
    @mock.patch("os.path.getsize")
    @mock.patch("os.scandir")
    def test_getLargestItemInDir(self, osScandirMock, osGetsizeMock, loggingInfoMock):

        # config fake data
        expectedLargestItem = FakeFileSystemItem(
            "fakeItem3Name", "fakeItem3Path")
        fakeDirectoryItems = [
            FakeFileSystemItem("fakeItem1Name", "fakeItem1Path"),
            FakeFileSystemItem("fakeItem2Name", "fakeItem2Path"),
            expectedLargestItem
        ]
        fakeDirectory = "fakeDirectory"

        # config mocks
        osScandirMock.side_effect = [fakeDirectoryItems, []]
        osGetsizeMock.side_effect = [1, 2, 3]

        # call testable function - run 1
        actualLargestItemInDir = AuditUtilities.getLargestItemInDir(
            fakeDirectory)

        # asserts
        osScandirMock.assert_called_with(fakeDirectory)
        fakeGetsizeCalls = [
            call(f"{fakeDirectory}/{fakeDirectoryItems[0].name}"),
            call(f"{fakeDirectory}/{fakeDirectoryItems[1].name}"),
            call(f"{fakeDirectory}/{fakeDirectoryItems[2].name}")
        ]
        osGetsizeMock.assert_has_calls(fakeGetsizeCalls)
        self.assertEqual(expectedLargestItem, actualLargestItemInDir)
        loggingInfoMock.assert_not_called()

        # call testable function - run 2
        actualLargestItemInDir = AuditUtilities.getLargestItemInDir(
            fakeDirectory)

        # asserts
        self.assertIsNone(actualLargestItemInDir)
        loggingInfoMock.assert_called_with(
            f"Tried to getLargestItemInDir from {fakeDirectory} but a file cold not be located")

    @mock.patch("src.controllers.ErrorController.reportError")
    @mock.patch("src.interfaces.FolderInterface.createDirectory")
    @mock.patch("src.interfaces.FolderInterface.directoryExists")
    def test_ensureDirStructureExists(self, directoryExistsMock, createDirectoryMock, reportErrorMock):

        # config fake values
        fakeTvShowDir = "fakeTvShowDir"
        fakeSeasonDir = "fakeSeasonDir"

        # config mocks
        directoryExistsMock.side_effect = [False, False]

        # call testable function - run 1
        operationSuccess = AuditUtilities.ensureDirStructureExists(
            fakeTvShowDir, fakeSeasonDir)

        # asserts
        calls = [call(fakeTvShowDir), call(fakeSeasonDir)]
        directoryExistsMock.assert_has_calls(calls)
        createDirectoryMock.assert_has_calls(calls)
        reportErrorMock.assert_not_called()
        self.assertTrue(operationSuccess)

        # reset mocks
        directoryExistsMock.reset_mock()
        directoryExistsMock.side_effect = [True, False]
        createDirectoryMock.reset_mock()

        # call testable function - run 2
        operationSuccess = AuditUtilities.ensureDirStructureExists(
            fakeTvShowDir, fakeSeasonDir)

        # asserts
        calls = [call(fakeTvShowDir), call(fakeSeasonDir)]
        directoryExistsMock.assert_has_calls(calls)
        createDirectoryMock.assert_has_calls(calls[1:])
        reportErrorMock.assert_not_called()
        self.assertTrue(operationSuccess)

        # reset mocks
        directoryExistsMock.reset_mock()
        directoryExistsMock.side_effect = [False, True]
        createDirectoryMock.reset_mock()

        # call testable function - run 3
        operationSuccess = AuditUtilities.ensureDirStructureExists(
            fakeTvShowDir, fakeSeasonDir)

        # asserts
        calls = [call(fakeTvShowDir), call(fakeSeasonDir)]
        directoryExistsMock.assert_has_calls(calls)
        createDirectoryMock.assert_has_calls(calls[:0])
        reportErrorMock.assert_not_called()
        self.assertTrue(operationSuccess)

        # reset mocks
        directoryExistsMock.reset_mock()
        directoryExistsMock.side_effect = [False]
        createDirectoryMock.reset_mock()
        fakeException = Exception()
        createDirectoryMock.side_effect = fakeException

        # call testable function - run 4
        operationSuccess = AuditUtilities.ensureDirStructureExists(
            fakeTvShowDir, fakeSeasonDir)

        # asserts
        directoryExistsMock.assert_called_with(fakeTvShowDir)
        createDirectoryMock.assert_called_with(fakeTvShowDir)
        reportErrorMock.assert_called_with(
            "Directory structure could not be completed", exception=fakeException, sendEmail=True)
        self.assertFalse(operationSuccess)
