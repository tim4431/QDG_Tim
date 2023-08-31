import logging
import sys


# Redirect stdout to the logging module(not used)
class StdoutLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.original_stdout = sys.stdout

    def write(self, message):
        if message.strip() != "":
            self.logger.log(self.log_level, message.strip())

    def flush(self):
        pass


def setup_logger(log_fileName):
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] - %(message)s")

    # Create a file handler
    file_handler = logging.FileHandler(log_fileName + ".log")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("[%(levelname)s] - %(message)s")
    file_handler.setFormatter(file_formatter)
    #
    logger = logging.getLogger()
    # Remove existing file handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    # Add the file handler to the root logger
    logger.addHandler(file_handler)


def create_logger(log_fileName):
    logger = logging.getLogger(log_fileName)
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] - %(message)s")
    # Create a file handler
    file_handler = logging.FileHandler(log_fileName)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("[%(levelname)s] - %(message)s")
    file_handler.setFormatter(file_formatter)
    # add file handler to logger
    logger.addHandler(file_handler)
    return logger


def close_logger(logger):
    if logger is None and (logger.handlers is not None):
        return
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    setup_logger("logging_test")
    logging.info("info")
    logging.debug("debug")
    logging.error("error")
    logging.warning("warning")
    try:
        raise Exception("e")
    except Exception as e:
        print("ee")
    print("fk")
    setup_logger("logging_test")
    logging.warning("warning")
