#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import MediaIndexFileInterface, MailInterface
from dataTypes.MailItem import MailItemType


def onSuccessfulTorrentAdd(mediaInfoRecord, mode):
	"""
	onSuccessfulTorrentAdd groups operations that should be run upon successfully initiating a download, including updating the mediaIndex.json file and sending an email
	:testedWith: TestNewTorrentController:test_onSuccessfulTorrentAdd
	:return: None
	"""
	# notify MediaIndex file
	MediaIndexFileInterface.writeMediaFile(mediaInfoRecord)

	# send email notification
	torrentExtraInfo = f"Latest episode: {mediaInfoRecord.getLatestEpisodeNumber()}"
	torrentRecord = mediaInfoRecord.getTorrentRecord()
	messageBody = f'ADDED TORRENT: {torrentRecord.getName()} {torrentExtraInfo} \n\n Magnet:{torrentRecord.getMagnet()}'
	MailInterface.getInstance().pushMail(messageBody, MailItemType.NEW_TORRENT)
