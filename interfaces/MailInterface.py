#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging

enterLogMessage = "MailInterface:sendMail called."
finishLogMessage = "Sent notification for torrent add."
fromEmailAddress = "tomconnollyapps@gmail.com"
#toEmailAddress = "tom.connolly2511@gmail.com"
toEmailAddress = "totomconnollyapps@gmail.com"

try:
    environmentEnv = os.getenv("ENVIRONMENT")
    mailUsername = os.getenv("MAIL_USERNAME")
    mailPassword = os.getenv("MAIL_PASSWORD")
except:
    logging.error("os.getenv not available")


def sendMail(message):
    logging.info(enterLogMessage)
    if environmentEnv == "production":
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.ehlo()
            #Next, log in to the server
            
            server.login(mailUsername, mailPassword)
            #server.login('tomconnollyapps@gmail.com', 'Ring6Door9Sofa3')

            mailSubject = "A new torrent has just been added."

            message = f'Subject: {mailSubject}\n\n{message}'
            #Send the mail
            server.sendmail(fromEmailAddress, toEmailAddress, message)

            logging.info(finishLogMessage)


if __name__== "__main__":
    environmentEnv = "production"
    mailUsername = "tomconnollyapps.gmail.com"
    mailPassword = "Ring6Door9Sofa3"
    sendMail("test message generated from running the interfaces/MailInterface.py as __main__")