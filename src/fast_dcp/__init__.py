"""A smart CLI wrapper for docker compose with interactive selection support."""

import logging
from importlib.metadata import version

__version__ = version("fast-dcp")


logger = logging.getLogger("fast_dcp")
logger.addHandler(logging.NullHandler())
logger.propagate = False
