#!/venv/bin/python

# external dependencies
from dotenv import load_dotenv
import os
from os.path import join, dirname
import logging

# internal dependencies
from interfaces import TPBInterface, MediaFileInterface
from controllers import LoggingController, LogicController

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#intitialise logging module
LoggingController.initLogging()


def main():

	logging.info("Media grab app started.")

	# catch all exceptions so they are always reported
	try:
		TPBInterface.init()
		mediaInfoRecords = MediaFileInterface.loadMediaFile() # information about the wanted media
		LogicController.runProgramLogic(mediaInfoRecords)
	
	except Exception:
		logging.error("Exception occurred", exc_info=True)


if __name__== "__main__":
	main()
