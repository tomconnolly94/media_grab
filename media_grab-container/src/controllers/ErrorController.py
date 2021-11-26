#!/venv/bin/python

# external dependencies
import logging
import sys
import inspect

# internal dependencies
from src.interfaces import MailInterface
from src.dataTypes.MailItem import MailItemType


def reportError(message="", exception=None, sendEmail=False):
    """
    reportError reports an error properly, offering options via params to detail a specific error message, capture the exception, and perhaps send an email
    :param message: optional text to be included in the error report
    :param exception: optional exception object, the stack trace of which will be included in the error report
    :param sendEmail: optional boolean to decide whether the error should be reported in an email
    :testedWith: TestErrorController:test_reportError
    :return: None
    """
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

        mailInterface = MailInterface.getInstance()
        mailInterface.pushMail(message, MailItemType.ERROR)
