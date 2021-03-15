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

# fake directories for use across multiple tests
fakeTargetTvDir = "test/dummy_directories/tv"
fakeDumpCompleteDir = "test/dummy_directories/dump_complete"
fakeRecycleBinDir = "test/dummy_directories/recycle_bin"

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


    def test_extractShowName(self):
        expectedFakeShowName = "fake show"
        fakeShowName = "fake show--s1e1"

        actualFakeShowName = CompletedDownloadsController.extractShowName(fakeShowName)
        self.assertEqual(expectedFakeShowName, actualFakeShowName)
        
        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractShowName(""))


    def test_extractSeasonNumber(self):
        expectedSeasonNumber = 2
        fakeShowName = "fake show--s2e1"

        actualFakeSeasonNumber = CompletedDownloadsController.extractSeasonNumber(fakeShowName)
        self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractSeasonNumber(""))


    def test_extractEpisodeNumber(self):
        expectedSeasonNumber = 3
        fakeShowName = "fake show--s1e3"

        actualFakeSeasonNumber = CompletedDownloadsController.extractEpisodeNumber(fakeShowName)
        self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractSeasonNumber(""))


    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    @mock.patch("os.rmdir")
    @mock.patch("os.scandir")
    @mock.patch("logging.info")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.notifyDownloadFinished")
    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch("os.rename")
    @mock.patch("interfaces.FolderInterface.fileExists")
    @mock.patch("interfaces.FolderInterface.getDirContents")
    @mock.patch("controllers.CompletedDownloadsController.extractExtension")
    @mock.patch("controllers.CompletedDownloadsController.extractEpisodeNumber")
    @mock.patch("controllers.CompletedDownloadsController.extractSeasonNumber")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    @mock.patch("interfaces.FolderInterface.createDirectory")
    @mock.patch('controllers.CompletedDownloadsController.extractShowName')
    @mock.patch('os.getenv')
    def test_auditFiles(self, getEnvMock, extractShowNameMock, createDirectoryMock, directoryExistsMock, extractSeasonNumberMock, extractEpisodeNumberMock, extractExtensionMock, getDirContentsMock, fileExistsMock, osRenameMock, reportItemAlreadyExistsMock, notifyDownloadFinishedMock, loggingInfoMock, osScandirMock, osRmdirMock, qBittorrentInterfaceGetInstanceMock):

        # config fake data
        fakeEpisodeNumber = 2
        fakeSeasonNumber = 1
        fakeTVShowName = "Faketvshowname"
        fakeFile1 = f"{fakeTVShowName}.S0{fakeSeasonNumber}.E0{fakeEpisodeNumber}.mp4"
        class FakeFile:
            def __init__(self, name, path):
                self.name = name
                self.path = path

        fakeFiles = [ FakeFile(fakeFile1, os.path.join(fakeDumpCompleteDir, fakeFile1)) ]
        fakeFilteredDownloadingItems = [ fakeFile1 ]
        fakeMode = PROGRAM_MODE.TV_EPISODES

        # config mocks
        getEnvMock.side_effect = getEnvMockFunc
        extractShowNameMock.return_value = fakeTVShowName
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ False, True, True ] 
        extractSeasonNumberMock.return_value = fakeSeasonNumber
        extractEpisodeNumberMock.return_value = fakeEpisodeNumber
        fileExistsMock.return_value = True
        extractExtensionMock.return_value = ".mp4"
        getDirContentsMock.return_value = fakeFiles
        osScandirMock.return_value = fakeFiles
        # create mock for instance
        qBittorrentInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        qBittorrentInterfaceGetInstanceMock.return_value = qBittorrentInterfaceInstanceMock
        qBittorrentInterfaceInstanceMock.pauseTorrent.return_value = True


        # Case 1 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        #   * file exists
        # CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)
        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)

        # config expected values
        expectedProspectiveFile = os.path.join(fakeTargetTvDir, fakeTVShowName, f"Season {fakeSeasonNumber}", f"{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}.mp4")

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_called_with(expectedProspectiveFile, fakeFiles[0].path)
        osRenameMock.assert_not_called()
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeFile1)

        # Case 1 end ############################################################################


        # Case 2 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        #   * file does not exist

        # reconfig mocks
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ False, True, True ] 
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        qBittorrentInterfaceInstanceMock.qBittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()

        # CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)
        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(os.path.join(fakeDumpCompleteDir, fakeFile1), expectedProspectiveFile)
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeFile1)

        # Case 2 end ############################################################################


        # Case 3 start ############################################################################
        #   * show dir exists
        #   * season dir does not exist
        #   * file does not exist

        # reconfig mocks
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ False, True, False ] 
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()
        qBittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()

        # CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)
        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)

        # config expected values
        expectedSeasonDir = os.path.join(fakeTargetTvDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedCreateDirectoryCalls = [call(expectedSeasonDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(os.path.join(fakeDumpCompleteDir, fakeFile1), expectedProspectiveFile)
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeFile1)

        # Case 3 end ############################################################################


        # Case 4 start ############################################################################
        #   * show dir does not exist
        #   * season dir does not exist
        #   * file does not exist

        # reconfig mocks
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ False, False, False ] 
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()
        qBittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()

        # CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)
        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)

        # config expected values
        expectedSeasonDir = os.path.join(fakeTargetTvDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedTvDir = os.path.join(fakeTargetTvDir, fakeTVShowName)
        expectedCreateDirectoryCalls = [call(expectedSeasonDir), call(expectedTvDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(os.path.join(fakeDumpCompleteDir, fakeFile1), expectedProspectiveFile)
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeFile1)

        # Case 4 end ############################################################################


    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    @mock.patch("os.rmdir")
    @mock.patch("os.scandir")
    @mock.patch("shutil.move")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.notifyDownloadFinished")
    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch("os.rename")
    @mock.patch("interfaces.FolderInterface.fileExists")
    @mock.patch("interfaces.FolderInterface.getDirContents")
    @mock.patch("controllers.CompletedDownloadsController.extractExtension")
    @mock.patch("controllers.CompletedDownloadsController.getLargestFileInDir")
    @mock.patch("controllers.CompletedDownloadsController.extractEpisodeNumber")
    @mock.patch("controllers.CompletedDownloadsController.extractSeasonNumber")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    @mock.patch("interfaces.FolderInterface.createDirectory")
    @mock.patch('controllers.CompletedDownloadsController.extractShowName')
    @mock.patch('os.getenv')
    def test_auditDirectories(self, getEnvMock, extractShowNameMock, createDirectoryMock, directoryExistsMock, extractSeasonNumberMock, extractEpisodeNumberMock, getLargestFileInDirMock, extractExtensionMock, getDirContentsMock, fileExistsMock, osRenameMock, reportItemAlreadyExistsMock, notifyDownloadFinishedMock, shutilMoveMock, osScandirMock, osRmdirMock, qBittorrentInterfaceGetInstanceMock):

        class FakeFileSystemItem:
            
            def __init__(self, dirName, path):
                self.name = dirName
                self.path = path

        # config fake data
        fakeSeasonNumber = 1
        fakeEpisodeNumber = 1
        fakeTVShowName = "fake TV Show Name"
        fakeDirName = f"{fakeTVShowName}.S0{fakeSeasonNumber}.E0{fakeEpisodeNumber}"
        fakeDir1 = FakeFileSystemItem(fakeDirName, os.path.join(fakeDumpCompleteDir, fakeDirName))
        fakeExtension = ".mp4"
        fakeFile1 = f"{fakeDirName}{fakeExtension}"
        fakeDirs = [ fakeDir1 ]
        fakeFilteredDownloadingItems = [ fakeDirName ]
        fakeMode = PROGRAM_MODE.TV_EPISODES

        # config mocks
        getEnvMock.side_effect = getEnvMockFunc
        extractShowNameMock.return_value = fakeTVShowName
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ True, True, True ] 
        fileExistsMock.return_value = True
        extractSeasonNumberMock.return_value = fakeSeasonNumber
        extractEpisodeNumberMock.return_value = fakeEpisodeNumber
        getLargestFileInDirMock.return_value = FakeFileSystemItem(fakeFile1, os.path.join(fakeDumpCompleteDir, fakeDirName, fakeFile1))
        extractExtensionMock.return_value = ".mp4"
        getDirContentsMock.return_value = fakeDirs
        osScandirMock.return_value = fakeDirs
        # create mock for instance
        qBittorrentInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        qBittorrentInterfaceGetInstanceMock.return_value = qBittorrentInterfaceInstanceMock
        qBittorrentInterfaceInstanceMock.qBittorrentInterfaceInstanceMock.pauseTorrent.return_value = True

        # config expected values
        expectedProspectiveFile = os.path.join(fakeTargetTvDir, fakeTVShowName.capitalize(), f"Season {fakeSeasonNumber}", f"{fakeTVShowName.capitalize()} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}{fakeExtension}")

        # Case 1 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        #   * file exists
        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)


        # asserts
        createDirectoryMock.assert_not_called()
        fakeDirPath = os.path.join(fakeDumpCompleteDir, fakeDirName)
        reportItemAlreadyExistsMock.assert_called_with(expectedProspectiveFile, fakeDirPath)
        osRenameMock.assert_not_called()
        notifyDownloadFinishedMock.assert_not_called()
        shutilMoveMock.assert_not_called()
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeDirName)

        # Case 1 end ############################################################################


        # Case 2 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        #   * file does not exist

        # reconfig mocks
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ True, True, True ] 
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        expectedOriginalFileLocation = os.path.join(fakeDumpCompleteDir, fakeDirName, fakeFile1)
        osRenameMock.reset_mock()
        qBittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()

        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(expectedOriginalFileLocation, expectedProspectiveFile)
        notifyDownloadFinishedMock.assert_called_with(fakeDirName, PROGRAM_MODE.TV_EPISODES)
        shutilMoveMock.assert_called_with(os.path.join(fakeDumpCompleteDir, fakeDirName), fakeRecycleBinDir)
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeDirName)

        # Case 2 end ############################################################################

        # Case 3 start ############################################################################
        #   * show dir exists
        #   * season dir does not exist
        #   * file does not exist

        # reconfig mocks
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ True, True, False ] 
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()
        qBittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()

        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)

        # config expected values
        # expectedSeasonDir = os.path.join(seasonDir, f"{showName} - S0{seasonNumber}E0{episodeNumber}{extension}")

        expectedSeasonDir = os.path.join(fakeTargetTvDir, fakeTVShowName.capitalize(), f"Season {fakeSeasonNumber}")
        expectedCreateDirectoryCalls = [call(expectedSeasonDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(expectedOriginalFileLocation, expectedProspectiveFile)
        notifyDownloadFinishedMock.assert_called_with(fakeDirName, PROGRAM_MODE.TV_EPISODES)
        shutilMoveMock.assert_called_with(os.path.join(fakeDumpCompleteDir, fakeDirName), fakeRecycleBinDir)
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeDirName)

        # Case 3 end ############################################################################


        # Case 4 start ############################################################################
        #   * show dir does not exist
        #   * season dir does not exist
        #   * file does not exist

        # reconfig mocks
        # 1. check input is directory, 2. check tv show dir exists, 3. check season dir exists
        directoryExistsMock.side_effect = [ True, False, False ] 
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()
        osRenameMock.reset_mock()
        qBittorrentInterfaceInstanceMock.pauseTorrent.reset_mock()

        CompletedDownloadsController.auditFileSystemItemsForEpisodes(fakeMode, fakeFilteredDownloadingItems)

        # config expected values
        expectedTvDir = os.path.join(fakeTargetTvDir, fakeTVShowName.capitalize())
        expectedCreateDirectoryCalls = [ call(expectedTvDir), call(expectedSeasonDir) ]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(expectedOriginalFileLocation, expectedProspectiveFile)
        notifyDownloadFinishedMock.assert_called_with(fakeDirName, PROGRAM_MODE.TV_EPISODES)
        shutilMoveMock.assert_called_with(os.path.join(fakeDumpCompleteDir, fakeDirName), fakeRecycleBinDir)
        qBittorrentInterfaceInstanceMock.pauseTorrent.assert_called_with(fakeDirName)

        # Case 4 end ############################################################################


    @mock.patch("interfaces.QBittorrentInterface.getInstance")
    @mock.patch("logging.info")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.notifyDownloadFinished")
    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch('os.getenv')
    def test_auditFilesWithFileSystem(self, getEnvMock, reportItemAlreadyExistsMock, notifyDownloadFinishedMock, loggingInfoMock, qBittorrentInterfaceGetInstanceMock):

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
            CompletedDownloadsController.auditDumpCompleteDir(mode, fakeFilteredDownloadingItems["tv-episodes"])

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
