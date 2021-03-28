#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging

# internal dependencies
from dataTypes.MailItem import MailItem

global mailInterfaceInstance
mailInterfaceInstance = None

# implement singleton pattern
def getInstance():
    global mailInterfaceInstance
    if not mailInterfaceInstance:
        mailInterfaceInstance = MailInterface()
    return mailInterfaceInstance


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

    def __sendMail(self, mailItem):

        heading = mailItem.getHeading()
        messageBody = mailItem.getContent()

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


    def __submitNewMailItem(self, mailItem):
        self.__mailItems.append(mailItem)

    ##### Private functions end #####

    ##### Public functions start #####

    def pushMail(self, heading, messageBody):
        if self.__collateMail:
            self.__submitNewMailItem(
                MailItem(heading, messageBody))
        else:
            self.__sendMail(MailItem(heading, messageBody))


    def sendNewTorrentMail(self, torrentName, torrentExtraInfo, torrentMagnet):
        messageBody = f'ADDED TORRENT: {torrentName} {torrentExtraInfo} \n\n Magnet:{torrentMagnet}'
        self.pushMail("A new torrent has just been added.", messageBody)

    
    def sendAllCollatedMailItems(self):
        for mailItem in self.__mailItems:
            self.__sendMail(mailItem)


    def sendTestMail(self):
        self.__environment = "production"
        self.__sendMail("Media Grab: Test Message", "test message generated from running the interfaces/MailInterface.py as __main__")

    ##### Public functions end #####

if __name__== "__main__":
    mailInterface = MailInterface() 
    mailInterface.sendTestMail()
    pass
