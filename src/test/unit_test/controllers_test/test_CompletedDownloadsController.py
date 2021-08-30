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
from src.test.unit_test.testUtilities import FakeFileSystemItem, cleanUpDirs, getEnvMockFunc, fakeRecycleBinDir, fakeTargetTvDir, fakeDumpCompleteDir


class TestCompletedDownloadsController(unittest.TestCase):

    @mock.patch("src.controllers.CompletedDownloadsController.permanentlyDeleteExpiredItems")
    @mock.patch("src.strategies.AuditSeasonStrategy.AuditSeasonStrategy.audit")
    @mock.patch("src.strategies.AuditEpisodeStrategy.AuditEpisodeStrategy.audit")
    @mock.patch("src.interfaces.FolderInterface.getDirContents")
    @mock.patch('os.getenv')
    @mock.patch("logging.info")
    def test_auditDumpCompleteDir(self, loggingInfoMock, getEnvMock, getDirContentsMock, AuditEpisodeStrategyAuditMock, AuditSeasonStrategyAuditMock, permanentlyDeleteExpiredItemsMock):

        # config fake data
        fakeDirName = "fakeDirName1"
        fakeFileSystemItems = [
            FakeFileSystemItem(fakeDirName, "fakeName1")
        ]
        os.environ["TV_TARGET_DIR"] = fakeTargetTvDir

        # config mocks
        getDirContentsMock.return_value = fakeFileSystemItems
        getEnvMock.side_effect = getEnvMockFunc

        AuditEpisodeStrategyAuditMock.return_value = True
        AuditSeasonStrategyAuditMock.return_value = True

        CompletedDownloadsController.auditDumpCompleteDir()

        # asserts
        loggingInfoCalls = [
            call("File auditing started."),
            call(f"Items in dump_complete directory: {[fakeDirName]}")
        ]
        loggingInfoMock.assert_has_calls(loggingInfoCalls)
        getDirContentsMock.assert_called_with(fakeDumpCompleteDir)
        permanentlyDeleteExpiredItemsMock.assert_called()

    @mock.patch("src.controllers.CompletedDownloadsController.permanentlyDeleteExpiredItems")
    @mock.patch("src.interfaces.QBittorrentInterface.getInstance")
    @mock.patch("logging.info")
    @mock.patch("src.utilities.AuditUtilities.reportItemAlreadyExists")
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
                        
    @mock.patch('src.interfaces.FolderInterface.deleteFile')
    @mock.patch('src.interfaces.FolderInterface.deleteDir')
    @mock.patch('os.path.getctime')
    @mock.patch('src.interfaces.FolderInterface.getDirContents')
    @mock.patch('os.getenv')
    def test_permanentlyDeleteExpiredItems(self, getEnvMock, getDirContentsMock, getctimeMock, deleteDirMock, deleteFileMock):

        logsDir = "logs"

        def fakeGetDirContents(directory):

            assert(directory in [fakeRecycleBinDir, logsDir])

            return [
                FakeFileSystemItem("fakeDirName1", os.path.join(directory, "fakePath1")),
                FakeFileSystemItem("fakeDirName2", os.path.join(directory, "fakePath2"))
            ]

        # config mocks
        getDirContentsMock.side_effect = fakeGetDirContents
        getctimeMock.side_effect = [
            (datetime.now() - timedelta(weeks=5)).timestamp(), # 5 weeks old
            (datetime.now() - timedelta(weeks=3)).timestamp(), # 3 weeks old
            (datetime.now() - timedelta(days=8)).timestamp(), # 8 days old
            (datetime.now() - timedelta(days=6)).timestamp(), # 6 days old
        ]
        getEnvMock.side_effect = getEnvMockFunc
        
        # run testable function
        CompletedDownloadsController.permanentlyDeleteExpiredItems()

        # mock asserts
        deleteDirMock.assert_called_with(
            os.path.join(fakeRecycleBinDir, "fakePath1"))
        deleteFileMock.assert_called_with(os.path.join(logsDir, "fakePath1"))


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
