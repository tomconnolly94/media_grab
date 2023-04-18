#!/venv/bin/python

# external dependencies
try:
    from qbittorrent import Client
except Exception:
    pass
import os
import logging

# internal dependencies


qBittorrentInterfaceInstance = None

# implement singleton pattern


def getInstance():
    """
    getInstance creates/accesses the singleton instance of QBittorrentInterface
    :testedWith: None - glue code
    :return: singleton instance of QBittorrentInterface
    """
    global qBittorrentInterfaceInstance
    if not qBittorrentInterfaceInstance:
        qBittorrentInterfaceInstance = QBittorrentInterface()
    return qBittorrentInterfaceInstance


class QBittorrentInterface():

    def __init__(self, dumpCompleteDir=None, qbittorrentClient=None):
        """
        __init__ initialises a QBittorrentInterface object, creating a client object
        :testedWith: TestCompletedDownloadsController:test_initTorrentDownload
        :return: None
        """
        qbtUrl = os.getenv('QBT_URL')


        if qbtUrl:
            self.__qb = Client(qbtUrl, verify=False)
            self.__qb.login(os.getenv("QBT_USERNAME"), os.getenv("QBT_PASSWORD"))

            
        self.dumpCompleteDir = dumpCompleteDir if dumpCompleteDir else os.getenv("DUMP_COMPLETE_DIR")


    def initTorrentDownload(self, mediaInfoRecord):
        """
        initTorrentDownload extracts a magnet link from a mediaInfoRecord and submits it to qBittorrent for downloading
        :testedWith: TestQBittorrentInterface:test_initTorrentDownload
        :return: the success/failure of the operation
        """
        downloadPath = os.path.join(
            self.dumpCompleteDir, mediaInfoRecord.getMediaGrabId())
        torrentRecord = mediaInfoRecord.getTorrentRecord()

        qbittorrentResponse = self.__qb.download_from_link(torrentRecord.getMagnet(), savepath=downloadPath)
        if qbittorrentResponse == "Ok.":
            logging.info(f"Torrent added: {torrentRecord.getName()}")
            return True
        raise Exception("Response from qbittorent was not 'Ok.'")


    def pauseTorrent(self, torrentName):
        """
        pauseTorrent requests that qBittorrent pause activity on a torrent found by name
        :testedWith: None - too small to be necessary
        :return: the success/failure of the operation
        """
        torrents = self.__qb.torrents()

        for torrent in torrents:
            if torrent["name"] == torrentName:
                self.__qb.pause(torrent["hash"])
                return True
        return False
    

    def overrideQBObject(self, overrideValue):
        """
        overrideQBObject injects a value to be set as the self.__qb object, useful for testing
        :testedWith: None - too small to be necessary
        :return: None
        """
        self.__qb = overrideValue
