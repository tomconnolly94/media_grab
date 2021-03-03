#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging

enterLogMessage = "MailInterface:sendMail called."
finishLogMessage = "Sent notification for torrent add."
toEmailAddress = "tom.connolly@protonmail.com"
environmentEnv = os.getenv("ENVIRONMENT")
mailUsername = os.getenv("MAIL_USERNAME")
mailPassword = os.getenv("MAIL_PASSWORD")


def sendMail(heading, messageBody):
    logging.info(enterLogMessage)

    #only send mail when in production mode
    if environmentEnv == "production":
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.ehlo()
            #Next, log in to the server
            
            server.login(mailUsername, mailPassword)
            #server.login('tomconnollyapps@gmail.com', 'Ring6Door9Sofa3')

            mailContent = f'Subject: {heading}\n\n{messageBody}'
            #Send the email
            server.sendmail(mailUsername, toEmailAddress, mailContent)

            logging.info(finishLogMessage)
    else:
        logging.info(f"Program is running in {environmentEnv} mode. No email has been sent.")


def sendNewTorrentMail(torrentName, torrentExtraInfo, torrentMagnet):
    messageBody = f'ADDED TORRENT: {torrentName} {torrentExtraInfo} \n\n Magnet:{torrentMagnet}'
    sendMail("Media Grab: A new torrent has just been added.", messageBody)


def sendTestMail():
    # test setup to send email using static mail account
    global environmentEnv
    environmentEnv = "production"
    sendMail("Media Grab: Test Message", "test message generated from running the interfaces/MailInterface.py as __main__")


if __name__== "__main__":
    sendTestMail()
