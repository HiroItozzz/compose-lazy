"""A CLI tool that provides shorthand aliases for common docker compose commands."""

from importlib.metadata import version

__version__ = version(__package__)

from fast_dcp.main import main, dcpu_main, dcpe_main

__all__ = ["main", "dcpu_main", "dcpe_main"]

import logging

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())
