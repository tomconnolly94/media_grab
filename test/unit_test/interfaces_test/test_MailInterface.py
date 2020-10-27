# external dependencies
import unittest
import mock
from unittest.mock import call, ANY

# internal dependencies
from interfaces import MailInterface

class TestMailInterface(unittest.TestCase):

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailDev(self, loggingInfoDevMock, osGetEnvMock, smtpMock):

        # config mocks
        osGetEnvMock.return_value = "notProduction"
        
        # config inputs
        fakeMessage = "fake message"

        # called testable method
        MailInterface.sendMail(fakeMessage)

        # mock asserts
        loggingInfoDevMock.assert_called_with("MailInterface:sendMail called.")


    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailProduction(self, loggingInfoProdMock, osGetEnvMock, smtpMock):

        envValue = "production"

        # config mocks
        osGetEnvMock.return_value = envValue

        # config inputs
        fakeMessage = "fake message"

        # called testable method
        MailInterface.sendMail(fakeMessage)

        # mock asserts
        calls = [ call("MailInterface:sendMail called."), call("Sent notification for torrent add.") ]
        loggingInfoProdMock.assert_has_calls(calls)
        calls = [ call("ENVIRONMENT"), call("MAIL_USERNAME"), call("MAIL_PASSWORD") ]
        osGetEnvMock.assert_has_calls(calls)
        calls = [ call().__enter__().starttls(), call().__enter__().ehlo(), call().__enter__().login(envValue, envValue), call().__enter__().sendmail(MailInterface.fromEmailAddress, MailInterface.toEmailAddress, ANY) ]
        smtpMock.assert_has_calls(calls)

        smtpMock.assert_called_once_with('smtp.gmail.com', 587)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
