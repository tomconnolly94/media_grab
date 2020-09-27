import unittest
import mock
from collections import namedtuple
import json 

from scrapers import IndexPageScraper

class TestIndexPageScraper(unittest.TestCase):

    @mock.patch('scrapers.IndexPageScraper.requests.get')
    def test_scrape(self, requestsGetMock):

        torrentData = []
    
        with open('test/unit_test/unit_test_resources/MockIndexPage.html', 'r') as file:
            requestsGetMock.return_value = namedtuple('literal', 'text')(text= file.read().replace('\n', ''))

        torrentItemInfo = IndexPageScraper.scrape("fakeUrl")        
        
        self.assertEqual(len(torrentItemInfo), 64)

        for item in torrentItemInfo:
            self.assertTrue(item["itemText"])
            self.assertTrue(item["itemPageLink"])
            self.assertTrue(item["itemMagnetLink"])
            

if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon

