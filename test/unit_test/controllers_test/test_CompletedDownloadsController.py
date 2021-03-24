# external dependencies
import unittest
import mock
import os
from unittest.mock import call
import shutil
from mock import MagicMock

# internal dependencies
from controllers import CompletedDownloadsController
from dataTypes.ProgramMode import PROGRAM_MODE 
from dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP

# fake directories for use across multiple tests
fakeTargetTvDir = "test/dummy_directories/tv"
fakeDumpCompleteDir = "test/dummy_directories/dump_complete"
fakeRecycleBinDir = "test/dummy_directories/recycle_bin"

class FakeFileSystemItem:
    
    def __init__(self, dirName, path):
        self.name = dirName
        self.path = path

# re-usable getEnvMock function
def getEnvMockFunc(param):
    if param == "TV_TARGET_DIR":
        return fakeTargetTvDir
    elif param == "DUMP_COMPLETE_DIR":
        return fakeDumpCompleteDir
    elif param == "RECYCLE_BIN_DIR":
        return fakeRecycleBinDir
    else:
        assert(None)
        
def cleanUpDirs(directories, downloadingItems):
    for dir in directories:
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file in downloadingItems:
                    os.remove(os.path.join(root, file))

            downloadingItemDirs = [ item.split("/")[0] for item in downloadingItems ]
            for dir in dirs:
                if dir in downloadingItemDirs:
                    shutil.rmtree(os.path.join(root, dir))


class TestCompletedDownloadsController(unittest.TestCase):


    def test_downloadWasInitiatedByMediaGrab(self):

        passingValues = [ 
            "showName--s1e1",
            "showName-s1e2--s1e2",
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
            self.assertTrue(
                CompletedDownloadsController.downloadWasInitiatedByMediaGrab(value))

        for value in failingValues:
            self.assertFalse(
                CompletedDownloadsController.downloadWasInitiatedByMediaGrab(value))


    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
    def test_extractShowNameMediaGrabDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedFakeShowName = "fake show"
        fakeShowName = "fake show--s1e1"

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = True

        actualFakeShowName = CompletedDownloadsController.extractShowName(fakeShowName)
        self.assertEqual(expectedFakeShowName, actualFakeShowName)
        
        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractShowName(""))

    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
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
            actualFakeShowName = CompletedDownloadsController.extractShowName(
                fakeShowName)
            self.assertEqual(expectedFakeShowName, actualFakeShowName)

        # check empty string
        self.assertEqual(
            None, CompletedDownloadsController.extractShowName(""))


    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
    def test_extractSeasonNumberMediaGrabDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedSeasonNumber = 2
        fakeShowName = "fake show--s2e1"

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = True

        actualFakeSeasonNumber = CompletedDownloadsController.extractSeasonNumber(fakeShowName)
        self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractSeasonNumber(""))


    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
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
            actualFakeSeasonNumber = CompletedDownloadsController.extractSeasonNumber(
                fakeShowName)
            self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(
            None, CompletedDownloadsController.extractSeasonNumber(""))


    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
    def test_extractEpisodeNumberMediaGrabDownload(self, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        expectedSeasonNumber = 3
        fakeShowName = "fake show--s1e3"

        # config fake mocks
        downloadWasInitiatedByMediaGrabMock.return_value = True

        actualFakeSeasonNumber = CompletedDownloadsController.extractEpisodeNumber(fakeShowName)
        self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractSeasonNumber(""))


    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
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
            actualFakeSeasonNumber = CompletedDownloadsController.extractEpisodeNumber(
                fakeShowName)
            self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        for fakeShowName in fakeShowNamesUnsuccessful:
            actualFakeSeasonNumber = CompletedDownloadsController.extractEpisodeNumber(
                fakeShowName)
            self.assertEqual(None, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(
            None, CompletedDownloadsController.extractSeasonNumber(""))


    def test_extractExtension(self):
        expectedExtension = ".mp4"
        testFileNames=[
            f"filename1{expectedExtension}",
            f"filename1.fakeext{expectedExtension}",
            f"filename1.mp3{expectedExtension}",
            f"filename1.jpg{expectedExtension}",
            f"x{expectedExtension}",
            f" {expectedExtension}"
        ]

        for fileName in testFileNames:
            actualExtension = CompletedDownloadsController.extractExtension(fileName)
            self.assertEqual(expectedExtension, actualExtension)


    @mock.patch("controllers.ErrorController.reportError")
    def test_reportItemAlreadyExists(self, reportErrorMock):
        fakeNewItemLocation = "fakeNewItemLocation"
        fakeTorrentName = "fakeTorrentName"
        
        CompletedDownloadsController.reportItemAlreadyExists(fakeNewItemLocation, fakeTorrentName)

        expectedErrorString = f"Downloaded torrent: {fakeTorrentName} and attempted to move it to {fakeNewItemLocation} but this target already exists."

        reportErrorMock.assert_called_with(expectedErrorString, sendEmail=True)


    @mock.patch("logging.info")
    @mock.patch("os.path.getsize")
    @mock.patch("os.scandir")
    def test_getLargestItemInDir(self, osScandirMock, osGetsizeMock, loggingInfoMock):

        # config fake data
        expectedLargestItem = FakeFileSystemItem("fakeItem3Name", "fakeItem3Path")
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
        actualLargestItemInDir = CompletedDownloadsController.getLargestItemInDir(fakeDirectory)

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
        actualLargestItemInDir = CompletedDownloadsController.getLargestItemInDir(fakeDirectory)
        
        # asserts
        self.assertIsNone(actualLargestItemInDir)
        loggingInfoMock.assert_called_with(f"Tried to getLargestItemInDir from {fakeDirectory} but a file cold not be located")


    @mock.patch("logging.info")
    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    def test_requestTorrentPause(self, qbittorrentInterfaceGetInstanceMock, loggingInfoMock):        

        # config fake data
        fakeTorrentName = "fakeTorrentName"

        # config mocks        
        qbittorrentInterfaceInstanceMock = MagicMock() # create mock for instance
        # assign mocked instance to return_value for mocked getInstance()
        qbittorrentInterfaceGetInstanceMock.return_value = qbittorrentInterfaceInstanceMock
        qbittorrentInterfaceInstanceMock.pauseTorrent = MagicMock()
        qbittorrentInterfaceInstanceMock.pauseTorrent.side_effect = [True, False]

        # call testable function - run 1
        CompletedDownloadsController.requestTorrentPause(fakeTorrentName)

        # asserts
        qbittorrentInterfaceGetInstanceMock.assert_called_with()
        qbittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeTorrentName)
        loggingInfoMock.assert_called_with(f"Paused torrent activity: ({fakeTorrentName})")

        # reset mocks
        qbittorrentInterfaceGetInstanceMock.reset_mock()
        qbittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()
        loggingInfoMock.reset_mock()
        
        # call testable function - run 2
        CompletedDownloadsController.requestTorrentPause(fakeTorrentName)

        # asserts
        qbittorrentInterfaceGetInstanceMock.assert_called_with()
        qbittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeTorrentName)
        loggingInfoMock.assert_called_with(f"Failed to pause torrent activity: ({fakeTorrentName})")


    @mock.patch("controllers.ErrorController.reportError")
    @mock.patch("interfaces.FolderInterface.createDirectory")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    def test_ensureDirStructureExists(self, directoryExistsMock, createDirectoryMock, reportErrorMock):

        # config fake values
        fakeTvShowDir = "fakeTvShowDir"
        fakeSeasonDir = "fakeSeasonDir"

        # config mocks
        directoryExistsMock.side_effect = [False, False]

        # call testable function - run 1
        operationSuccess = CompletedDownloadsController.ensureDirStructureExists(fakeTvShowDir, fakeSeasonDir)

        # asserts
        calls = [ call(fakeTvShowDir), call(fakeSeasonDir) ]
        directoryExistsMock.assert_has_calls(calls)
        createDirectoryMock.assert_has_calls(calls)
        reportErrorMock.assert_not_called()
        self.assertTrue(operationSuccess)


        # reset mocks
        directoryExistsMock.reset_mock()
        directoryExistsMock.side_effect = [True, False]
        createDirectoryMock.reset_mock()

        # call testable function - run 2
        operationSuccess = CompletedDownloadsController.ensureDirStructureExists(fakeTvShowDir, fakeSeasonDir)

        # asserts
        calls = [ call(fakeTvShowDir), call(fakeSeasonDir) ]
        directoryExistsMock.assert_has_calls(calls)
        createDirectoryMock.assert_has_calls(calls[1:])
        reportErrorMock.assert_not_called()
        self.assertTrue(operationSuccess)


        # reset mocks
        directoryExistsMock.reset_mock()
        directoryExistsMock.side_effect = [False, True]
        createDirectoryMock.reset_mock()

        # call testable function - run 3
        operationSuccess = CompletedDownloadsController.ensureDirStructureExists(fakeTvShowDir, fakeSeasonDir)

        # asserts
        calls = [ call(fakeTvShowDir), call(fakeSeasonDir) ]
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
        operationSuccess = CompletedDownloadsController.ensureDirStructureExists(fakeTvShowDir, fakeSeasonDir)

        # asserts
        directoryExistsMock.assert_called_with(fakeTvShowDir)
        createDirectoryMock.assert_called_with(fakeTvShowDir)
        reportErrorMock.assert_called_with("Directory structure could not be completed", exception=fakeException, sendEmail=True)
        self.assertFalse(operationSuccess)


    @mock.patch("logging.info")
    @mock.patch("controllers.ErrorController.reportError")
    @mock.patch("controllers.CompletedDownloadsController.getLargestItemInDir")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    def test_getTargetFile(self, directoryExistsMock, getLargestItemInDirMock, reportErrorMock, loggingInfoMock):
        
        # config fake values
        fakeFileSystemItem = FakeFileSystemItem("fakeDirName1", "fakePath1")
        fakeTargetFile = FakeFileSystemItem("fakeDirName2", "fakePath2")

        # config mocks
        directoryExistsMock.side_effect = [True, False, True]
        getLargestItemInDirMock.return_value = fakeTargetFile

        # call testable function - run 1: fileSystemItem is a directory and largest file is returned successfully
        actualTargetFile = CompletedDownloadsController.getTargetFile(fakeFileSystemItem)

        # asserts
        directoryExistsMock.assert_called_with(fakeFileSystemItem.path)
        getLargestItemInDirMock.assert_called_with(fakeFileSystemItem.path)
        loggingInfoMock.assert_called_with(f"{fakeFileSystemItem.name} is a directory. The file {fakeTargetFile.name} has been extracted as the media item of interest.")
        reportErrorMock.assert_not_called()
        self.assertEqual(fakeTargetFile, actualTargetFile)


        # reset mocks
        getLargestItemInDirMock.reset_mock()
        loggingInfoMock.reset_mock()
        reportErrorMock.reset_mock()

        # call testable function - run 2: fileSystemItem is not a directory
        actualTargetFile = CompletedDownloadsController.getTargetFile(fakeFileSystemItem)

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
        actualTargetFile = CompletedDownloadsController.getTargetFile(fakeFileSystemItem)

        # asserts
        directoryExistsMock.assert_called_with(fakeFileSystemItem.path)
        getLargestItemInDirMock.assert_called_with(fakeFileSystemItem.path)
        loggingInfoMock.assert_not_called()
        reportErrorMock.assert_called_with(f"The fileSystemItem: {fakeFileSystemItem.name} is a directory but a targetFile could not be extracted. Skipping...")
        self.assertEqual(None, actualTargetFile)


    @mock.patch("controllers.CompletedDownloadsController.ensureDirStructureExists")
    @mock.patch("controllers.CompletedDownloadsController.extractEpisodeNumber")
    @mock.patch("controllers.CompletedDownloadsController.extractSeasonNumber")
    @mock.patch("controllers.CompletedDownloadsController.extractShowName")
    @mock.patch("os.getenv")
    def test_getProspectiveFilepPath(self, osGetentMock, extractShowNameMock, extractSeasonNumberMock, extractEpisodeNumberMock, ensureDirStructureExistsMock):

        # config fake data
        fakeTargetTvDir = "fakeTargetTvDir"
        fakeShowName = "Fakeshowname"
        fakeSeasonNumber = 2
        fakeEpisodeNumber = 2
        fakeMediaGrabId = f"{fakeShowName}--s{fakeSeasonNumber}e{fakeEpisodeNumber}"
        mode = PROGRAM_MODE.TV_EPISODES
        fakeExtension = ".mp4"
        fakeSeasonDir = f"Season {fakeSeasonNumber}"

        # expected values
        expectedProspectiveFilePath = os.path.join(fakeTargetTvDir, fakeShowName, fakeSeasonDir, f"{fakeShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}{fakeExtension}")
        expectedTvShowDir = os.path.join(fakeTargetTvDir, fakeShowName)
        expectedSeasonDir = os.path.join(expectedTvShowDir, fakeSeasonDir)

        # config mocks
        osGetentMock.return_value = fakeTargetTvDir
        extractShowNameMock.return_value = fakeShowName
        extractSeasonNumberMock.return_value = fakeSeasonNumber
        extractEpisodeNumberMock.return_value = fakeEpisodeNumber

        # run testable function
        actualProspectiveFilePath = CompletedDownloadsController.getProspectiveFilePath(fakeMediaGrabId, mode, fakeExtension)

        # asserts
        self.assertEqual(expectedProspectiveFilePath, actualProspectiveFilePath)
        osGetentMock.assert_called_with(PROGRAM_MODE_DIRECTORY_KEY_MAP[mode])
        extractShowNameMock.assert_called_with(fakeMediaGrabId)
        extractSeasonNumberMock.assert_called_with(fakeMediaGrabId)
        extractEpisodeNumberMock.assert_called_with(fakeMediaGrabId)
        ensureDirStructureExistsMock.assert_called_with(expectedTvShowDir, expectedSeasonDir)

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
        actualSubItem = CompletedDownloadsController.unWrapQBittorrentWrapperDir(fakeFileSystemItem)

        # asserts
        self.assertEqual(fakeFileSystemSubItems[0], actualSubItem)

        # reconfig mocks
        osScandirMock.return_value = []

        # call testable function - run 1
        actualSubItem = CompletedDownloadsController.unWrapQBittorrentWrapperDir(
            fakeFileSystemItem)

        # asserts
        loggingInfoMock.assert_called_with(
            f"Tried to browse past the directory created by qbittorrent ({fakeFileSystemItem.path}) but nothing was found inside.")

    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
    @mock.patch("interfaces.FolderInterface.recycleOrDeleteDir")
    @mock.patch("os.rmdir")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.notifyDownloadFinished")
    @mock.patch("os.rename")
    @mock.patch("interfaces.FolderInterface.fileExists")
    @mock.patch("controllers.CompletedDownloadsController.getProspectiveFilePath")
    @mock.patch("controllers.CompletedDownloadsController.extractExtension")
    @mock.patch("controllers.CompletedDownloadsController.getTargetFile")
    @mock.patch("logging.info")
    @mock.patch("controllers.CompletedDownloadsController.requestTorrentPause")
    @mock.patch("controllers.CompletedDownloadsController.unWrapQBittorrentWrapperDir")
    def test_auditFileSystemItemForEpisode(self, unWrapQBittorrentWrapperDirMock, requestTorrentPauseMock, loggingInfoMock, getTargetFileMock, extractExtensionMock, getProspectiveFilePathMock, fileExistsMock, osRenameMock, notifyDownloadFinishedMock, osRmdirMock, recycleOrDeleteDirMock, downloadWasInitiatedByMediaGrabMock):

        # config fake values
        fakeFileSystemItemWrapper = FakeFileSystemItem("fakeWrapperDir1Name", "fakeWrapperPath1Name")
        fakeFileSystemItem = FakeFileSystemItem("fakeDir1Name", "fakePath1Name")
        fakeTargetFile = FakeFileSystemItem(
            "fakeTargetFileDir1Name", "fakeTargetFilePath1Name")
        fakeExtension = ".mp4"
        fakeProspectiveFile = "fakeProspectiveFile"

        # config mocks
        unWrapQBittorrentWrapperDirMock.return_value = fakeFileSystemItem
        getTargetFileMock.return_value = fakeTargetFile
        extractExtensionMock.return_value = fakeExtension
        getProspectiveFilePathMock.return_value = fakeProspectiveFile
        fileExistsMock.return_value = False
        downloadWasInitiatedByMediaGrabMock.return_value = True

        # run testable function - run 1: successful run
        CompletedDownloadsController.auditFileSystemItemForEpisode(
            fakeFileSystemItemWrapper)

        # asserts
        unWrapQBittorrentWrapperDirMock.assert_called_with(fakeFileSystemItemWrapper)
        requestTorrentPauseMock.assert_called_with(fakeFileSystemItem.name)
        loggingCalls = [
            call(
                f"{fakeFileSystemItem.name} has finished downloading and will be moved."),
            call(f"Moved '{fakeTargetFile.path}' to '{fakeProspectiveFile}'")
        ]
        loggingInfoMock.assert_has_calls(loggingCalls)
        getTargetFileMock.assert_called_with(fakeFileSystemItem)
        extractExtensionMock.assert_called_with(fakeTargetFile.name)
        getProspectiveFilePathMock.assert_called_with(
            fakeFileSystemItemWrapper.name, PROGRAM_MODE.TV_EPISODES, fakeExtension)
        fileExistsMock.assert_called_with(fakeProspectiveFile)
        osRenameMock.assert_called_with(fakeTargetFile.path, fakeProspectiveFile)
        notifyDownloadFinishedMock.assert_called_with(
            fakeFileSystemItemWrapper.name, PROGRAM_MODE.TV_EPISODES)
        recycleOrDeleteDirMock.assert_called_with(fakeFileSystemItem.path)
        osRmdirMock.assert_called_with(fakeFileSystemItemWrapper.path)

    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
    @mock.patch("controllers.CompletedDownloadsController.auditFileSystemItemForEpisode")
    @mock.patch("interfaces.FolderInterface.getDirContents")
    @mock.patch("logging.info")
    def test_auditFileSystemItemsForEpisodes(self, loggingInfoMock, getDirContentsMock, auditFileSystemItemForEpisodeMock, downloadWasInitiatedByMediaGrabMock):

        # config fake data
        fakeDirName = "fakeDirName1"
        fakeFileSystemItems = [
            FakeFileSystemItem(fakeDirName, "fakeName1")
        ]
        fakeDownloadingItems = [fakeDirName, "fakeDirName2"]

        # config mocks
        getDirContentsMock.return_value = fakeFileSystemItems
        downloadWasInitiatedByMediaGrabMock.return_value = True

        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeDownloadingItems)

        # asserts
        loggingInfoCalls = [
            call("File auditing started."),
            call(f"Items in dump_complete directory: {[fakeDirName]}")
        ]
        loggingInfoMock.assert_has_calls(loggingInfoCalls)
        getDirContentsMock.assert_called_with(fakeDumpCompleteDir)
        auditFileSystemItemForEpisodeMock.assert_called_with(
            fakeFileSystemItems[0])

    @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    @mock.patch("logging.info")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.notifyDownloadFinished")
    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch('os.getenv')
    def test_auditFilesWithFileSystem(self, getEnvMock, reportItemAlreadyExistsMock, notifyDownloadFinishedMock, loggingInfoMock, qBittorrentInterfaceGetInstanceMock, downloadWasInitiatedByMediaGrabMock):

        # init items
        downloadingItems = [
            "fake tv show name--s01e01.mp4",
            "fake tv show name--s01e02.mp4",
            "fake-tv-show-name.s01.e03/fake tv show name--s01e03.mp4"
        ] # representation of what is in the dump_complete folder

        # config fake data #
        mode = PROGRAM_MODE.TV_EPISODES
        fakeFilteredDownloadingItems = {
            "tv-seasons": [],
            "tv-episodes": [
                "fake tv show name--s01e01",
                "fake tv show name--s01e02",
                "fake tv show name--s01e03",
                "fakeDownloadingFile2--s1e4",
                "fakeDownloadingFile3--s3e6"
            ]
        } # this should be the content of the DownloadsInProgressFile 
        expectedTvShowName = "Fake tv show name"
        directoriesToCleanUp = [ fakeTargetTvDir, fakeDumpCompleteDir, fakeRecycleBinDir ]
        # create mock for instance
        qBittorrentInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        qBittorrentInterfaceGetInstanceMock.return_value = qBittorrentInterfaceInstanceMock
        qBittorrentInterfaceInstanceMock.qBittorrentInterfaceInstanceMock.pauseTorrent.return_value = True
        downloadWasInitiatedByMediaGrabMock.return_value = True

        # config mocks
        getEnvMock.side_effect = getEnvMockFunc

        # setup fake files
        for path in downloadingItems:
            pathParts = path.split("/")
            newDir = ""


            newDir = "/".join(pathParts[:-1])
            fileName = pathParts[-1]
            fileNameNoExt = fileName.split(".mp4")[0]
            baseDirPath = os.path.join(fakeDumpCompleteDir, fileNameNoExt)
            if not os.path.isdir(baseDirPath):
                os.mkdir(baseDirPath)
                
            if len(pathParts) > 1:
                newDir = "/".join(pathParts[:-1])
                dirPath = os.path.join(baseDirPath, newDir)
                if not os.path.isdir(dirPath):
                    os.mkdir(dirPath)

            episodeFile = os.path.join(baseDirPath, newDir, pathParts[-1])
            if not os.path.isfile(episodeFile):
                os.mknod(episodeFile)

        # this is required so that the new folder created under fakeTargetTvDir can be found and cleaned up
        downloadingItems.append(expectedTvShowName) 

        try:
            # assert state is as expected before audit method is called
            self.assertTrue(len(list(os.scandir(fakeTargetTvDir))) == 0)
            numItemsInDumpCompleteBefore = len(list(os.scandir(fakeDumpCompleteDir)))
            self.assertTrue(numItemsInDumpCompleteBefore >= 2)
            self.assertTrue(len(list(os.scandir(fakeRecycleBinDir))) == 0)

            # run auditDumpCompleteDir
            CompletedDownloadsController.auditDumpCompleteDir(fakeFilteredDownloadingItems["tv-episodes"])

            expectedNumItems = len(downloadingItems) - 1
            # assert that the contents of downloadingItems has been moved from the `dummy_directories/dump_complete` directory to the `dummy_directories/tv` directory
            self.assertTrue(len(list(os.scandir(os.path.join(fakeTargetTvDir, expectedTvShowName, "Season 1")))) == expectedNumItems)
            self.assertTrue(len(list(os.scandir(fakeDumpCompleteDir))) == numItemsInDumpCompleteBefore - expectedNumItems)
            self.assertTrue(len(list(os.scandir(fakeRecycleBinDir))) == 1)
            notifyDownloadFinishedMock.assert_called()
            loggingInfoMock.assert_called()
            reportItemAlreadyExistsMock.assert_not_called()

        finally:
            # clean up moved files
            cleanUpDirs(directoriesToCleanUp, downloadingItems)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
