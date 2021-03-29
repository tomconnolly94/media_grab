#!/venv/bin/python

# external dependencies
import enum

class MailItemType(enum.Enum):
   ERROR = 1
   NEW_TORRENT = 2



class MailItem():

    def __init__(self, content, mailItemType=MailItemType.ERROR):
        self.__mailItemType = mailItemType
        self.__content = content


    def getMailItemType(self):
        return self.__mailItemType


    def getContent(self):
        return self.__content
