import logging
import subprocess
import sys
from abc import ABC, abstractmethod
from argparse import Namespace
from pathlib import Path
from typing import Iterable

import yaml
from yaml.scanner import ScannerError

from . import cli_utils

logger = logging.getLogger(__name__)

CONFIG_PATH = Path.home() / ".config" / "fast-dcp"


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


class YamlHandler:
    def __init__(self, path: Path) -> None:
        """Initialize basic YAML setting, configuration path, and load YAML.

        Set AttrDict should convert from/to dict object in YAML, path to configuration file,
        and load configuration or create basic structure in configuration file.

        Args:
            path (Path): Path to the configuration file.
            keys (str): Top level keys to be initialized in configuration file.
        """
        yaml.add_representer(
            AttrDict,
            lambda dumper, data: dumper.represent_dict(data),
            Dumper=yaml.SafeDumper,
        )
        yaml.add_constructor(
            "tag:yaml.org,2002:map",
            lambda loader, node: AttrDict(loader.construct_mapping(node, deep=True)),
            Loader=yaml.SafeLoader,
        )
        self.path = path
        self._config = None

    @property
    def config(self) -> AttrDict:
        if self._config is None:
            logger.debug("WARNING: YamlHandler is not initialized.")
            self._config = AttrDict()
        return self._config

    def setup_config(self, *keys: str) -> None:
        """Load configuration or create basic structure in configuration file.

        Returns:
            AttrDict: Loaded YAML configuration.
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

        # Setup basic data structure
        for key in keys:
            if key not in config:
                config[key] = AttrDict()
        logger.debug(f"{config=}")

        self._config = config

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

    def _read_and_load(self) -> AttrDict:
        return yaml.safe_load(self.path.read_text(encoding="utf-8")) or AttrDict()

    def dump_and_write(self) -> None:
        self.path.write_text(
            yaml.dump(self._config, Dumper=yaml.SafeDumper), encoding="utf-8"
        )


class AbstractWsExecutor(ABC):
    _WORKSPACE_KEY = "workspaces"
    YAML_KEYS = (_WORKSPACE_KEY,)

    def __init__(self) -> None:
        self.handler = YamlHandler(CONFIG_PATH)

    def __call__(self, args: Namespace) -> int:
        self.handler.setup_config(*self.YAML_KEYS)
        code = self._switch(args)
        return code

    @abstractmethod
    def _switch(self, args: Namespace) -> int: ...

    def _select_workspace_or_create(self, candidates: Iterable[str]) -> str:
        candidates = sorted(candidates)
        if not candidates:
            return input("Please enter a new workspace name: ").strip()
        self._display_intro(candidates)
        choices: list[str] | None = cli_utils.interactive_select(
            candidates, multiple=False, allow_zero=True
        )
        if choices is None:
            return input("Please enter a new workspace name: ").strip()

        return choices[0]

    def _select_workspace_simply(self, candidates: Iterable[str]) -> str:
        candidates = sorted(candidates)
        self._display_intro(candidates)
        choices: list[str] = cli_utils.interactive_select(candidates, multiple=False)
        return choices[0]

    def _display_intro(self, candidates: Iterable[str]) -> None:
        msg = "☑ Found {} registered workspace{}."

        length = len(candidates)
        if length > 1:
            print(msg.format(length, "s"))
        else:
            print(msg.format(length, ""))


class WorkspaceRegistrar(AbstractWsExecutor):
    def _switch(self, args: Namespace) -> int:
        try:
            match args.ws_subcmd:
                case "register" | "reg":
                    return self.register_repo()
                case "delete" | "del":
                    return self.delete_repo()
                case "list" | "li":
                    return self.show_list()
                case _:  # pragma: no cover
                    # Unreachable branch
                    return 1  # pragma: no cover
        except KeyboardInterrupt:
            print("\nCancelled.")
            return 130
        except SystemExit:
            return 0

    def show_list(self) -> int:
        config = self.handler.config
        if not (workspaces := config[self._WORKSPACE_KEY]):
            print("☓ No workspaces registered yet.")
            return 1
        for key in workspaces:
            print(f"{key}")
            if not workspaces[key]:
                print("☓ No repos registered yet.")
            for value in workspaces[key]:
                print(f"  - {value}")
        return 0

    def register_repo(self) -> int:
        # User input
        new_repo = Path(input("Please enter a new directory path: ")).resolve()

        if not new_repo.is_dir():
            print(f"❌ The path doesn't exists: {str(new_repo)}", file=sys.stderr)
            return 1

        workspace_dict = self.handler.config[self._WORKSPACE_KEY]
        workspace_name = self._select_workspace_or_create(workspace_dict)
        appended = self.handler.append_value(
            self._WORKSPACE_KEY, workspace_name, str(new_repo)
        )
        if appended:
            self.handler.dump_and_write()
            print(f"\n☑ Registered new path to {workspace_name}: {str(new_repo)}")
        else:
            print(
                f"Oops, `{str(new_repo)}` is already in `{workspace_name}`.",
                file=sys.stderr,
            )
        print("💡 Hint: To get workspace lists, run `dcp ws list(li)`.")
        return 0

    def delete_repo(self) -> int:
        config = self.handler.config
        workspace_dict = config[self._WORKSPACE_KEY]
        if not workspace_dict:
            print("☓ No workspaces registered yet.", file=sys.stderr)
            return 1

        # User input
        target_workspace_name = self._select_workspace_simply(workspace_dict)
        target_workspace = workspace_dict[target_workspace_name]

        msg = "☑ Found {} director{}."
        if (length := len(target_workspace)) == 1:
            print(msg.format(length, "y"))
        elif length >= 2:
            print(msg.format(length, "ies"))

        for idx, choice in enumerate(target_workspace, start=1):
            print(f"{idx:>5}. {choice}")

        while True:
            try:
                # User input
                user_input = input("\nEnter your choices to delete (e.g., 1,3,4): ")

                # Sort in reverse order to avoid index error.
                choices = sorted(
                    map(
                        lambda i: int(i) - 1,
                        (i.strip() for i in user_input.split(",") if i.strip()),
                    ),
                    reverse=True,
                )
                if any((i < 0 for i in choices)):
                    raise IndexError
                if max(choices) >= length:
                    raise IndexError
            except (IndexError, ValueError):
                print("☓ Invalid selection. Please use a valid number.", file=sys.stderr)
            else:
                break

        for i in choices:
            name = target_workspace[i]
            del target_workspace[i]
            print(f"☑ Deleted: {name}")

        if not target_workspace:
            del workspace_dict[target_workspace_name]

        self.handler.dump_and_write()
        return 0


class WorkspaceExecutor(AbstractWsExecutor):
    def _switch(self, args: Namespace) -> int:
        cmd = []
        match args.ws_subcmd:
            case "up" | "u":
                cmd = ["docker", "compose", "up", "-d"]
            case "restart" | "re":
                cmd = ["docker", "compose", "restart"]
            case "stop" | "s":
                cmd = ["docker", "compose", "stop"]
            case "down":
                cmd = ["docker", "compose", "down"]
            case _:  # pragma: no cover
                # Unreachable branch
                return 1  # pragma: no cover

        try:
            codes = []
            for workdir in self.get_target_workspace():
                logger.debug(
                    f"\n---------workdir---------\n{workdir}\n----output docker cmd---- \n{cmd}"
                )
                code = self._execute_command(cmd, workdir)
                codes.append(code)
        except KeyboardInterrupt:
            print("\nCancelled.")
            return 130
        except FileNotFoundError:
            print("Docker is not found.", file=sys.stderr)
            return 1
        except Exception:
            print("An unexpected error occurred.", file=sys.stderr)
            return 1

        return next((c for c in codes if c != 0), 0)

    def get_target_workspace(self) -> list[str]:
        workspaces: dict = self.handler.config[self._WORKSPACE_KEY]
        workspace_name: str = self._select_workspace_simply(workspaces)
        return workspaces[workspace_name]

    def _execute_command(self, cmd: list[str], workdir: str) -> int:
        print(f"▷ Executing `{' '.join(cmd)}` in `{workdir}`.")
        result = subprocess.run(cmd, cwd=workdir)
        return result.returncode
