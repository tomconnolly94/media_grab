# external dependencies
import unittest
import mock
from unittest.mock import call, ANY
import os

# internal dependencies
from interfaces import MailInterface

class TestMailInterface(unittest.TestCase):

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailDev(self, loggingInfoDevMock, osGetEnvMock, smtpMock):
        
        MailInterface.environment = "dev"
        
        # config inputs
        fakeHeading = "fake heading"
        fakeMessage = "fake message"

        # called testable method
        MailInterface.sendMail(fakeHeading, fakeMessage)

        # mock asserts
        loggingInfoDevMock.assert_called_with("Program is running in dev mode. No email has been sent.")


    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailProduction(self, loggingInfoProdMock, osGetEnvMock, smtpMock):

        # config inputs
        fakeToEmailAddress = "fakeToEmailAddress"
        envValue = "production"
        fakeMailUsername = "fakeMailUsername"
        fakeMailPassword = "fakeMailPassword"

        # override env values
        MailInterface.toEmailAddress = fakeToEmailAddress
        MailInterface.environment = envValue
        MailInterface.mailUsername = fakeMailUsername
        MailInterface.mailPassword = fakeMailPassword

        fakeHeading = "fake heading"
        fakeMessage = "fake message"

        # called testable method
        MailInterface.sendMail(fakeHeading, fakeMessage)

        # mock asserts
        calls = [ call("MailInterface:sendMail called.")]
        loggingInfoProdMock.assert_has_calls(calls)

        calls = [
            call('smtp.gmail.com', 587),
            call().__enter__(),
            call().__enter__().starttls(),
            call().__enter__().ehlo(),
            call().__enter__().login(fakeMailUsername, fakeMailPassword),
            call().__enter__().sendmail(fakeMailUsername, fakeToEmailAddress, f'Subject: [Media Grab] {fakeHeading}\n\n{fakeMessage}'),
            call().__exit__(None, None, None)
        ]
        smtpMock.assert_has_calls(calls)

        self.assertIsNotNone(MailInterface.environment)
        self.assertIsNotNone(MailInterface.mailUsername)
        self.assertIsNotNone(MailInterface.mailPassword)

if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
