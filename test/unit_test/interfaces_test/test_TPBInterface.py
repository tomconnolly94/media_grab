# external dependencies
import unittest
import mock

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


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
