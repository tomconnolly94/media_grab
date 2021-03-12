# external dependencies
import unittest
import mock
from unittest.mock import call, ANY
import os

# internal dependencies
from interfaces.MailInterface import MailInterface

class TestMailInterface(unittest.TestCase):

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailDev(self, loggingInfoDevMock, osGetEnvMock, smtpMock):
                
        # config inputs
        fakeHeading = "fake heading"
        fakeMessage = "fake message"

        # called testable method
        mailInterface = MailInterface(environment="dev")
        mailInterface.sendMail(fakeHeading, fakeMessage)

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

        fakeHeading = "fake heading"
        fakeMessage = "fake message"

        # called testable method
        mailInterface = MailInterface(toEmailAddress=fakeToEmailAddress, environment=envValue, mailUsername=fakeMailUsername, mailPassword=fakeMailPassword)

        mailInterface.sendMail(fakeHeading, fakeMessage)

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

        self.assertIsNotNone(mailInterface.environment)
        self.assertIsNotNone(mailInterface.mailUsername)
        self.assertIsNotNone(mailInterface.mailPassword)

if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
