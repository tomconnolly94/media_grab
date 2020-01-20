from qbittorrent import Client

# connect to the qbittorent Web UI
qb = Client("http://127.0.0.1:8081/")

def initTorrentDownload(torrentMagnet):
    result = qb.login("tom", "India2015")
    print(result)
    print(torrentMagnet)
    result = qb.download_from_link(torrentMagnet)
    print(result)
