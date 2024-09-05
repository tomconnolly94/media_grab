# external dependencies
import unittest
from unittest import mock
from unittest.mock import MagicMock
from unittest.mock import call

# internal dependencies
from src.interfaces.MailInterface import MailInterface
from src.dataTypes.MailItem import MailItemType
from src.interfaces.MailInterface import singleNewTorrentMessage


class TestMailInterface(unittest.TestCase):

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailSingleDev(self, loggingInfoDevMock, osGetEnvMock, smtpMock):
                
        # config inputs
        fakeMessage = "fake message"

        # called testable method
        mailInterface = MailInterface(environment="development", collateMail=False)
        mailInterface.pushMail(fakeMessage, MailItemType.NEW_TORRENT)

        # mock
        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call("Program is running in development mode. No email has been sent.")
        ]
        # mock asserts
        loggingInfoDevMock.assert_has_calls(loggingCalls)

    @mock.patch('src.interfaces.MailInterface.EmailMessage')
    @mock.patch('smtplib.SMTP')
    @mock.patch('logging.info')
    def test_sendMailSingleProduction(self, loggingInfoProdMock, smtpMock, EmailMessageMock):

        # config inputs
        fakeToEmailAddress = "fakeToEmailAddress"
        envValue = "production"
        fakeMailUsername = "fakeMailUsername"
        fakeMessage = "fake message"
        EmailMessageMagicMock = MagicMock()
        EmailMessageMock.return_value = EmailMessageMagicMock

        # called testable method
        mailInterface = MailInterface(toEmailAddress=fakeToEmailAddress, environment=envValue,
                                      mailUsername=fakeMailUsername, collateMail=False)

        mailInterface.pushMail(fakeMessage, MailItemType.NEW_TORRENT)

        # mock asserts
        calls = [call("MailInterface:__sendMail called.")]
        loggingInfoProdMock.assert_has_calls(calls)

        calls = [
            call('192.168.0.106'),
            call().send_message(EmailMessageMagicMock),
            call().quit()
        ]
        smtpMock.assert_has_calls(calls)

    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendMailMultiDev(self, loggingInfoDevMock, osGetEnvMock, smtpMock):

        # config inputs
        fakeMessage = "fake message"

        # called testable method
        mailInterface = MailInterface(environment="development")
        mailInterface.pushMail(fakeMessage, MailItemType.ERROR)
        mailInterface.pushMail(fakeMessage, MailItemType.ERROR)

        mailInterface.sendAllCollatedMailItems()

        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call("Program is running in development mode. No email has been sent.")
        ]
        # mock asserts
        loggingInfoDevMock.assert_has_calls(loggingCalls)


    @mock.patch('smtplib.SMTP')
    @mock.patch('os.getenv')
    @mock.patch('logging.info')
    def test_sendingMailIsNotPossible(self, loggingInfoDevMock, osGetEnvMock, smtpMock):

        # config inputs
        fakeToEmailAddress = "fakeToEmailAddress"
        envValue = "development"
        fakeMailUsername = "fakeMailUsername"
        fakeMessage = "fake message"

        # config mocks
        osGetEnvMock.return_value = None

        # called testable method - run 1 sending mail is possible
        mailInterfaceSendingPossible = MailInterface(
            toEmailAddress=fakeToEmailAddress, environment=envValue, mailUsername=fakeMailUsername, collateMail=False)

        # push messages
        mailSendSuccess = mailInterfaceSendingPossible.pushMail(
            fakeMessage, MailItemType.ERROR)

        # define calls
        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call("Program is running in development mode. No email has been sent.")
        ]

        # asserts
        self.assertTrue(mailSendSuccess)
        loggingInfoDevMock.assert_has_calls(loggingCalls)

        # reset mocks
        loggingInfoDevMock.reset_mock()

        # called testable method - run 2 sending mail is not possible
        mailInterfaceSendingNotPossible = MailInterface(environment=envValue, mailUsername=fakeMailUsername, collateMail=False)

        # push messages
        mailSendSuccess = mailInterfaceSendingNotPossible.pushMail(
            fakeMessage, MailItemType.ERROR)

        # define calls
        loggingCalls = [
            call('MailInterface:__sendMail called.'),
            call('Sending a notification mail is not possible because at least one of the following values was not provided - toEmailAddress: None, mailUsername: fakeMailUsername')
        ]
        
        # asserts
        self.assertFalse(mailSendSuccess)
        loggingInfoDevMock.assert_has_calls(loggingCalls)


if __name__ == '__main__':
    unittest.main()


# N.B. test cant be debugged from the vs code side bar, to debug test, add breakpoint and hit f5, this should be fixed soon
