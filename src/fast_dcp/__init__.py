__version__ = "0.1.0"

import logging

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())

from .main import main, dcpu_main, dcpe_main

__all__ = ["main", "dcpu_main", "dcpe_main"]
