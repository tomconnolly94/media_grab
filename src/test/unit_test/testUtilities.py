# external dependencies
import os

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
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                os.remove(os.path.join(root, file))

            for directory in dirs:
                shutil.rmtree(os.path.join(root, directory))
