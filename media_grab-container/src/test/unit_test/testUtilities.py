# external dependencies
import os
import shutil

# fake directories for use across multiple tests
dummyDirectoriesDir = f"{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/dummy_directories/"

fakeTargetTvDir = dummyDirectoriesDir + "tv"
fakeDumpCompleteDir = dummyDirectoriesDir + "dump_complete"
fakeRecycleBinDir = dummyDirectoriesDir + "recycle_bin"
fakeLogsDir = "logs"


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
    elif param == "LOGS_DIR":
        return fakeLogsDir
    else:
        assert(None)


def cleanUpDirs(directories, downloadingItems):
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                os.remove(os.path.join(root, file))

            for directory in dirs:
                shutil.rmtree(os.path.join(root, directory))
