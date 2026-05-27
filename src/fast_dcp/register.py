import logging
import sys
from pathlib import Path

import yaml
from yaml.scanner import ScannerError

logger = logging.getLogger(__name__)

CONFIG_PATH = Path.home() / ".config" / "fast-dcp"


class AttrDict(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
    def __init__(self, path: Path):
        self.path = path
        self._config = AttrDict()
        yaml.add_representer(
            AttrDict,
            lambda dumper, data: dumper.represent_dict(data),
            Dumper=yaml.SafeDumper,
        )
        yaml.add_constructor(
            "tag:yaml.org,2002:map",
            lambda loader, node: AttrDict(**loader.construct_mapping(node, deep=True)),
            Loader=yaml.SafeLoader,
        )

    @property
    def config(self):
        return self._config

    def setup_config(self, *keys) -> None:
        try:
            if self.path.exists():
                self._config = self._read_and_load()
            else:
                # Make parent directories.
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self.path.touch()
        # For developpers
        except ScannerError:
            print(f"❌ Couldn't load yaml: {self.path}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"❌ Couldn't find directory: {self.path.parent}", file=sys.stderr)
            sys.exit(1)

        # Setup basic data structure
        for key in keys:
            if key not in self._config:
                self._config[key] = AttrDict()
        logger.debug(f"{self._config=}")

    def append_subcategory(self, category: str, **subcategory: str) -> int:
        """Append values to the config under the given category.

        Assumed Structure:
        category_1:
          subcategory_1:
            - value_1
            - value_2
          subcategory_2:
            - value_3

        """
        if not self._config.get(category):
            self._config[category] = AttrDict()

        target = self._config[category]
        cnt = 0
        for key, value in subcategory.items():
            if key not in target:
                target[key] = []
            if value in target[key]:
                print(f"Oops, `{value}` is already in `{key}`.")
                continue
            target[key].append(value)
            target[key].sort()
            cnt += 1

        return cnt

    def _read_and_load(self) -> dict:
        return yaml.safe_load(self.path.read_text(encoding="utf-8")) or AttrDict()

    def dump_and_write(self) -> None:
        self.path.write_text(
            yaml.dump(self._config, Dumper=yaml.SafeDumper), encoding="utf-8"
        )


class Registrar:
    _WORKSPACE_KEY = "workspaces"
    YAML_KEYS = (_WORKSPACE_KEY,)

    def __init__(self) -> None:
        self.handler = YamlHandler(CONFIG_PATH)

    def __call__(self, args) -> None:
        self.handler.setup_config(*self.YAML_KEYS)

        try:
            if args.register:
                return self.register_repo()
            if args.delete:
                return self.delete_repo()
            if args.list:
                return self.show_list()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(130)

    def show_list(self) -> None:
        config = self.handler.config
        for key in config[self._WORKSPACE_KEY]:
            print(f"========={key}=========")
            for value in config[self._WORKSPACE_KEY][key]:
                print(f"- {value}")

    def register_repo(self) -> None:
        # User iput
        new_repo = Path(input("Please enter a new directory path: ")).resolve()

        if not new_repo.is_dir():
            print(f"❌ The path doesn't exists: {str(new_repo)}")
            return

        # User input
        workspace_name = self._select_workspace_name()

        count = self.handler.append_subcategory(
            self._WORKSPACE_KEY, **{workspace_name: str(new_repo)}
        )
        if count == 0:
            print(f"The path already exists: {str(new_repo)}")
        else:
            self.handler.dump_and_write()
            print(f"☑ Registered new path to {workspace_name}: {str(new_repo)}")
        print("💡 Hint: To check workspace list, execute `dcp --list`.")

    def delete_repo(self) -> None:
        prompt = "☑ Found {} registered workspace{}."

        config = self.handler.config
        workspaces = config[self._WORKSPACE_KEY]

        if not workspaces:
            print("❌ No workspaces found.")
            return
        
        # User input
        target_workspace_name = self._select_workspace_name()
        target_workspace = workspaces[target_workspace_name]

        if (count := len(target_workspace)) == 1:
            print(prompt.format(count, ""))
        elif count >= 2:
            print(prompt.format(count, "s"))

        for idx, choice in enumerate(target_workspace, start=1):
            print(f"{idx:>5}. {choice}")

        # TODO: add error handling
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
        for i in choices:
            name = target_workspace[i]
            del target_workspace[i]
            print(f"☑ Deleted: {name}")

        if not target_workspace:
            del workspaces[target_workspace_name]

        self.handler.dump_and_write()

    def _select_workspace_name(self) -> str:
        workspaces = self.handler.config[self._WORKSPACE_KEY]

        if workspaces:
            prompt = "☑ Found {} registered workspace{}."

            if (count := len(workspaces)) == 1:
                print(prompt.format(count, ""))
            elif count >= 2:
                print(prompt.format(count, "s"))

            for idx, choice in enumerate(workspaces, start=1):
                print(f"{idx:>5}. {choice}")

            # TODO: add error handling
            user_input_workspace = input(
                "\nEnter your choice or input new workspace name: "
            )
            try:
                target_workspace_number = int(user_input_workspace.strip()) - 1
                target_workspace_name = list(workspaces.keys())[target_workspace_number]
            except ValueError:
                target_workspace_name = user_input_workspace

        else:
            target_workspace_name = input("Please enter a new workspace name: ").strip()

        return target_workspace_name
