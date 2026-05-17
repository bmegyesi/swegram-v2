import logging
from logging import Logger
from pathlib import Path


def get_logger(filename: str) -> Logger:
    # Create logging formatter
    log_formatter = logging.Formatter(fmt="%(name)-25s :: %(levelname)-8s :: %(message)s")

    # Create logger
    logger = logging.getLogger('.'.join(Path(filename).with_suffix('').parts))
    logger.setLevel(logging.DEBUG)


    # Create console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(log_formatter)

    # Add console handler to logger
    logger.addHandler(consoleHandler)
    return logger
