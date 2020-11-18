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


def sendMail(message):
    logging.info(enterLogMessage)

    #only send mail when in production mode
    if environmentEnv == "production":
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.ehlo()
            #Next, log in to the server
            
            server.login(mailUsername, mailPassword)
            #server.login('tomconnollyapps@gmail.com', 'Ring6Door9Sofa3')

            mailSubject = "Media Grab: A new torrent has just been added."

            message = f'Subject: {mailSubject}\n\n{message}'
            #Send the email
            server.sendmail(mailUsername, toEmailAddress, message)

            logging.info(finishLogMessage)
    else:
        logging.info(f"Program is running in {environmentEnv} mode. No email has been sent.")


if __name__== "__main__":
    # test setup to send email using static mail account
    environmentEnv = "production"
    # leave commented to use default mail account login details 
    #mailUsername = "" # complete this field
    #mailPassword = "" # complete this field
    sendMail("test message generated from running the interfaces/MailInterface.py as __main__")