#!/venv/bin/python

# external dependencies
from dotenv import load_dotenv
import os, sys
from os.path import join, dirname
import logging
import getopt

# internal dependencies
from controllers import LoggingController, LogicController, ErrorController
from interfaces import MailInterface
from dataTypes.ProgramModeMap import PROGRAM_MODE_MAP
from dataTypes.ProgramMode import PROGRAM_MODE

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
		# mode defaults to tv-episodes if no mode is provided
		mode = PROGRAM_MODE.TV_EPISODES
			
	logging.info(f"Mode is {mode}")

	return mode


def assertVitalEnvValuesExist():
	essentialEnvs = set([
		"QBT_URL", # necessary to submit torrents
		"MEDIA_FILE", # necessary to query torrents
		"DOWNLOADS_IN_PROGRESS_FILE", # necessary to track downloading torrents
		"ENVIRONMENT", # necessary to determine the mode of the program
		"DUMP_COMPLETE_DIR", # necessary to determine where to deposit (and find) downloaded items
		"THE_MOVIE_DATABASE_API_KEY" # necessary to get information about the requested media
	])

	if essentialEnvs.issubset(os.environ):
		return True
	exceptionText = "Some of the required env entries are not present, please review your .env file. Program exited."
	exception = Exception(exceptionText)
	ErrorController.reportError(exceptionText, exception=exception, sendEmail=True)
	raise exception
	

def main(argv):

	mode = interpretArguments(argv)
	assertVitalEnvValuesExist()
	environment = os.getenv("ENVIRONMENT")
	logging.info(f"Media grab app started. Environment={environment}")

	# catch all exceptions so they are always reported
	try:
		LogicController.runProgramLogic(mode)
		logging.info("Media grab app exiting.")
	
	except Exception as exception:
		ErrorController.reportError("Exception occurred", exception=exception, sendEmail=True)
	
	finally:
		# send mail items that have been collated
		MailInterface.getInstance().sendAllCollatedMailItems()


if __name__== "__main__":
	main(sys.argv[1:])
