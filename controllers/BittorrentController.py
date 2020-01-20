from qbittorrent import Client

# connect to the qbittorent Web UI
qb = Client("http://127.0.0.1:8081/")

def initTorrentDownload(torrentMagnet):
    qb.login("tom", "India2015")
    torrentInitResult = qb.download_from_link(torrentMagnet)

    if torrentInitResult == "Ok.":
        return True
    return False