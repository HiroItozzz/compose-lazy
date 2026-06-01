import logging
import os

try:
    from dotenv import load_dotenv

    load_dotenv()

except ImportError:
    pass

DEBUG = os.environ.get("COMPOSE_LAZY_DEBUG", "False").lower() in ["true", "t"]

LOG_LEVEL = "DEBUG"


def setup_logger(name: str) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        return

    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    ch_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(filename)s %(message)s", "%H:%M:%S"
    )
    ch.setFormatter(ch_formatter)

    if DEBUG:
        logger.addHandler(ch)
