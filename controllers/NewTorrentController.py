#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import MediaIndexFileInterface, MailInterface, DownloadsInProgressFileInterface


def onSuccessfulTorrentAdd(queryRecord, updateableField, torrentMagnet, mode):

	MediaIndexFileInterface.writeMediaFile(queryRecord, updateableField)

	# send email notification
	torrentExtraInfo = f"{updateableField} {queryRecord['typeSpecificData'][updateableField]}"
	MailInterface.sendNewTorrentMail(queryRecord["torrentName"], torrentExtraInfo, torrentMagnet)

	# notify DownloadsInProgress file
	DownloadsInProgressFileInterface.notifyDownloadStarted(queryRecord["torrentName"], mode)
