#!/venv/bin/python

# external dependencies
import logging

#internal dependencies
from interfaces import MediaFileInterface, MailInterface


def onSuccessfulTorrentAdd(queryRecord, updateableField, torrentMagnet):

	MediaFileInterface.writeMediaFile(queryRecord, updateableField)

	# TODO: send email notification
	addMessage = f'ADDED TORRENT: {queryRecord["name"]} {updateableField} {queryRecord["typeSpecificData"][updateableField]} \n\n Magnet:{torrentMagnet}'
	MailInterface.sendMail(addMessage)
	
	logging.info(addMessage)

