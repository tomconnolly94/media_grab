#!/venv/bin/python

# external dependencies
import unittest
import mock
from mock import MagicMock
import os

# internal dependencies
from src.controllers import ErrorController
from src.dataTypes.MailItem import MailItemType


class TestErrorController(unittest.TestCase):

    @mock.patch("src.interfaces.MailInterface.getInstance")
    @mock.patch("logging.getLoggerClass")
    @mock.patch("logging.error")
    @mock.patch("inspect.getframeinfo")
    @mock.patch("inspect.stack")
    def test_reportError(self, inspectStackMock, getframeinfoMock, loggingErrorMock, getLoggerClassMock, mailInterfaceGetInstanceMock):
        
        # config fake values
        fakeErrorMessage = "fakeErrorMessage"
        exception = Exception(fakeErrorMessage)
        fakeFrame = "frame"
        fakeBaseFilename = "fakeBaseFilename"
        fakeFileName = "fakeFilename"
        fakeFunction = "fakeFunction"
        fakeLineNo = "fakeLineNo"

        # define mock objects
        class FakeFrameInfo():
            def __init__(self):
                self.filename = fakeFileName
                self.function = fakeFunction
                self.lineno = fakeLineNo

        class FakeLogHandler():
            def __init__(self):
                self.baseFilename = fakeBaseFilename

        class FakeRoot():
            def __init__(self):
                self.handlers = [ FakeLogHandler() ]

        class FakeLoggerClass():
            def __init__(self):
                self.root = FakeRoot()

        # config mock values
        inspectStackMock.return_value = ["first", [fakeFrame]]
        getframeinfoMock.return_value = FakeFrameInfo()
        getLoggerClassMock.return_value = FakeLoggerClass()

        # create mock for instance
        mailInterfaceInstanceMock = MagicMock()
        # assign mocked instance to return_value for mocked getInstance()
        mailInterfaceGetInstanceMock.return_value = mailInterfaceInstanceMock


        # call testable function
        ErrorController.reportError(fakeErrorMessage, exception, True)

        # asserts
        getframeinfoMock.assert_called_with(fakeFrame)
        expectedErrorMessage = f"{fakeFileName}:{fakeFunction}():{fakeLineNo} - {fakeErrorMessage}"
        loggingErrorMock.assert_called_with(expectedErrorMessage, exc_info=True)
        mailInterfaceInstanceMock.pushMail.assert_called_with("fakeFilename:fakeFunction():fakeLineNo - fakeErrorMessage\n\n More logs can be found in: fakeBaseFilename", MailItemType.ERROR)

