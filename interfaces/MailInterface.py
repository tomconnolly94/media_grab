#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging

enterLogMessage = "MailInterface:sendMail called."
finishLogMessage = "Sent notification for torrent add."
fromEmailAddress = "tomconnollyapps@gmail.com"
toEmailAddress = "tom.connolly2511@gmail.com"

def sendMail(message):
    logging.info(enterLogMessage)
    if os.getenv("ENVIRONMENT") == "production":
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.ehlo()
            #Next, log in to the server
            
            server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
            #server.login('tomconnollyapps@gmail.com', 'Ring6Door9Sofa3')

            mailSubject = "A new torrent has just been added."

            message = f'Subject: {mailSubject}\n\n{message}'
            #Send the mail
            server.sendmail(fromEmailAddress, toEmailAddress, message)

            logging.info(finishLogMessage)
