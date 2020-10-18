#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging


def sendMail(message):
    logging.info("sendMail called")
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
            server.sendmail("tomconnollyapps@gmail.com", "tom.connolly2511@gmail.com", message)

            logging.info("Sending notification for torrent")

#sendMail("test message")