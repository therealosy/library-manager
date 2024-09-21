import logging
import sys
from typing import Literal
import re
import urllib
import urllib.parse

from utils.constants import REQUEST_METHODS
from utils.environment import APP_ENVIRONMENT


# Clear default uvicorn logger config
uvicorn_logger = logging.getLogger("uvicorn").handlers.clear()
uvicorn_logger = logging.getLogger("uvicorn.access").handlers.clear()


class CustomFormatter(logging.Formatter):

    def get_log_format(self, record: logging.LogRecord):

        green = "\033[92m"
        cyan = "\033[96m"
        purple = "\033[35m"
        yellow = "\033[93m"
        red = "\033[91m"
        reset = "\033[0m"
        bold = "\033[1m"

        level_name = "{:10}".format(record.levelname + ":")

        # caller_name = record.name
        message_body = urllib.parse.unquote(record.getMessage().replace("%", ""))

        if record.name == "uvicorn.access":
            message_body = re.sub(
                r"\" ([5]\d{2})", '" ' + red + r"\1" + reset, message_body
            )
            message_body = re.sub(
                r"\" ([4]\d{2})", '" ' + yellow + r"\1" + reset, message_body
            )
            message_body = re.sub(
                r"\" ([2]\d{2})", '" ' + green + r"\1" + reset, message_body
            )
            for request_method in REQUEST_METHODS:
                message_body = message_body.replace(
                    f'"{request_method}', f'"{bold}{purple}{request_method}{reset}'
                )

        message_text = (
            "[%(name)s : %(lineno)d] [%(funcName)s] [%(asctime)s] " + message_body
        )
        date_format = "%Y-%m-%d %T"

        format = {
            logging.DEBUG: cyan + level_name + reset + message_text,
            logging.INFO: green + level_name + reset + message_text,
            logging.WARNING: yellow + level_name + reset + message_text,
            logging.ERROR: red + level_name + reset + message_text,
            logging.CRITICAL: bold
            + red
            + level_name
            + reset
            + bold
            + message_text
            + reset,
        }
        return format[record.levelno], date_format

    def format(self, record):
        msg_format, date_format = self.get_log_format(record)
        formatter = logging.Formatter(msg_format, date_format)
        return formatter.format(record)


LOG_LEVELS = {
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "WARNING": logging.WARNING,
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
}


DEFAULT_LOG_LEVEL = (
    logging.INFO if APP_ENVIRONMENT.upper() in ["PRODUCTION", "PROD"] else logging.DEBUG
)


def getlogger(
    name: str = "root",
    log_level: Literal["INFO", "DEBUG", "WARNING", "CRITICAL", "ERROR"] | None = None,
) -> logging.Logger:

    logging_level = LOG_LEVELS.get(log_level, DEFAULT_LOG_LEVEL)

    logging_handler = logging.StreamHandler(sys.stdout)
    logging_handler.setFormatter(CustomFormatter())
    logger = logging.getLogger(name)
    logger.addHandler(logging_handler)
    logger.setLevel(logging_level)

    return logger
