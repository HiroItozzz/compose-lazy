import logging
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from argparse import Namespace
from pathlib import Path
from typing import Iterable

from . import utils
from .config import CONFIG_PATH
from .utils import YamlHandler, call_safely

logger = logging.getLogger(__name__)


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
        candidates = list(candidates)
        if not candidates:
            return input("Please enter a new workspace name: ").strip()

        self._display_intro(candidates)
        choices: list[str] | None = utils.interactive_select(
            candidates, multiple=False, allow_zero=True
        )

        if choices is None:
            return input("Please enter a new workspace name: ").strip()

        return choices[0]

    def _select_workspace_simply(self, candidates: Iterable[str]) -> str | None:
        candidates = list(candidates)
        if not candidates:
            print("☓ No workspaces registered yet.", file=sys.stderr)
            return None
        elif len(candidates) == 1:
            choices = candidates
        else:
            self._display_intro(candidates)
            choices: list[str] = utils.interactive_select(candidates, multiple=False)
        return choices[0]

    def _display_intro(self, candidates: list[str]) -> None:
        msg = "☑ Found {} registered workspace{}!"
        length = len(candidates)

        print()
        if length > 1:
            print(msg.format(length, "s"))
        else:
            print(msg.format(length, ""))


class WorkspaceRegistrar(AbstractWsExecutor):
    @call_safely
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
        except (TypeError, KeyError, AttributeError):
            logger.debug("Workspace config has unexpected structure.", exc_info=True)
            print(
                "❌️ Workspace config is invalid or outdated.\n"
                "💡 Delete ~/.config/compose-lazy/config.yml and re-register your workspaces.",
                file=sys.stderr,
            )
            return 1

    def show_list(self) -> int:
        config = self.handler.config
        if not (workspaces := config[self._WORKSPACE_KEY]):
            print("☓ No workspaces registered yet.")
            return 1
        width, _ = shutil.get_terminal_size()
        for ws_key in workspaces:
            print(f"───── {ws_key} ".ljust(min(width, 100), "─"))
            repos_dict: dict[str, list[str]] = workspaces[ws_key]
            if not repos_dict:
                print("☓ No repos registered yet.")
            for idx, repo_name in enumerate(repos_dict, start=1):
                print(f"{'📁 PATH[' + str(idx) + ']':>9}: {repo_name}")
                print(f"{'FILES':>10}: {', '.join(repos_dict[repo_name])}")
        return 0

    def register_repo(self) -> int:
        # User input
        new_repo = (
            Path(input("Please enter a new directory path: ")).expanduser().resolve()
        )

        if not new_repo.is_dir():
            print(f"❌ The path doesn't exists: {str(new_repo)}", file=sys.stderr)
            return 1

        selected_yamls = utils.get_file_choices(new_repo)

        workspace_dict = self.handler.config[self._WORKSPACE_KEY]
        workspace_name = self._select_workspace_or_create(workspace_dict)
        for yaml_name in selected_yamls:
            appended = self.handler.append_value(
                self._WORKSPACE_KEY, workspace_name, str(new_repo), yaml_name
            )
            if appended:
                self.handler.dump_and_write()
                print(
                    f"☑ Registered new path to {workspace_name}: {str(new_repo)} ({yaml_name})"
                )
            else:
                print(
                    f"Oops, `{str(new_repo)} ({yaml_name})` is already in `{workspace_name}`.",
                    file=sys.stderr,
                )
        print("💡 Hint: To get workspace lists, run `dcp ws list(li)`.")
        return 0

    def delete_repo(self) -> int:
        config = self.handler.config
        workspace_dict = config[self._WORKSPACE_KEY]

        # User input
        target_workspace_name = self._select_workspace_simply(workspace_dict)
        if target_workspace_name is None:
            return 1
        target_workspace = workspace_dict[target_workspace_name]

        print()
        msg = "☑ Found {} repositor{}!"
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

        keys = list(target_workspace)
        for i in choices:
            name = keys[i]
            del target_workspace[name]
            print(f"☑ Deleted: {name}")

        if not target_workspace:
            del workspace_dict[target_workspace_name]

        self.handler.dump_and_write()
        return 0


class WorkspaceProcessor(AbstractWsExecutor):
    BASE_COMMAND = ["docker", "compose"]

    @call_safely
    def _switch(self, args: Namespace) -> int:

        if (workspace := self.get_target_workspace()) is None:
            return 1
        match args.ws_subcmd:
            case "up" | "u":
                subcommand = ["up", "-d"]
            case "build" | "b":
                subcommand = ["build"]
            case "restart" | "re":
                subcommand = ["restart"]
            case "stop" | "s":
                subcommand = ["stop"]
            case "down":
                subcommand = ["down"]
            case _:  # pragma: no cover
                # Unreachable branch
                return 1  # pragma: no cover

        return self._iterate_execution(subcommand, workspace)

    def _iterate_execution(
        self, subcommand: list[str], workspace: dict[str, list[str]]
    ) -> int:
        try:
            codes = []
            for workdir, yaml_names in workspace.items():
                if not Path(workdir).is_dir():
                    print(f"❌️ Workspace directory not found: {workdir}", file=sys.stderr)
                    codes.append(1)
                    continue

                missing = [y for y in yaml_names if not (Path(workdir) / y).exists()]
                if missing:
                    # fmt: off
                    for y in missing:
                        print(f"❌️ Compose file not found: {Path(workdir) / y}", file=sys.stderr)
                    print(f"⚠️  Skipping {Path(workdir).name} — re-register to fix.", file=sys.stderr)
                    codes.append(1)
                    continue
                    # fmt: on

                optional_args = utils.format_as_flag_args(yaml_names, "-f")
                cmd = self.BASE_COMMAND + optional_args + subcommand

                code = self._execute_command(cmd, workdir)
                codes.append(code)

        except (TypeError, KeyError, AttributeError):
            logger.debug("Workspace config has unexpected structure.", exc_info=True)
            print(
                "❌️ Workspace config is invalid or outdated.\n"
                "💡 Delete ~/.config/compose-lazy/config.yml and re-register your workspaces.",
                file=sys.stderr,
            )
            return 1
        except FileNotFoundError:
            print("Docker is not found.", file=sys.stderr)
            return 1
        return next((c for c in codes if c != 0), 0)

    def _execute_command(self, cmd: list[str], workdir: str) -> int:
        repo_name = Path(workdir).name
        width, _ = shutil.get_terminal_size()
        logger.debug(
            f"\n---------workdir---------\n{workdir}\n----output docker cmd---- \n{cmd}"
        )
        print(
            f"───── 📂 {repo_name} ".ljust(min(width, 100) - 1, "─")
        )  # Subtract the count of full width chars
        print(f"▷ Executing `{' '.join(cmd)}` in {repo_name.upper()}.")
        result = subprocess.run(cmd, cwd=workdir)
        return result.returncode

    def get_target_workspace(self) -> dict[str, list[str]] | None:
        """Let the user select workspace and returns all paths in it.

        Returns:
            list[str]: All paths in a workspace user selected.
        """
        workspaces: dict = self.handler.config[self._WORKSPACE_KEY]
        workspace_name = self._select_workspace_simply(workspaces)
        if workspace_name is None:
            return None
        return workspaces[workspace_name]
