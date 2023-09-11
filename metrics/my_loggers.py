import logging


def configure_logger(log_file="output/my_log.log", log_level=logging.DEBUG):
    logger = logging.getLogger("my_logger")
    logger.setLevel(log_level)

    # Create a file handler and set the log level
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setLevel(log_level)

    # Create a log message formatter
    log_format = "[%(levelname)s]: %(filename)s:%(lineno)d: %(message)s"
    formatter = logging.Formatter(log_format)

    # Set the formatter for the file handler
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger
