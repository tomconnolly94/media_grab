#!/venv/bin/python

"""The first step is to create an SMTP object, each object is used for connection 
with one server."""

import smtplib
import os

server = smtplib.SMTP('smtp.gmail.com', 587)

def sendMail(message):
    server.ehlo()
    server.starttls()
    server.ehlo()
    #Next, log in to the server
    server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))

    mailSubject = "A new torrent has just been added."

    message = f'Subject: {mailSubject}\n\n{message}'
    #Send the mail
    server.sendmail("tomconnollyapps@gmail.com", "tom.connolly2511@gmail.com", message)
