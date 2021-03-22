#!/venv/bin/python

# external dependencies
from qbittorrent import Client
import os
import logging

# internal dependencies
from controllers import ErrorController

qBittorrentInterfaceInstance = None

# implement singleton pattern
def getInstance():
    global qBittorrentInterfaceInstance
    if not qBittorrentInterfaceInstance:
        qBittorrentInterfaceInstance = QBittorrentInterface()
    return qBittorrentInterfaceInstance


class QBittorrentInterface():


    def __init__(self, dumpCompleteDir=None):
        qbtUrl = os.getenv('QBT_URL')

        if qbtUrl:
            self.qb = Client(qbtUrl, verify=False)
            
        self.dumpCompleteDir = dumpCompleteDir if dumpCompleteDir else os.getenv("DUMP_COMPLETE_DIR")


    def initTorrentDownload(self, mediaInfoRecord):
        downloadPath = os.path.join(self.dumpCompleteDir, mediaInfoRecord.getMediaGrabId())
        torrentRecord = mediaInfoRecord.getTorrentRecord()
        
        try:
            qbittorrentResponse = self.qb.download_from_link(torrentRecord.getMagnet(), savepath=downloadPath)
            if qbittorrentResponse == "Ok.":
                logging.info(f"Torrent added: {torrentRecord.getName()}")
                return True
            return False
        except Exception as exception:
            ErrorController.reportError("Exception occurred when submitting torrent magnet to qbittorrent", exception=exception, sendEmail=True)
            return False


    def pauseTorrent(self, torrentName):
        torrents = self.qb.torrents()

        for torrent in torrents:
            if torrent["name"] == torrentName:
                self.qb.pause(torrent["hash"])
                return True
        return False
