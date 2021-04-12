# external dependencies
import unittest
import mock
from unittest.mock import call, ANY
import os

# internal dependencies
from interfaces.MailInterface import MailInterface
from dataTypes.MailItem import MailItemType


class TestMailInterface(unittest.TestCase):

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailSingleDev(self, loggingInfoDevMock, osGetEnvMock, smtpMock):
                
        # config inputs
        fakeHeading = "fake heading"
        fakeMessage = "fake message"

        # called testable method
        mailInterface = MailInterface(environment="dev", collateMail=False)
        mailInterface.pushMail(fakeHeading, fakeMessage)

        # mock
        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call("Program is running in dev mode. No email has been sent.")
        ]
        # mock asserts
        loggingInfoDevMock.assert_has_calls(loggingCalls)

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailSingleProduction(self, loggingInfoProdMock, osGetEnvMock, smtpMock):

        # config inputs
        fakeToEmailAddress = "fakeToEmailAddress"
        envValue = "production"
        fakeMailUsername = "fakeMailUsername"
        fakeMailPassword = "fakeMailPassword"

        fakeHeading = "fake heading"
        fakeMessage = "fake message"

        # called testable method
        mailInterface = MailInterface(toEmailAddress=fakeToEmailAddress, environment=envValue,
                                      mailUsername=fakeMailUsername, mailPassword=fakeMailPassword, collateMail=False)

        mailInterface.pushMail(fakeHeading, fakeMessage)

        # mock asserts
        calls = [call("MailInterface:__sendMail called.")]
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

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailMultiDev(self, loggingInfoDevMock, osGetEnvMock, smtpMock):

        # config inputs
        fakeMessage = "fake message"

        # called testable method
        mailInterface = MailInterface(environment="dev")
        mailInterface.pushMail(fakeMessage, MailItemType.ERROR)
        mailInterface.pushMail(fakeMessage, MailItemType.ERROR)

        mailInterface.sendAllCollatedMailItems()

        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call("Program is running in dev mode. No email has been sent.")
        ]
        # mock asserts
        loggingInfoDevMock.assert_has_calls(loggingCalls)


    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendingMailIsNotPossible(self, loggingInfoDevMock, osGetEnvMock, smtpMock):

        # config inputs
        fakeToEmailAddress = "fakeToEmailAddress"
        envValue = "dev"
        fakeMailUsername = "fakeMailUsername"
        fakeMailPassword = "fakeMailPassword"

        fakeHeading = "fake heading"
        fakeMessage = "fake message"

        # config mocks
        osGetEnvMock.return_value = None

        # called testable method - run 1 sending mail is possible
        mailInterfaceSendingPossible = MailInterface(
            toEmailAddress=fakeToEmailAddress, environment=envValue, mailUsername=fakeMailUsername, mailPassword=fakeMailPassword, collateMail=False)

        # push messages
        mailSendSuccess = mailInterfaceSendingPossible.pushMail(
            fakeMessage, MailItemType.ERROR)

        # define calls
        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call("Program is running in dev mode. No email has been sent.")
        ]

        # asserts
        self.assertTrue(mailSendSuccess)
        loggingInfoDevMock.assert_has_calls(loggingCalls)

        # reset mocks
        loggingInfoDevMock.reset_mock()

        # called testable method - run 2 sending mail is not possible
        mailInterfaceSendingNotPossible = MailInterface(environment=envValue, mailUsername=fakeMailUsername, mailPassword=fakeMailPassword, collateMail=False)

        # push messages
        mailSendSuccess = mailInterfaceSendingNotPossible.pushMail(
            fakeMessage, MailItemType.ERROR)

        # define calls
        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call('Sending a notification mail is not possible because at least one of the following values was not provided - toEmailAddress: None, mailUsername: fakeMailUsername, mailPassword: fakeMailPassword')
        ]
        
        # asserts
        self.assertFalse(mailSendSuccess)
        loggingInfoDevMock.assert_has_calls(loggingCalls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
