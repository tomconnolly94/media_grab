#!/venv/bin/python

# external dependencies
from qbittorrent import Client
import os

global qb

def init():
    # create qbittorrent client on program init
    global qb
    qb = Client(os.getenv('QBT_URL'), verify=False)

def initTorrentDownload(torrentMagnet):
    # qb.login(os.getenv('QBT_USERNAME'), os.getenv('QBT_PASSWORD'))

    torrentMagnet = torrentMagnet.replace(" ", "+")

    print(torrentMagnet)
    try:
        qb.download_from_link([torrentMagnet])
        return True
    # except (UnsupportedMediaType415Error, TorrentFileNotFoundError, TorrentFilePermissionError) as torrentFailedException:
    except Exception as torrentFailedException:    
        print(torrentFailedException)
        return False
