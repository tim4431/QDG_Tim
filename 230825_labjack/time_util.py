import datetime
import logging
import os

TIME_STAMP_FORMAT = "%Y-%m-%d %H:%M:%S"  # year-month-day hour:minute:second.microsecond
DATE_FORMAT = "%Y-%m-%d"


def get_time_date():
    curtime = datetime.datetime.now()
    curTimeStr = curtime.strftime(TIME_STAMP_FORMAT)
    curDateStr = curtime.strftime(DATE_FORMAT)
    return curtime, curTimeStr, curDateStr


def setup_logging(log_fileName):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s"
    )
    cwd = os.getcwd()
    file_handler = logging.FileHandler(os.path.join(cwd, log_fileName + ".log"))
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
    file_handler.setFormatter(file_formatter)
    #
    logger = logging.getLogger()
    # Remove existing file handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    # Add the file handler to the root logger
    logger.addHandler(file_handler)


def setup_csv(fileDateStr):
    # if the file exists, do nothing
    if os.path.exists(fileDateStr + ".csv"):
        return
    write_csv(fileDateStr, "Timestamp, Temperature (K), Temperature (C)\n")


def write_csv(fileDateStr, writeline):
    f = open_csv(fileDateStr)
    f.write(writeline)
    f.close()


def open_csv(fileDateStr):
    # Get the current working directory
    cwd = os.getcwd()

    # Build a file-name and the file path.
    fileName = "%s.csv" % (fileDateStr)
    filePath = os.path.join(cwd, fileName)

    # Open the file and write a header line
    f = open(filePath, "a")

    return f
