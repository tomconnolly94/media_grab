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
    global mailInterfaceInstance
    if not mailInterfaceInstance:
        mailInterfaceInstance = MailInterface()
    return mailInterfaceInstance

errorMailHeading = "Houston we have a problem"
singleNewTorrentMessage = "A new torrent has just been added."
multipleNewTorrentsMessage = "New torrents have just been added."


class MailInterface():

    def __init__(self, enterLogMessage=None, toEmailAddress=None, environment=None, mailUsername=None, mailPassword=None, collateMail=True):
        # assign class properties if they are provided, use defaults if they are not
        self.__enterLogMessage = enterLogMessage if enterLogMessage else "MailInterface:__sendMail called."
        self.__toEmailAddress = toEmailAddress if toEmailAddress else "tom.connolly@protonmail.com"
        self.__environment = environment if environment else os.getenv("ENVIRONMENT")
        self.__mailUsername = mailUsername if mailUsername else os.getenv("MAIL_USERNAME")
        self.__mailPassword = mailPassword if mailPassword else os.getenv("MAIL_PASSWORD")
        self.__collateMail = collateMail
        self.__mailItems = []

    ##### Private functions start #####

    def __sendMail(self, heading, messageBody):

        logging.info(self.__enterLogMessage)

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


        elif self.__environment == "dev":
            logging.info(f"Program is running in {self.__environment} mode. No email has been sent.")
        else:
            logging.info(f"Environment mode: {self.__environment} is not recognised.")

    ##### Private functions end #####

    ##### Public functions start #####

    def pushMail(self, messageBody, mailItemType):
        if self.__collateMail:
            self.__mailItems.append(
                MailItem(messageBody, mailItemType))
        else:
            self.__sendMail(singleNewTorrentMessage, messageBody)

    def sendAllCollatedMailItems(self):
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

        if numNewTorrentMessages > 0:
            firstTorrentNameChunk = f"{newTorrentMailMessages[:40]}..."
            multiTorrentMessage = f"{multipleNewTorrentsMessage} - {firstTorrentNameChunk}"
            singleTorrentMessage = f"{singleNewTorrentMessage} - {firstTorrentNameChunk}"

            newTorrentMailMessage = multiTorrentMessage if numNewTorrentMessages > 1 else singleTorrentMessage

            self.__sendMail(newTorrentMailMessage, newTorrentMailMessages)

        if numErrorMessages > 0:
            self.__sendMail(errorMailHeading, errorMailMessages)

    ##### Public functions end #####

if __name__== "__main__":
    mailInterface = MailInterface(enterLogMessage="test sendMail entered", toEmailAddress="tom.connolly@protonmail.com",
                                  environment="production", mailUsername="app.dev.notifications.tc@gmail.com", mailPassword="NKa1q6&zCf^@7$wq", collateMail=True)

    mailInterface.pushMail(
        "test message generated from running the interfaces/MailInterface.py as __main__", MailItemType.NEW_TORRENT)
    mailInterface.pushMail(
        "test message generated from running the interfaces/MailInterface.py as __main__", MailItemType.ERROR)
    mailInterface.sendAllCollatedMailItems()
    pass
