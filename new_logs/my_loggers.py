import logging

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "[%(levelname)s]: %(filename)s:%(lineno)d: %(message)s"


# basic logger
LOG_FILE = "output/log.log"
logger = logging.getLogger("logger")

logger.setLevel(LOG_LEVEL)
file_handler = logging.FileHandler(LOG_FILE, mode='w')
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(file_handler)