#!/venv/bin/python

# external dependencies
from qbittorrent import Client
import os

global qb

def init():
    # create qbittorrent client on program init
    global qb
    qb = Client(os.getenv('QBT_URL'))

def initTorrentDownload(torrentMagnet):
    qb.login(os.getenv('QBT_USERNAME'), os.getenv('QBT_PASSWORD'))
    torrentInitResult = qb.download_from_link(torrentMagnet)

    if torrentInitResult == "Ok.":
        return True
    return False
