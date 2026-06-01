import logging
import sys
from pathlib import Path
from typing import Any, Self

import yaml
from yaml.scanner import ScannerError

logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return self.keys()


class YamlReader:
    def __init__(self, path: Path) -> None:
        """Initialize basic YAML setting, configuration path.

        Set AttrDict should convert from dict object in YAML, path to configuration file.

        Args:
            path (Path): Path to the configuration file.
        """
        yaml.add_constructor(
            "tag:yaml.org,2002:map",
            lambda loader, node: AttrDict(loader.construct_mapping(node, deep=True)),
            Loader=yaml.SafeLoader,
        )
        self.path = path
        self._config = None

    @property
    def config(self) -> dict:
        if self._config is None:
            logger.debug("WARNING: YamlHandler is not initialized.")
            self._config = AttrDict()
        return self._config

    def setup_config(self) -> Self:
        """Load configuration or create basic structure in config variable.

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
                config = AttrDict()
        # For developers
        except ScannerError:
            print(f"❌ Couldn't load yaml: {self.path}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"❌ Couldn't find directory: {self.path.parent}", file=sys.stderr)
            sys.exit(1)

        self._config = config
        return self

    def get_values(self, *keys: str) -> Any:
        """Get values under nested dict of config"""
        current = self.config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current

    def _read_and_load(self) -> dict:
        return yaml.safe_load(self.path.read_text(encoding="utf-8")) or AttrDict()


class YamlHandler(YamlReader):
    def __init__(self, *args, **kwargs) -> None:
        """Initialize basic YAML setting, configuration path, and load YAML.

        Set AttrDict should convert from/to dict object in YAML, path to configuration file.

        Args:
            path (Path): Path to the configuration file.
        Returns:
            Self: The instance itself.
        """
        yaml.add_representer(
            AttrDict,
            lambda dumper, data: dumper.represent_dict(data),
            Dumper=yaml.SafeDumper,
        )
        super().__init__(*args, **kwargs)

    def setup_config(self, *keys: str) -> Self:
        """Load configuration or create basic structure in config variable.

        Args:
            keys (str): Top level keys to be initialized in configuration file.
        Returns:
            AttrDict: Loaded YAML configuration.
        """
        super().setup_config()
        config = self.config

        # Setup basic data structure
        for key in keys:
            if key not in config:
                config[key] = AttrDict()
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
            if not current.get(key):
                current[key] = AttrDict()
            current = current[key]
        last_key = keys[-1]
        if not current.get(last_key):
            current[last_key] = []

        if value in current[last_key]:
            return False
        current[last_key].append(value)
        current[last_key].sort()
        return True

    def dump_and_write(self) -> None:
        self.path.write_text(
            yaml.dump(self._config, Dumper=yaml.SafeDumper), encoding="utf-8"
        )
