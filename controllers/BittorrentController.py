from qbittorrent import Client
import os

# connect to the qbittorent Web UI
qb = None

def ensureClient():
    global qb
    if qb:
        return qb
    else:
        qb = Client(os.getenv('QBT_URL'))
        return qb

def initTorrentDownload(torrentMagnet):
    global qb
    qb = ensureClient()
    qb.login(os.getenv('QBT_USERNAME'), os.getenv('QBT_PASSWORD'))
    torrentInitResult = qb.download_from_link(torrentMagnet)

    if torrentInitResult == "Ok.":
        return True
    return False