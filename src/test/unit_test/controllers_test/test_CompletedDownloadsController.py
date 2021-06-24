# external dependencies
import unittest
import mock
import os
from unittest.mock import call
import shutil
from mock import MagicMock
from datetime import datetime, timedelta

# internal dependencies
from src.controllers import CompletedDownloadsController
from src.dataTypes.ProgramMode import PROGRAM_MODE
from src.dataTypes.ProgramModeMap import PROGRAM_MODE_DIRECTORY_KEY_MAP
from test.unit_test.testUtilities import FakeFileSystemItem, cleanUpDirs, getEnvMockFunc

# fake directories for use across multiple tests
fakeTargetTvDir = "test/dummy_directories/tv"
fakeDumpCompleteDir = "test/dummy_directories/dump_complete"
fakeRecycleBinDir = "test/dummy_directories/recycle_bin"

class TestCompletedDownloadsController(unittest.TestCase):

    @mock.patch("controllers.CompletedDownloadsController.postMoveDirectoryCleanup")
    @mock.patch("controllers.CompletedDownloadsController.moveFile")
    @mock.patch("controllers.CompletedDownloadsController.getTargetFile")
    @mock.patch("logging.info")
    @mock.patch("controllers.CompletedDownloadsController.requestTorrentPause")
    @mock.patch("controllers.CompletedDownloadsController.unWrapQBittorrentWrapperDir")
    @mock.patch("controllers.CompletedDownloadsControllerUtilities.downloadWasInitiatedByMediaGrab")
    def test_auditFileSystemItemForEpisode(self, downloadWasInitiatedByMediaGrabMock, unWrapQBittorrentWrapperDirMock, requestTorrentPauseMock, loggingInfoMock, getTargetFileMock, moveFileMock, postMoveDirectoryCleanupMock):

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


        # run testable function - run 1: successful run
        result = CompletedDownloadsController.auditFileSystemItemForEpisode(
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

    # @mock.patch("controllers.CompletedDownloadsController.downloadWasInitiatedByMediaGrab")
    # @mock.patch("interfaces.FolderInterface.recycleOrDeleteDir")
    # @mock.patch("os.rmdir")
    @mock.patch("os.rename")
    @mock.patch("interfaces.FolderInterface.fileExists")
    @mock.patch("controllers.CompletedDownloadsController.getProspectiveFilePath")
    @mock.patch("controllers.CompletedDownloadsControllerUtilities.extractExtension")
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

        # run testable function - run 1: successful run
        CompletedDownloadsController.moveFile(fakeTargetFile, fakeFileSystemItem, fakeFileSystemItem.name, fakeFileSystemItem.path)

        # asserts
        loggingInfoMock.assert_called_with(
            f"Moved '{fakeTargetFile.path}' to '{fakeProspectiveFile}'")
        extractExtensionMock.assert_called_with(fakeTargetFile.name)
        getProspectiveFilePathMock.assert_called_with(
            fakeFileSystemItem.name, PROGRAM_MODE.TV, fakeExtension)
        fileExistsMock.assert_called_with(fakeProspectiveFile)
        osRenameMock.assert_called_with(
            fakeTargetFile.path, fakeProspectiveFile)

    @mock.patch("controllers.CompletedDownloadsController.permanentlyDeleteExpiredItems")
    @mock.patch("controllers.CompletedDownloadsControllerUtilities.downloadWasInitiatedByMediaGrab")
    @mock.patch("controllers.CompletedDownloadsController.auditFileSystemItemForEpisode")
    @mock.patch("interfaces.FolderInterface.getDirContents")
    @mock.patch('os.getenv')
    @mock.patch("logging.info")
    def test_auditDumpCompleteDir(self, loggingInfoMock, getEnvMock, getDirContentsMock, auditFileSystemItemForEpisodeMock, downloadWasInitiatedByMediaGrabMock, permanentlyDeleteExpiredItemsMock):

        # config fake data
        fakeDirName = "fakeDirName1"
        fakeFileSystemItems = [
            FakeFileSystemItem(fakeDirName, "fakeName1")
        ]
        os.environ["TV_TARGET_DIR"] = fakeTargetTvDir

        # config mocks
        getDirContentsMock.return_value = fakeFileSystemItems
        downloadWasInitiatedByMediaGrabMock.return_value = True
        getEnvMock.side_effect = getEnvMockFunc

        CompletedDownloadsController.auditDumpCompleteDir()

        # asserts
        loggingInfoCalls = [
            call("File auditing started."),
            call(f"Items in dump_complete directory: {[fakeDirName]}")
        ]
        loggingInfoMock.assert_has_calls(loggingInfoCalls)
        getDirContentsMock.assert_called_with(fakeDumpCompleteDir)
        auditFileSystemItemForEpisodeMock.assert_called_with(
            fakeFileSystemItems[0])
        permanentlyDeleteExpiredItemsMock.assert_called()

    @mock.patch("controllers.CompletedDownloadsController.permanentlyDeleteExpiredItems")
    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    @mock.patch("logging.info")
    @mock.patch("controllers.CompletedDownloadsControllerUtilities.reportItemAlreadyExists")
    @mock.patch('os.getenv')
    def test_auditFilesWithFileSystem(self, getEnvMock, reportItemAlreadyExistsMock, loggingInfoMock, qBittorrentInterfaceGetInstanceMock, permanentlyDeleteExpiredItemsMock):

        # init items
        downloadingItems = [
            "fake tv show name--s01e01/fake tv show name.s01e01.mp4", # mediaGrab initiated download - no sub folder
            "fake tv show name--s01e02/fake-tv-show-name.s01.e02/fake-tv-show-name.s01.e02.mp4", # mediaGrab initiated download - with sub folder
            "fake tv show name s01e03.mp4",  # manually initiated download - no sub folder
            "fake-tv-show-name.s01.e04/fake-tv-show-name.s01.e04.mp4", # manually initiated download - with sub folder
            "non-parsable item",
            "fake tv show name--s02/fake-tv-show-name.s02/fake-tv-show-name.s02.e01.mp4",
            "fake tv show name--s02/fake-tv-show-name.s02/fake-tv-show-name.s02.e02.mp4",
            "fake tv show name--s02/fake-tv-show-name.s02/fake-tv-show-name.s02.e03.mp4",
            "fake tv show name--s02/fake-tv-show-name.s02/fake-tv-show-name.s02.e04.mp4",
            "fake tv show name--s02/fake-tv-show-name.s02/fake-tv-show-name.s02.e05.mp4"
        ] # representation of what is in the dump_complete folder

        # config fake data #
        mode = PROGRAM_MODE.TV
        expectedTvShowName = "Fake tv show name"
        directoriesToCleanUp = [ fakeTargetTvDir, fakeDumpCompleteDir, fakeRecycleBinDir ]
        # create mock for instance
        qBittorrentInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        qBittorrentInterfaceGetInstanceMock.return_value = qBittorrentInterfaceInstanceMock
        qBittorrentInterfaceInstanceMock.qBittorrentInterfaceInstanceMock.pauseTorrent.return_value = True
        os.environ["TV_TARGET_DIR"] = fakeTargetTvDir
        os.environ["RECYCLE_BIN_DIR"] = fakeRecycleBinDir

        # config mocks
        getEnvMock.side_effect = getEnvMockFunc

        # setup fake files
        for path in downloadingItems:
            pathParts = path.split("/")
            directories = pathParts[:-1]
            newDirPath = fakeDumpCompleteDir

            # create directories
            for directory in directories:
                newDirPath = os.path.join(newDirPath, directory)
                if not os.path.isdir(newDirPath):
                    os.mkdir(newDirPath)

            newFilePath = os.path.join(fakeDumpCompleteDir, path)

            if not os.path.isfile(newFilePath):
                # os.mknod(newFilePath)
                size = 50000001
                with open('%s' % newFilePath, 'wb') as fout:
                    fout.write(os.urandom(size))  # 1

        try:
            # assert state is as expected before audit method is called
            self.assertEqual(0, len(list(os.scandir(fakeTargetTvDir))))
            self.assertEqual(len(downloadingItems), 10)
            self.assertEqual(0, len(list(os.scandir(fakeRecycleBinDir))))

            # run auditDumpCompleteDir
            CompletedDownloadsController.auditDumpCompleteDir()
            
            # assert that the contents of downloadingItems has been moved from the `dummy_directories/dump_complete` directory to the `dummy_directories/tv` directory
            self.assertEqual(4, len(list(os.scandir(os.path.join(
                fakeTargetTvDir, expectedTvShowName, "Season 1")))))
            self.assertEqual(1, len(list(os.scandir(fakeDumpCompleteDir))))
            self.assertEqual(3, len(list(os.scandir(fakeRecycleBinDir))))
            loggingInfoMock.assert_called()
            permanentlyDeleteExpiredItemsMock.assert_called()
            reportItemAlreadyExistsMock.assert_not_called()

        finally:
            # clean up moved files
            cleanUpDirs(directoriesToCleanUp, downloadingItems)
            pass
                        
    @mock.patch('interfaces.FolderInterface.deleteFile')
    @mock.patch('interfaces.FolderInterface.deleteDir')
    @mock.patch('os.path.getctime')
    @mock.patch('interfaces.FolderInterface.getDirContents')
    def test_permanentlyDeleteExpiredItems(self, getDirContentsMock, getctimeMock, deleteDirMock, deleteFileMock):

        logsDir = "logs"

        def getDirContents(directory):

            assert(directory in [fakeRecycleBinDir, logsDir])

            return [
                FakeFileSystemItem("fakeDirName1", os.path.join(directory, "fakePath1")),
                FakeFileSystemItem("fakeDirName2", os.path.join(directory, "fakePath2"))
            ]

        # config mocks
        getDirContentsMock.side_effect = getDirContents
        getctimeMock.side_effect = [
            (datetime.now() - timedelta(weeks=5)).timestamp(), # 5 weeks old
            (datetime.now() - timedelta(weeks=3)).timestamp(), # 3 weeks old
            (datetime.now() - timedelta(days=8)).timestamp(), # 8 days old
            (datetime.now() - timedelta(days=6)).timestamp(), # 6 days old
        ]
        
        # run testable function
        CompletedDownloadsController.permanentlyDeleteExpiredItems()

        # mock asserts
        deleteDirMock.assert_called_with(
            os.path.join(fakeRecycleBinDir, "fakePath1"))
        deleteFileMock.assert_called_with(os.path.join(logsDir, "fakePath1"))


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
