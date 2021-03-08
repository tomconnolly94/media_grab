#!/venv/bin/python

# external dependencies
from qbittorrent import Client
import os
import logging

# internal dependencies
from controllers import ErrorController

global qb

def init():
    # create qbittorrent client on program init
    global qb
    qb = Client(os.getenv('QBT_URL'), verify=False)

def initTorrentDownload(torrent):
    
    dumpCompleteDir = os.getenv("DUMP_COMPLETE_DIR")
    dumpCompleteDir = "/home/shares/public/netShare/download/dump_complete"
    downloadPath = os.path.join(dumpCompleteDir, torrent["torrentName"])
    # downloadPath = torrent["torrentName"]
    
    try:
        qbittorrentResponse = qb.download_from_link(torrent["magnet"], savepath=downloadPath)
        if qbittorrentResponse == "Ok.":
            logging.info(f"Torrent added: {torrent['torrentName']}")
            return True
        return False
    except Exception as exception:
        ErrorController.reportError("Exception occurred when submitting torrent magnet to qbittorrent", exception=exception, sendEmail=True)
        return False


def pauseTorrent(torrentName):
    torrents = qb.torrents()

    for torrent in torrents:
        if torrent["name"] == torrentName:
            qb.pause(torrent["hash"])
            return True
    return False
