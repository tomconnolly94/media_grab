# external dependencies
import unittest
import mock
import os
from unittest.mock import call
import shutil

# internal dependencies
from controllers import CompletedDownloadsController
from data_types.ProgramMode import PROGRAM_MODE 

# fake directories for use across multiple tests
fakeTargetTvDir = "test/dummy_directories/tv/"
fakeDumpCompleteDir = "test/dummy_directories/dump_complete/"

# re-usable getEnvMock function
def getEnvMockFunc(param):
    if param == "TV_TARGET_DIR":
        return fakeTargetTvDir
    elif param == "DUMP_COMPLETE_DIR":
        return fakeDumpCompleteDir
    else:
        assert(None)

class TestCompletedDownloadsController(unittest.TestCase):


    def test_extractShowName(self):
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

        for fakeShowName in fakeShowNamesSuccessful:
            actualFakeShowName = CompletedDownloadsController.extractShowName(fakeShowName)
            self.assertEqual(expectedFakeShowName, actualFakeShowName)
        
        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractShowName(""))


    def test_extractSeasonNumber(self):
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

        for fakeShowName in fakeShowNamesSuccessful:
            actualFakeSeasonNumber = CompletedDownloadsController.extractSeasonNumber(fakeShowName)
            self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractSeasonNumber(""))


    def test_extractEpisodeNumber(self):
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

        for fakeShowName in fakeShowNamesSuccessful:
            actualFakeSeasonNumber = CompletedDownloadsController.extractEpisodeNumber(fakeShowName)
            self.assertEqual(expectedSeasonNumber, actualFakeSeasonNumber)

        for fakeShowName in fakeShowNamesUnsuccessful:
            actualFakeSeasonNumber = CompletedDownloadsController.extractEpisodeNumber(fakeShowName)
            self.assertEqual(None, actualFakeSeasonNumber)

        # check empty string
        self.assertEqual(None, CompletedDownloadsController.extractSeasonNumber(""))


    @mock.patch("logging.info")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.notifyDownloadFinished")
    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch("os.rename")
    @mock.patch("interfaces.FolderInterface.fileExists")
    @mock.patch("controllers.CompletedDownloadsController.extractEpisodeNumber")
    @mock.patch("controllers.CompletedDownloadsController.extractSeasonNumber")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    @mock.patch("interfaces.FolderInterface.createDirectory")
    @mock.patch('controllers.CompletedDownloadsController.extractShowName')
    @mock.patch('os.getenv')
    def test_auditFiles(self, getEnvMock, extractShowNameMock, createDirectoryMock, directoryExistsMock, extractSeasonNumberMock, extractEpisodeNumberMock, fileExistsMock, osRenameMock, reportItemAlreadyExistsMock, notifyDownloadFinishedMock, loggingInfoMock):

        # config fake data
        fakeEpisodeNumber = 2
        fakeSeasonNumber = 1
        fakeTVShowName = "fakeTVShowName"
        fakeFile1 = f"{fakeTVShowName}.S0{fakeSeasonNumber}.E0{fakeEpisodeNumber}.mp4"
        class FakeFile:
            def __init__(self, name):
                self.name = name
        fakeFiles = [ FakeFile(fakeFile1) ]
        fakeFilteredDownloadingItems = [ fakeFile1 ]

        # config mocks
        getEnvMock.side_effect = getEnvMockFunc
        extractShowNameMock.return_value = fakeTVShowName
        directoryExistsMock.side_effect = [ True, True ]
        extractSeasonNumberMock.return_value = fakeSeasonNumber
        extractEpisodeNumberMock.return_value = fakeEpisodeNumber
        fileExistsMock.return_value = True


        # Case 1 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        #   * file exists
        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)

        # config expected values
        expectedProspectiveFile = f"{fakeTargetTvDir}{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}.mp4"

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_called_with(expectedProspectiveFile, fakeFile1)
        osRenameMock.assert_not_called()

        # Case 1 end ############################################################################


        # Case 2 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        #   * file does not exist

        # reconfig mocks
        directoryExistsMock.side_effect = [ True, True ]
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()

        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)

        # config expected values
        expectedProspectiveFile = f"{fakeTargetTvDir}{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}.mp4"

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDir}{fakeFile1}", expectedProspectiveFile)

        # Case 2 end ############################################################################


        # Case 3 start ############################################################################
        #   * show dir exists
        #   * season dir does not exist
        #   * file does not exist

        # reconfig mocks
        directoryExistsMock.side_effect = [ True, False ]
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()

        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)

        # config expected values
        expectedProspectiveFile = f"{fakeTargetTvDir}{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}.mp4"
        expectedSeasonDir = os.path.join(fakeTargetTvDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedCreateDirectoryCalls = [call(expectedSeasonDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDir}{fakeFile1}", expectedProspectiveFile)

        # Case 3 end ############################################################################


        # Case 4 start ############################################################################
        #   * show dir does not exist
        #   * season dir does not exist
        #   * file does not exist

        # reconfig mocks
        directoryExistsMock.side_effect = [ False, False ]
        fileExistsMock.return_value = False
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()

        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, fakeTargetTvDir)

        # config expected values
        expectedProspectiveFile = f"{fakeTargetTvDir}{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}.mp4"
        expectedSeasonDir = os.path.join(fakeTargetTvDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedTvDir = os.path.join(fakeTargetTvDir, fakeTVShowName)
        expectedCreateDirectoryCalls = [call(expectedSeasonDir), call(expectedTvDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDir}{fakeFile1}", expectedProspectiveFile)

        # Case 4 end ############################################################################


    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch("os.rename")
    @mock.patch("controllers.CompletedDownloadsController.extractSeasonNumber")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    @mock.patch("interfaces.FolderInterface.createDirectory")
    @mock.patch('controllers.CompletedDownloadsController.extractShowName')
    @mock.patch('os.getenv')
    def test_auditDirectories(self, getEnvMock, extractShowNameMock, createDirectoryMock, directoryExistsMock, extractSeasonNumberMock, osRenameMock, reportItemAlreadyExistsMock):

        # config fake data
        fakeSeasonNumber = 1
        fakeTVShowName = "fake TV Show Name"
        fakeDir1 = f"{fakeTVShowName}.S0{fakeSeasonNumber}"
        fakeDirs = [ fakeDir1 ]
        fakeFilteredDownloadingItems = [ fakeDir1 ]

        # config mocks
        getEnvMock.side_effect = getEnvMockFunc
        extractShowNameMock.return_value = fakeTVShowName
        directoryExistsMock.side_effect = [ True, True ]
        extractSeasonNumberMock.return_value = fakeSeasonNumber


        # Case 1 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        CompletedDownloadsController.auditDirectories(fakeDirs, fakeFilteredDownloadingItems, fakeTargetTvDir)

        # config expected values
        expectedProspectiveDirectory = f"{fakeTargetTvDir}{fakeTVShowName}/Season {fakeSeasonNumber}"

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_called_with(expectedProspectiveDirectory, fakeDir1)
        osRenameMock.assert_not_called()

        # Case 1 end ############################################################################


        # Case 2 start ############################################################################
        #   * show dir exists
        #   * season dir does not exist

        # reconfig mocks
        directoryExistsMock.side_effect = [ True, False ]
        reportItemAlreadyExistsMock.reset_mock()

        CompletedDownloadsController.auditDirectories(fakeDirs, fakeFilteredDownloadingItems, fakeTargetTvDir)

        # config expected values
        expectedSeasonDir = os.path.join(fakeTargetTvDir, fakeTVShowName, f"Season {fakeSeasonNumber}")

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDir}/{fakeDir1}", expectedSeasonDir)

        # Case 2 end ############################################################################


        # Case 3 start ############################################################################
        #   * show dir does not exist
        #   * season dir does not exist

        # reconfig mocks
        directoryExistsMock.side_effect = [ False, False ]
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()

        CompletedDownloadsController.auditDirectories(fakeDirs, fakeFilteredDownloadingItems, fakeTargetTvDir)

        # config expected values
        expectedSeasonDir = os.path.join(fakeTargetTvDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedTvDir = os.path.join(fakeTargetTvDir, fakeTVShowName)
        expectedCreateDirectoryCalls = [call(expectedTvDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDir}/{fakeDir1}", expectedSeasonDir)

        # Case 3 end ############################################################################


    @mock.patch("logging.info")
    @mock.patch("interfaces.DownloadsInProgressFileInterface.notifyDownloadFinished")
    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch('os.getenv')
    def test_auditFilesWithFileSystem(self, getEnvMock, reportItemAlreadyExistsMock, notifyDownloadFinishedMock,  loggingInfoMock):

        # init items
        downloadingItems = [
            "fake-tv-show-name.s01.e01.mp4",
            "fake-tv-show-name.s01.e02.mp4"
        ] # representation of what is in the dump_complete folder

        # config fake data #
        mode = PROGRAM_MODE.TV_EPISODES
        fakeFilteredDownloadingItems = {
            "tv-seasons": [],
            "tv-episodes": [
                "fake-tv-show-name.s01.e01.mp4",
                "fake-tv-show-name.s01.e02.mp4",
                "downloadingFile.S01.E03/fakeDownloadingFile2.mp4",
                "fakeDownloadingFile3.mp4"
            ]
        } # this should be the content of the DownloadsInProgressFile 

        # config mocks
        getEnvMock.side_effect = getEnvMockFunc

        # setup fake files
        for path in downloadingItems:
            pathParts = path.split("/")
            newDir = ""
            if len(pathParts) > 1:
                newDir = "/".join(pathParts[:-1])
                os.mkdir(f"{fakeDumpCompleteDir}{newDir}")
            episodeFile = f"{fakeDumpCompleteDir}{newDir}/{pathParts[-1]}"
            os.mknod(episodeFile)

        # assert state is as expected before audit method is called
        self.assertTrue(len(list(os.scandir(fakeTargetTvDir))) == 0)
        self.assertTrue(len(list(os.scandir(fakeDumpCompleteDir))) == 2)

        # run auditDumpCompleteDir
        CompletedDownloadsController.auditDumpCompleteDir(mode, fakeFilteredDownloadingItems["tv-episodes"])

        # assert that the contents of downloadingItems has been moved from the `dummy_directories/dump_complete` directory to the `dummy_directories/tv` directory
        self.assertTrue(len(list(os.scandir(f"{fakeTargetTvDir}fake tv show name/Season 1"))) == 2)
        self.assertTrue(len(list(os.scandir(fakeDumpCompleteDir))) == 0)
        notifyDownloadFinishedMock.assert_called()
        loggingInfoMock.assert_called()
        reportItemAlreadyExistsMock.assert_not_called()

        # clean up moved files
        cleanUpDirs = [ fakeTargetTvDir ]

        for dir in cleanUpDirs:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
