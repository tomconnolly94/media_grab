#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import MediaIndexFileInterface, MailInterface


def onSuccessfulTorrentAdd(mediaInfoRecord, mode):

	# notify MediaIndex file
	MediaIndexFileInterface.writeMediaFile(mediaInfoRecord)

	# send email notification
	torrentExtraInfo = f"Latest episode: {mediaInfoRecord.getLatestEpisodeNumber()}"
	torrentRecord = mediaInfoRecord.getTorrentRecord()
	MailInterface.getInstance().sendNewTorrentMail(torrentRecord.getName(), torrentExtraInfo, torrentRecord.getMagnet())
