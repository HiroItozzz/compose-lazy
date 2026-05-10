"""A CLI tool that provides shorthand aliases for common docker compose commands."""

import logging
from importlib.metadata import version

__version__ = version("fast-dcp")


logger = logging.getLogger("fast-dcp")
logger.addHandler(logging.NullHandler())
