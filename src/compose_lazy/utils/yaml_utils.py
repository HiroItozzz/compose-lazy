import logging
import sys
from pathlib import Path
from typing import Any, Self

import yaml
from yaml.scanner import ScannerError

from .cli_utils import handle_config

logger = logging.getLogger(__name__)


class YamlHandler:
    def __init__(self, path: Path) -> None:
        """Initialize basic YAML setting, configuration path, and load YAML.

        Args:
            path (Path): Path to the configuration file.
        """
        self.path = path
        self._config = None

    @property
    def config(self) -> dict:
        if self._config is None:
            logger.debug("WARNING: YamlHandler is not initialized.")
            self._config = {}
        return self._config

    @handle_config
    def setup_config(self, *keys) -> Self:
        """Load configuration and create basic structure in config variable.

        Args:
            keys (str): Top level keys to be initialized in configuration file.
        Returns:
            Self: The instance itself.
        """
        try:
            if self.path.exists():
                config = self._read_and_load()
            else:
                # Make parent directories.
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self.path.touch()
                config = {}
        # For developers
        except ScannerError:
            print(f"❌ Couldn't load yaml: {self.path}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"❌ Couldn't find directory: {self.path.parent}", file=sys.stderr)
            sys.exit(1)

        # Setup basic data structure
        for key in keys:
            if key not in config:
                config[key] = {}
        logger.debug(f"{config=}")
        self._config = config

        return self

    def append_value(self, *args: str) -> bool:
        """Append value to the config.

        For example, if `append_elements("cat1", "cat2", "cat3", "value")` executed,
        configuration dict or YAML got structure like bellow:
        ```
        cat1:
          cat2:
            cat3:
              - value
        ```
        """
        *keys, value = args
        current = self.config
        for key in keys[:-1]:
            if current.get(key) is None:
                current[key] = {}
            current = current[key]
        last_key = keys[-1]
        if not current.get(last_key):
            current[last_key] = []

        if value in current[last_key]:
            return False
        current[last_key].append(value)
        current[last_key].sort()
        return True

    def get_values(self, *keys: str) -> Any:
        """Get values under nested dict of config"""
        current = self.config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current

    def _read_and_load(self) -> dict:
        return yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}

    def dump_and_write(self) -> None:
        self.path.write_text(yaml.safe_dump(self._config), encoding="utf-8")
