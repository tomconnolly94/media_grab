#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import MediaIndexFileInterface, MailInterface, DownloadsInProgressFileInterface


def onSuccessfulTorrentAdd(mediaInfoRecord, updateableField, torrentMagnet, mode):

	# notify MediaIndex file
	MediaIndexFileInterface.writeMediaFile(mediaInfoRecord, updateableField)

	# send email notification
	torrentExtraInfo = f"{updateableField} {mediaInfoRecord['typeSpecificData'][updateableField]}"
	MailInterface.getInstance().sendNewTorrentMail(mediaInfoRecord["torrentName"], torrentExtraInfo, torrentMagnet)

	# notify DownloadsInProgress file
	DownloadsInProgressFileInterface.notifyDownloadStarted(mediaInfoRecord["mediaGrabId"], mode)
