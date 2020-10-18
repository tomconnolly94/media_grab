#!/venv/bin/python

# external dependencies 
import os
import logging
import time

def initLogging():
    
    logFormat = '%(asctime)s - %(levelname)s - %(message)s'
    logDateFormat = '%d-%b-%y %H:%M:%S'

    if os.getenv("ENVIRONMENT") == "production":
        logFilename = f"logs/media-grab_{time.strftime('%d-%m-%Y_%H-%M')}.log"
        logging.basicConfig(filename=logFilename, filemode='w', format=logFormat, datefmt=logDateFormat, level=logging.INFO)
    else:
        logging.basicConfig(format=logFormat, datefmt=logDateFormat, level=logging.INFO)

    logging.debug('Logging initialised.')
    return logging
