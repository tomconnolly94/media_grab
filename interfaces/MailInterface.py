#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging

# internal dependencies
from dataTypes.MailItem import MailItem, MailItemType
from controllers import ErrorController

global mailInterfaceInstance
mailInterfaceInstance = None

# implement singleton pattern
def getInstance():
    """
    getInstance creates/accesses the singleton instance of MailInterface
    :testedWith: None - glue code
    :return: singleton instance of MailInterface
    """
    global mailInterfaceInstance
    if not mailInterfaceInstance:
        mailInterfaceInstance = MailInterface()
    return mailInterfaceInstance

errorMailHeading = "Houston we have a problem"
singleNewTorrentMessage = "A new torrent has just been added."
multipleNewTorrentsMessage = "New torrents have just been added."


class MailInterface():

    def __init__(self, enterLogMessage=None, toEmailAddress=None, environment=None,
                 mailUsername=None, mailPassword=None, collateMail=True):
        """
        __init__ initialises all private members of the object
        :testedWith: None - tested indirectly
        :param enterLogMessage: optional log message to print upon entry to the sendMail message, the param is to allow overwriting for amongst other purposes, testing.
        :param toEmailAddress: optional notification target email address, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        :param environment: optional dev/production mode for the program run, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        :param mailUsername: optional username for a mail account to send notifications from, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        :param mailPassword: optional password for the notification email account, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        :param collateMail: optional mode that allows a collation of all messages to prevent many emails being fired off for one program run, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        """
        # assign class properties if they are provided, use defaults if they are not
        self.__enterLogMessage = enterLogMessage if enterLogMessage else "MailInterface:__sendMail called."
        self.__toEmailAddress = toEmailAddress if toEmailAddress else os.getenv(
            "ENVIRONMENT")
        self.__environment = environment if environment else os.getenv("ENVIRONMENT")
        self.__mailUsername = mailUsername if mailUsername else os.getenv("MAIL_USERNAME")
        self.__mailPassword = mailPassword if mailPassword else os.getenv("MAIL_PASSWORD")
        self.__collateMail = collateMail
        self.__mailItems = []

    ##### Private functions start #####

    def __sendMail(self, heading, messageBody):
        """
        __sendMail sends an email containing a notification
        :testedWith: TestMailInterface:test_sendMailSingleDev, TestMailInterface:test_sendMailSingleProduction, TestMailInterface:test_sendMailMultiDev
        :param heading: the subject line for the email to be sent
        :param messageBody: the message body of the email to be sent
        :return: success/failure of the operation
        """
        logging.info(self.__enterLogMessage)

        if self.__sendingMailIsNotPossible():
            return False

        if self.__environment == "production":
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                # init mail server connection
                server.starttls()
                server.ehlo()

                # log in to the server                
                server.login(self.__mailUsername, self.__mailPassword)

                mailContent = f'Subject: [Media Grab] {heading}\n\n{messageBody}'
                server.sendmail(self.__mailUsername,
                                    self.__toEmailAddress, 
                                    mailContent)
                return True


        elif self.__environment == "dev":
            logging.info(f"Program is running in {self.__environment} mode. No email has been sent.")
            return True
        else:
            logging.info(f"Environment mode: {self.__environment} is not recognised.")
            return False

    def __sendingMailIsNotPossible(self):
        """
        __sendingMailIsNotPossible checks that the private members required to send an email are set.
        :testedWith: TestMailInterface:test_sendingMailIsNotPossible
        :return: whether it is possible to send an email with the current configuration of the MailInterface 
        """
        if self.__toEmailAddress and self.__mailUsername and self.__mailPassword:
            return False

        logging.info(
            f"Sending a notification mail is not possible because at least one of the following values was not provided - toEmailAddress: {self.__toEmailAddress}, mailUsername: {self.__mailUsername}, mailPassword: {self.__mailPassword}")
        return True

    ##### Private functions end #####

    ##### Public functions start #####

    def pushMail(self, messageBody, mailItemType):
        """
        pushMail submits a message to either be emailed immediately or at the end of the program run
        :testedWith: TestMailInterface:test_sendingMailIsNotPossible
        :param messageBody: the text content of the message
        :param mailItemType: the type of the message (error|info)
        :return: the success of the mail submission
        """
        if self.__collateMail:
            self.__mailItems.append(
                MailItem(messageBody, mailItemType))
            return True
        else:
            return self.__sendMail(singleNewTorrentMessage, messageBody)
    
    def sendAllCollatedMailItems(self):
        """
        sendAllCollatedMailItems formats all submitted mail items into one large email and sends that email
        :testedWith: TestMailInterface:test_sendMailMultiDev
        :return: the success of the operation
        """
        errorMailMessages = ""
        newTorrentMailMessages = ""

        numErrorMessages = 0
        numNewTorrentMessages = 0
        messageSuffix = "\n\n\n----------------------------------------\n"

        for mailItem in self.__mailItems:
            if mailItem.getMailItemType() == MailItemType.ERROR:
                errorMailMessages += mailItem.getContent() + messageSuffix
                numErrorMessages += 1
            elif mailItem.getMailItemType() == MailItemType.NEW_TORRENT:
                newTorrentMailMessages += mailItem.getContent() + messageSuffix
                numNewTorrentMessages += 1
            else:
                ErrorController.reportError(f"MailItemType: {mailItem.getMailItemType()} not handled!")
                return False
        
        if numNewTorrentMessages > 0:
<<<<<<< HEAD
            firstTorrentNameChunk = f"{newTorrentMailMessages[:40]}..."
=======
            firstTorrentNameChunk = f"{newTorrentMailMessages[0][:40]}..."
>>>>>>> develop
            multiTorrentMessage = f"{multipleNewTorrentsMessage} - {firstTorrentNameChunk}"
            singleTorrentMessage = f"{singleNewTorrentMessage} - {firstTorrentNameChunk}"

            newTorrentMailMessage = multiTorrentMessage if numNewTorrentMessages > 1 else singleTorrentMessage

            self.__sendMail(newTorrentMailMessage, newTorrentMailMessages)

        if numErrorMessages > 0:
            self.__sendMail(errorMailHeading, errorMailMessages)

    ##### Public functions end #####

if __name__== "__main__":
    mailInterface = MailInterface(enterLogMessage="test sendMail entered", toEmailAddress="tom.connolly@protonmail.com",
                                  environment="production", mailUsername="app.dev.notifications.tc@gmail.com", mailPassword="", collateMail=True)

    mailInterface.pushMail(
        "test message generated from running the interfaces/MailInterface.py as __main__", MailItemType.NEW_TORRENT)
    mailInterface.pushMail(
        "test message generated from running the interfaces/MailInterface.py as __main__", MailItemType.ERROR)
    mailInterface.sendAllCollatedMailItems()
    pass
