"""A smart CLI wrapper for docker compose with interactive selection support."""

import logging
from importlib.metadata import version

__version__ = version("compose-lazy")

logger = logging.getLogger("compose_lazy")
logger.addHandler(logging.NullHandler())
logger.propagate = False
