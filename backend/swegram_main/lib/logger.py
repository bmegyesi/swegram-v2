import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(filename: str) -> Logger:

    LOG_FILE = os.getenv("LOG_FILE", "/app/logs/app.log")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    # Create logging formatter
    log_formatter = logging.Formatter(fmt="%(name)-25s :: %(levelname)-8s :: %(message)s")

    # Create logger
    logger = logging.getLogger('.'.join(Path(filename).with_suffix('').parts))
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)

    # Create console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(log_formatter)

    # Add console handler to logger
    logger.addHandler(consoleHandler)
    return logger
