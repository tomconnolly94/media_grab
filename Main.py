#!/venv/bin/python

# external dependencies
from dotenv import load_dotenv
import os, sys
from os.path import join, dirname
import logging
import getopt

# internal dependencies
from interfaces import TPBInterface, MediaFileInterface
from controllers import LoggingController, LogicController
from data_types.ProgramMode import ProgramMode 

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#intitialise logging module
LoggingController.initLogging()


def interpretArguments(argv):
	mode = ''
	usage = f"""Usage:
					{os.path.basename(__file__)} -m <mode>"""

	try:
		opts, args = getopt.getopt(argv,"hm:",["mode="])
	except getopt.GetoptError:
		print(usage)
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(usage)
			sys.exit()
		elif opt in ("-m", "--mode"):
			mode = arg
			
	print(f"Mode is {mode}")

	return mode


def main(argv):

	logging.info("Media grab app started.")

	mode = interpretArguments(argv)

	# catch all exceptions so they are always reported
	try:
		TPBInterface.init()
		mediaInfoRecords = MediaFileInterface.loadMediaFile() # information about the wanted media
		LogicController.runProgramLogic(mediaInfoRecords, mode)
	
	except Exception:
		logging.error("Exception occurred", exc_info=True)


if __name__== "__main__":
	main(sys.argv[1:])
