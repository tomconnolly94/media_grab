#!/venv/bin/python

# external dependencies
from qbittorrent import Client
import os
import logging

global qb

def init():
    # create qbittorrent client on program init
    global qb
    qb = Client(os.getenv('QBT_URL'), verify=False)

def initTorrentDownload(torrentMagnet):
    logging.info(f"Torrent added: {torrentMagnet}")
    try:
        qb.download_from_link([torrentMagnet])
        return True
    except Exception:
        logging.error("Exception occurred", exc_info=True)
        return False
