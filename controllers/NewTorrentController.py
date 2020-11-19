#!/venv/bin/python

# external dependencies
import logging

# internal dependencies
from interfaces import MediaIndexFileInterface, MailInterface


def onSuccessfulTorrentAdd(queryRecord, updateableField, torrentMagnet):

	MediaIndexFileInterface.writeMediaFile(queryRecord, updateableField)

	# send email notification
	torrentExtraInfo = f"{updateableField} {queryRecord['typeSpecificData'][updateableField]}"
	MailInterface.sendNewTorrentMail(queryRecord["name"], torrentExtraInfo, torrentMagnet)
