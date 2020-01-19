import libtorrent as lt
import time

ses = lt.session()
ses.listen_on(6881, 6891)
#downloadTargetDir = "/home/pi/Downloads"
downloadTargetDir = "/home/tom/downloads/"
params = {
    "save_path": downloadTargetDir,
    "storage_mode": lt.storage_mode_t(2),
    "paused": False,
    "auto_managed": True,
    "duplicate_is_error": True
}

def getMetadata(handle):
    print("downloading metadata...")
    while (not handle.has_metadata()):
        time.sleep(1)

def initTorrent(torrentMagnet):    
    handle = lt.add_magnet_uri(ses, torrentMagnet, params)
    ses.start_dht()

    getMetadata(handle)

    print("got metadata, starting torrent download...")
    while (handle.status().state != lt.torrent_status.seeding):
        s = handle.status()
        state_str = ["queued", "checking", "downloading metadata", \
                    "downloading", "finished", "seeding", "allocating"]
        print("%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s %.3" % \
                    (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                    s.num_peers, state_str[s.state], s.total_download/1000000))
        time.sleep(5)