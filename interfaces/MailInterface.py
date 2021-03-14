#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging

global mailInterfaceInstance
mailInterfaceInstance = None

# implement singleton pattern
def getInstance():
    global mailInterfaceInstance
    if not mailInterfaceInstance:
        mailInterfaceInstance = MailInterface()
    return mailInterfaceInstance

class MailInterface():

    def __init__(self, enterLogMessage=None, toEmailAddress=None, environment=None, mailUsername=None, mailPassword=None):
        # assign class properties if they are provided, use defaults if they are not
        self.enterLogMessage = enterLogMessage if enterLogMessage else "MailInterface:sendMail called."
        self.toEmailAddress = toEmailAddress if toEmailAddress else "tom.connolly@protonmail.com"
        self.environment = environment if environment else os.getenv("ENVIRONMENT")
        self.mailUsername = mailUsername if mailUsername else os.getenv("MAIL_USERNAME")
        self.mailPassword = mailPassword if mailPassword else os.getenv("MAIL_PASSWORD")


    def sendMail(self, heading, messageBody):
        logging.info(self.enterLogMessage)

        #only send mail when in production mode
        if self.environment == "production":
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.ehlo()

                #Next, log in to the server                
                server.login(self.mailUsername, self.mailPassword)
                #server.login('tomconnollyapps@gmail.com', 'Ring6Door9Sofa3')

                mailContent = f'Subject: [Media Grab] {heading}\n\n{messageBody}'

                #Send the email
                server.sendmail(self.mailUsername, self.toEmailAddress, mailContent)
        elif self.environment == "dev":
            logging.info(f"Program is running in {self.environment} mode. No email has been sent.")
        else:
            logging.info(f"Environment mode: {self.environment} is not recognised.")

    
    def sendNewTorrentMail(self, torrentName, torrentExtraInfo, torrentMagnet):
        messageBody = f'ADDED TORRENT: {torrentName} {torrentExtraInfo} \n\n Magnet:{torrentMagnet}'
        self.sendMail("A new torrent has just been added.", messageBody)


    def sendTestMail(self):
        self.environment = "production"
        self.sendMail("Media Grab: Test Message", "test message generated from running the interfaces/MailInterface.py as __main__")


if __name__== "__main__":
    mailInterface = MailInterface() 
    mailInterface.sendTestMail()
    pass
