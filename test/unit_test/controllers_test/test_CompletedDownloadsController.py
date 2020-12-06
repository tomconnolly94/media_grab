# external dependencies
import unittest
import mock
import os
from unittest.mock import call

# internal dependencies
from controllers import CompletedDownloadsController

class TestCompletedDownloadsController(unittest.TestCase):


    def test_extractShowName(self):
        expectedFakeShowName = "fakeShow"
        fakeShowNamesSuccessful = [
            "fakeShow ", 
            "fakeShow - S01",
            "fakeShow - S01E01",
            "fakeShow -   S01E01",
            "fakeShow.S01E01",
            "fakeShow.S01.E01",
            "FakeShow.S01.E01",
            "fakeShow.S01"
        ]

        for fakeShowName in fakeShowNamesSuccessful:
            actualFakeShowName = CompletedDownloadsController.extractShowName(fakeShowName)
            self.assertEqual(expectedFakeShowName, actualFakeShowName)


    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch("os.rename")
    @mock.patch("interfaces.FolderInterface.fileExists")
    @mock.patch("controllers.CompletedDownloadsController.extractEpisodeNumber")
    @mock.patch("controllers.CompletedDownloadsController.extractSeasonNumber")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    @mock.patch("controllers.CompletedDownloadsController.createDirectory")
    @mock.patch('controllers.CompletedDownloadsController.extractShowName')
    def test_auditFiles(self, extractShowNameMock, createDirectoryMock, directoryExistsMock, extractSeasonNumberMock, extractEpisodeNumberMock, fileExistsMock, osRenameMock, reportItemAlreadyExistsMock):

        # config fake data
        fakeDumpCompleteDirPath = "fakeDumpCompleteDirPath"
        CompletedDownloadsController.dumpCompleteDirPath = fakeDumpCompleteDirPath
        fakeEpisodeNumber = 2
        fakeSeasonNumber = 1
        fakeTVShowName = "fakeTVShowName"
        fakeFile1 = f"{fakeTVShowName}.S0{fakeSeasonNumber}.E0{fakeEpisodeNumber}"
        fakeFiles = [ fakeFile1 ]
        fakeFilteredDownloadingItems = [ fakeFile1 ]
        targetDir = "fakeTargetDir"

        # config mocks
        extractShowNameMock.return_value = fakeTVShowName
        directoryExistsMock.side_effect = [ True, True ]
        extractSeasonNumberMock.return_value = fakeSeasonNumber
        extractEpisodeNumberMock.return_value = fakeEpisodeNumber
        fileExistsMock.return_value = True


        # Case 1 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        #   * file exists
        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, targetDir)

        # config expected values
        expectedProspectiveFile = f"{targetDir}/{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}"

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

        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, targetDir)

        # config expected values
        expectedProspectiveFile = f"{targetDir}/{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}"

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDirPath}/{fakeFile1}", expectedProspectiveFile)

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

        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, targetDir)

        # config expected values
        expectedProspectiveFile = f"{targetDir}/{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}"
        expectedSeasonDir = os.path.join(targetDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedCreateDirectoryCalls = [call(expectedSeasonDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDirPath}/{fakeFile1}", expectedProspectiveFile)

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

        CompletedDownloadsController.auditFiles(fakeFiles, fakeFilteredDownloadingItems, targetDir)

        # config expected values
        expectedProspectiveFile = f"{targetDir}/{fakeTVShowName}/Season {fakeSeasonNumber}/{fakeTVShowName} - S0{fakeSeasonNumber}E0{fakeEpisodeNumber}"
        expectedSeasonDir = os.path.join(targetDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedTvDir = os.path.join(targetDir, fakeTVShowName)
        expectedCreateDirectoryCalls = [call(expectedSeasonDir), call(expectedTvDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDirPath}/{fakeFile1}", expectedProspectiveFile)

        # Case 4 end ############################################################################


    @mock.patch("controllers.CompletedDownloadsController.reportItemAlreadyExists")
    @mock.patch("os.rename")
    @mock.patch("controllers.CompletedDownloadsController.extractSeasonNumber")
    @mock.patch("interfaces.FolderInterface.directoryExists")
    @mock.patch("controllers.CompletedDownloadsController.createDirectory")
    @mock.patch('controllers.CompletedDownloadsController.extractShowName')
    def test_auditDirectories(self, extractShowNameMock, createDirectoryMock, directoryExistsMock, extractSeasonNumberMock, osRenameMock, reportItemAlreadyExistsMock):

        # config fake data
        fakeDumpCompleteDirPath = "fakeDumpCompleteDirPath"
        CompletedDownloadsController.dumpCompleteDirPath = fakeDumpCompleteDirPath
        fakeSeasonNumber = 1
        fakeTVShowName = "fakeTVShowName"
        fakeDir1 = f"{fakeTVShowName}.S0{fakeSeasonNumber}"
        fakeDirs = [ fakeDir1 ]
        fakeFilteredDownloadingItems = [ fakeDir1 ]
        targetDir = "fakeTargetDir"

        # config mocks
        extractShowNameMock.return_value = fakeTVShowName
        directoryExistsMock.side_effect = [ True, True ]
        extractSeasonNumberMock.return_value = fakeSeasonNumber


        # Case 1 start ############################################################################
        #   * show dir exists
        #   * season dir exists
        CompletedDownloadsController.auditDirectories(fakeDirs, fakeFilteredDownloadingItems, targetDir)

        # config expected values
        expectedProspectiveDirectory = f"{targetDir}/{fakeTVShowName}/Season {fakeSeasonNumber}"

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

        CompletedDownloadsController.auditDirectories(fakeDirs, fakeFilteredDownloadingItems, targetDir)

        # config expected values
        expectedSeasonDir = os.path.join(targetDir, fakeTVShowName, f"Season {fakeSeasonNumber}")

        # asserts
        createDirectoryMock.assert_not_called()
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDirPath}/{fakeDir1}", expectedSeasonDir)

        # Case 2 end ############################################################################


        # Case 3 start ############################################################################
        #   * show dir does not exist
        #   * season dir does not exist

        # reconfig mocks
        directoryExistsMock.side_effect = [ False, False ]
        reportItemAlreadyExistsMock.reset_mock()
        osRenameMock.reset_mock()

        CompletedDownloadsController.auditDirectories(fakeDirs, fakeFilteredDownloadingItems, targetDir)

        # config expected values
        expectedSeasonDir = os.path.join(targetDir, fakeTVShowName, f"Season {fakeSeasonNumber}")
        expectedTvDir = os.path.join(targetDir, fakeTVShowName)
        expectedCreateDirectoryCalls = [call(expectedTvDir)]

        # asserts
        createDirectoryMock.assert_has_calls(expectedCreateDirectoryCalls)
        reportItemAlreadyExistsMock.assert_not_called()
        osRenameMock.assert_called_with(f"{fakeDumpCompleteDirPath}/{fakeDir1}", expectedSeasonDir)

        # Case 3 end ############################################################################


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
