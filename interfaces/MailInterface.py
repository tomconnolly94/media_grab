#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging

enterLogMessage = "MailInterface:sendMail called."
finishLogMessage = "Sent notification for torrent add."
toEmailAddress = "tom.connolly@protonmail.com"
environment = None
mailUsername = None
mailPassword = None


def init():
    global environment
    environment = os.getenv("ENVIRONMENT")
    global mailUsername
    mailUsername = os.getenv("MAIL_USERNAME")
    global mailPassword
    mailPassword = os.getenv("MAIL_PASSWORD")


def sendMail(heading, messageBody):
    logging.info(enterLogMessage)

    #only send mail when in production mode
    if environment == "production":
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.ehlo()
            #Next, log in to the server
            
            server.login(mailUsername, mailPassword)
            #server.login('tomconnollyapps@gmail.com', 'Ring6Door9Sofa3')

            mailContent = f'Subject: [Media Grab] {heading}\n\n{messageBody}'
            #Send the email
            server.sendmail(mailUsername, toEmailAddress, mailContent)

            logging.info(finishLogMessage)
    elif environment == "dev":
        logging.info(f"Program is running in {environment} mode. No email has been sent.")
    else:
        logging.info(f"Environment mode: {environment} is not recognised.")


def sendNewTorrentMail(torrentName, torrentExtraInfo, torrentMagnet):
    messageBody = f'ADDED TORRENT: {torrentName} {torrentExtraInfo} \n\n Magnet:{torrentMagnet}'
    sendMail("A new torrent has just been added.", messageBody)


def sendTestMail():
    # test setup to send email using static mail account
    global environment
    environment = "production"
    sendMail("Media Grab: Test Message", "test message generated from running the interfaces/MailInterface.py as __main__")


if __name__== "__main__":
    #sendTestMail()
    pass
