import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path


class StreamToLogger:
    def __init__(self, logger, level, original_stream):
        self.logger = logger
        self.level = level
        self.original_stream = original_stream

    def write(self, message):
        message = message.strip()

        if message:
            self.logger.log(self.level, message)

            # Keep terminal output
            self.original_stream.write(message + "\n")

    def flush(self):
        self.original_stream.flush()


def get_logger(filename: str) -> Logger:

    CONSOLE_LOG_FILE = os.getenv("CONSOLE_LOG_FILE", os.path.join(os.getcwd(), "log/console.log"))
    os.makedirs(os.path.dirname(CONSOLE_LOG_FILE), exist_ok=True)

    # Create logger
    logger = logging.getLogger('.'.join(Path(filename).with_suffix('').parts))

    # prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create logging formatter
    log_formatter = logging.Formatter(fmt="%(asctime)s :: %(levelname)-8s :: %(name)-15s :: %(message)s")

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(log_formatter)

    # Console log file
    console_file_handler = RotatingFileHandler(
        CONSOLE_LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    console_file_handler.setLevel(logging.DEBUG)
    console_file_handler.setFormatter(log_formatter)

    handlers = [
        console_handler,
        console_file_handler,
    ]

    # Add handlers to app logger
    for handler in handlers:
        logger.addHandler(handler)
    logger.propagate = False

    # ==========================================
    # Configure uvicorn loggers
    # ==========================================
    uvicorn_loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
    ]

    for uvicorn_logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)

        # Clear existing handlers
        uvicorn_logger.handlers.clear()

        # Add same handlers
        for handler in handlers:
            uvicorn_logger.addHandler(handler)

        uvicorn_logger.setLevel(logging.DEBUG)
        uvicorn_logger.propagate = False

    return logger
