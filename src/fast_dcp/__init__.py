"""A CLI tool that provides shorthand aliases for common docker compose commands."""

__version__ = "0.0.2"

from fast_dcp.main import dcpe_main, dcpu_main, main

__all__ = ["main", "dcpu_main", "dcpe_main"]

import logging

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())
