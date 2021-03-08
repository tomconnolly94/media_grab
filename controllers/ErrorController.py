#!/venv/bin/python

# external dependencies
import logging
import sys
import inspect

# internal dependencies
from interfaces import MailInterface


def reportError(message="", exception=None, sendEmail=False):

    frame = inspect.stack()[1][0]
    info = inspect.getframeinfo(frame)
    logPrefix = f"{info.filename}:{info.function}():{info.lineno}"
    message = f"{logPrefix} - {message}"


    # print message with stack trace if an exception is available
    if exception:
        logging.error(message, exc_info=True)
    else:
        logging.error(message)

    if sendEmail:
        logHandler = logging.getLoggerClass().root.handlers[0]
        moreLogsMessage = "\n\n More logs can be found in:"        

        # add info about which log file the error will be held in
        if hasattr(logHandler, "baseFilename"):
            logFileName = logHandler.baseFilename
            message += f"{moreLogsMessage} {logFileName}"
        else:
            message += f"{moreLogsMessage} console output"

        MailInterface.sendMail("Houston we have a problem", message)


if __name__== "__main__":
    exception = Exception("big exception!")
    try:
        raise exception
    except:
        reportError("big error!", exception=exception, sendEmail=True)
