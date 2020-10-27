# external dependencies
import unittest
import mock

# internal dependencies
from interfaces import MediaFileInterface

class TestMediaFileInterface(unittest.TestCase):

    def test_sendMailDev(self):

        # config inputs        
        fakeMediaInfoRecords = [
            {
                "name": "fakeMediaInfoName1",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "fakeMediaInfoName2",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            },
            {
                "name": "fakeMediaInfoName3",
                "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
            }
        ]

        relevantRecord = 1
        relevantField = "latestSeason"
        queryRecord = fakeMediaInfoRecords[0]
        queryRecord["typeSpecificData"][relevantField] = 2

        # called testable method
        updatedMedia = MediaFileInterface.updateMedia(fakeMediaInfoRecords, queryRecord, relevantField)

        self.assertEqual(2, updatedMedia[0]["typeSpecificData"][relevantField])

        relevantRecord = 1
        relevantField = "latestEpisode"
        queryRecord = fakeMediaInfoRecords[relevantRecord]
        queryRecord["typeSpecificData"]["latestEpisode"] = 2
        # called testable method
        updatedMedia = MediaFileInterface.updateMedia(fakeMediaInfoRecords, queryRecord, relevantField)

        self.assertEqual(2, updatedMedia[relevantRecord]["typeSpecificData"][relevantField])

        nonExistentRecord = {
            "name": "fakeMediaInfoName4",
            "typeSpecificData": { "latestSeason": 1, "latestEpisode": 1 }
        }
        # called testable method
        updatedMedia = MediaFileInterface.updateMedia(fakeMediaInfoRecords, nonExistentRecord, "latestSeason")

        self.assertEqual(None, updatedMedia)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
