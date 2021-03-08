# external dependencies
import unittest
import mock
import os

# internal dependencies
from controllers import ErrorController


class TestErrorController(unittest.TestCase):

    @mock.patch("interfaces.MailInterface.sendMail")
    @mock.patch("logging.getLoggerClass")
    @mock.patch("logging.error")
    @mock.patch("inspect.getframeinfo")
    @mock.patch("inspect.stack")
    def test_reportError(self, inspectStackMock, getframeinfoMock, loggingErrorMock, getLoggerClassMock, sendMailMock):
        
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

        # call testable function
        ErrorController.reportError(fakeErrorMessage, exception, True)

        # asserts
        getframeinfoMock.assert_called_with(fakeFrame)
        expectedErrorMessage = f"{fakeFileName}:{fakeFunction}():{fakeLineNo} - {fakeErrorMessage}"
        loggingErrorMock.assert_called_with(expectedErrorMessage, exc_info=True)
        sendMailMock.assert_called_with("Houston we have a problem", "fakeFilename:fakeFunction():fakeLineNo - fakeErrorMessage\n\n More logs can be found in: fakeBaseFilename")

