#!/venv/bin/python

class MailItem():

    def __init__(self, heading, content):
        self.__heading = heading
        self.__content = content


    def getHeading(self):
        return self.__heading


    def getContent(self):
        return self.__content
