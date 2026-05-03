import logging

DEBUG = False

LOG_LEVEL = "DEBUG" if DEBUG else "INFO"


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
    ch_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(filename)s %(message)s", "%H:%M:%S"
    )
    ch.setFormatter(ch_formatter)

    logger.addHandler(ch)
    return logger
