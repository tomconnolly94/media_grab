#!/venv/bin/python

# external dependencies
from dotenv import load_dotenv
import os, sys
from os.path import join, dirname
import logging
import getopt

# internal dependencies
from interfaces import TPBInterface, MediaIndexFileInterface, QBittorrentInterface
from controllers import LoggingController, LogicController
from data_types.ProgramModeMap import PROGRAM_MODE_MAP 

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#intitialise logging module
LoggingController.initLogging()


def interpretArguments(argv):
	mode = ''
	permitted_modes = "|".join([key for key in PROGRAM_MODE_MAP.keys() if isinstance(key, str)])
	usage = f"""Usage:
	python {os.path.basename(__file__)} -m <mode> [{permitted_modes}]"""

	try:
		opts = getopt.getopt(argv,"hm:",["mode="])[0]
	except getopt.GetoptError:
		print(usage)
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(usage)
			sys.exit(3)
		elif opt in ("-m", "--mode"):
			#validate mode argument
			if arg in PROGRAM_MODE_MAP.keys():
				mode = PROGRAM_MODE_MAP[arg]
			else:
				print(usage)
				sys.exit(4)

	if not mode:
		logging.error("Mode was not provided")
		print(usage)
		sys.exit(5)
			
	print(f"Mode is {mode}")

	return mode


def main(argv):

	mode = interpretArguments(argv)

	logging.info("Media grab app started.")

	# catch all exceptions so they are always reported
	try:
		QBittorrentInterface.init()
		mediaInfoRecords = MediaIndexFileInterface.loadMediaFile() # information about the wanted media
		LogicController.runProgramLogic(mediaInfoRecords, mode)
	
	except Exception:
		logging.error("Exception occurred", exc_info=True)


if __name__== "__main__":
	main(sys.argv[1:])
