# external dependencies
import unittest
import mock
import os

# internal dependencies
from src.interfaces import FolderInterface

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


class TestFolderInterface(unittest.TestCase):

    @mock.patch('interfaces.FolderInterface.deleteDir')
    @mock.patch('logging.info')
    @mock.patch('shutil.move')
    @mock.patch('os.getenv')
    @mock.patch.dict('os.environ', {"RECYCLE_BIN_DIR": fakeRecycleBinDir, "OTHER_ENV_VAR": "other_env_var"}, clear=True)
    def test_recycleOrDeleteDir(self, osGetEnvMock, shutilMoveMock, loggingInfoMock, deleteDirMock):

        # config fake data
        fakeDirectoryPath = "fake/dir/path"

        # config mocks
        osGetEnvMock.side_effect = getEnvMockFunc

        # run testable function (with recycleBinDir accessible) - run 1
        operationSuccess = FolderInterface.recycleOrDeleteDir(fakeDirectoryPath)

        # mock asserts
        self.assertTrue(operationSuccess)
        osGetEnvMock.assert_called_with("RECYCLE_BIN_DIR")
        shutilMoveMock.assert_called_with(fakeDirectoryPath, fakeRecycleBinDir)
        loggingInfoMock.assert_called_with(
            f"Stored '{fakeDirectoryPath}' in '{fakeRecycleBinDir}', in case it is needed. Please remember to delete items from here.")
        deleteDirMock.assert_not_called()

        # config mocks
        del os.environ["RECYCLE_BIN_DIR"]
        osGetEnvMock.reset_mock()
        shutilMoveMock.reset_mock()
        loggingInfoMock.reset_mock()
        deleteDirMock.reset_mock()

        # run testable function (with recycleBinDir inaccessible) - run 2
        FolderInterface.recycleOrDeleteDir(fakeDirectoryPath)

        # mock asserts
        self.assertTrue(operationSuccess)
        osGetEnvMock.assert_not_called()
        shutilMoveMock.assert_not_called()
        loggingInfoMock.assert_called_with(
            f"`RECYCLE_BIN_DIR` env value not specified in .env file so '{fakeDirectoryPath}' cannot be recycled.")
        deleteDirMock.assert_called_with(fakeDirectoryPath)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
