# external dependencies
import unittest
import mock
import json

# internal dependencies
from interfaces import TPBInterface

class TestTPBInterface(unittest.TestCase):

    @mock.patch("interfaces.TPBInterface.TPB")
    @mock.patch("os.getenv")
    @mock.patch("interfaces.TPBInterface.getTPBProxySites")
    def test_initDev(self, getTPBProxySitesMock, osGetEnvMock, tpbMock):

        fakeProxySites = ["proxyTPBUrl1", "proxyTPBUrl2", "proxyTPBUrl3"]
        getTPBProxySitesMock.return_value = fakeProxySites
        osGetEnvMock.return_value = "notProduction"

        TPBInterface.init()

        tpbMock.assert_called_once_with(fakeProxySites[0])

    
    @mock.patch("requests.get")
    def test_getTPBProxySites(self, getMock):

        class MockResponse:
            def __init__(self, json_data):
                self.json_data = json_data

            def json(self):
                return self.json_data

        getMock.return_value = MockResponse(json.loads("""{"proxies":{"1":{"domain":"tpbbazpirate.in","speed":2.65,"secure":true,"country":"BE","probed":true},"2":{"domain":"unblocktpb247.org","speed":1.51,"secure":true,"country":"SE","probed":true},"3":{"domain":"tpbahoy.art","speed":1.66,"secure":true,"country":"ES","probed":true},"4":{"domain":"tpblife.info","speed":1.48,"secure":true,"country":"GB","probed":true},"5":{"domain":"bayindia.net","speed":1.08,"secure":true,"country":"DK","probed":true},"6":{"domain":"tpbfree.in","speed":0.67,"secure":true,"country":"DK","probed":true},"7":{"domain":"proxtpb.link","speed":1.21,"secure":true,"country":"NO","probed":true},"8":{"domain":"tpbportalpirate.link","speed":1.41,"secure":true,"country":"ES","probed":true},"9":{"domain":"tpbindia.fans","speed":2.81,"secure":true,"country":"AU","probed":true},"10":{"domain":"proxyukpass.org","speed":0.97,"secure":true,"country":"SE","probed":true},"11":{"domain":"indiatpb.rocks","speed":2.4,"secure":true,"country":"DK","probed":true},"12":{"domain":"ukpirate247.org","speed":2.59,"secure":true,"country":"NO","probed":true},"13":{"domain":"tpbtpb.tel","speed":1.39,"secure":true,"country":"PT","probed":true},"14":{"domain":"baypiratepiraat.info","speed":1.45,"secure":true,"country":"AU","probed":true},"16":{"domain":"beaindia.org","speed":1.67,"secure":true,"country":"SE","probed":true},"17":{"domain":"baybaypirate.info","speed":0.64,"secure":true,"country":"BE","probed":true},"18":{"domain":"tpbairproxy.org","speed":2.22,"secure":true,"country":"SE","probed":true},"19":{"domain":"tpblautbay.one","speed":2.69,"secure":true,"country":"SE","probed":true},"20":{"domain":"tpbunblocktpb.net","speed":1.96,"secure":true,"country":"IN","probed":true},"21":{"domain":"redtpb.link","speed":2.06,"secure":true,"country":"NL","probed":true},"22":{"domain":"indiaboat.art","speed":2.07,"secure":true,"country":"IN","probed":true},"23":{"domain":"proxyonered.top","speed":2.46,"secure":true,"country":"BE","probed":true},"24":{"domain":"piratefreeproxy.in","speed":0.54,"secure":true,"country":"ES","probed":true},"26":{"domain":"toppiratebaz.org","speed":1.27,"secure":true,"country":"DE","probed":true}},"meta":{"last_updated":1603917601}}"""))



        actualProxySites = TPBInterface.getTPBProxySites()
        expectedProxySites = ['tpbbazpirate.in', 'unblocktpb247.org', 'tpbahoy.art', 'tpblife.info', 'bayindia.net', 'tpbfree.in', 'proxtpb.link', 'tpbportalpirate.link', 'tpbindia.fans', 'proxyukpass.org', 'indiatpb.rocks', 'ukpirate247.org', 'tpbtpb.tel', 'baypiratepiraat.info', 'beaindia.org', 'baybaypirate.info', 'tpbairproxy.org', 'tpblautbay.one', 'tpbunblocktpb.net', 'redtpb.link', 'indiaboat.art', 'proxyonered.top', 'piratefreeproxy.in', 'toppiratebaz.org']
        self.assertEqual(expectedProxySites, actualProxySites)


    @mock.patch("interfaces.TPBInterface.query")
    def test_getTorrentRecords(self, queryMock):
        TPBQueryResponses = [[], ["torrent1", "torrent2", "torrent3"]]
        queryMock.side_effect = TPBQueryResponses
        queries = ["fakeQueryString1", "fakeQueryString2", "fakeQueryString3"]

        torrentRecords = TPBInterface.getTorrentRecords(queries)

        self.assertEqual(TPBQueryResponses[1], torrentRecords)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon