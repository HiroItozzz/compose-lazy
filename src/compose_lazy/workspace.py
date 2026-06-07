import logging
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from argparse import Namespace
from pathlib import Path
from typing import Iterable, cast

from . import utils
from .config import CONFIG_PATH
from .types import ComposeLazyConfig, RepoPaths, WorkspaceConfig
from .utils import YamlHandler, call_safely, handle_config

from wcwidth import wcswidth


logger = logging.getLogger(__name__)


class AbstractWsExecutor(ABC):
    def __init__(self) -> None:
        self.handler = YamlHandler(CONFIG_PATH)

    def __call__(self, args: Namespace) -> int:
        self.handler.setup_config("workspaces")
        code = self._switch(args)
        return code

    @property
    def config(self) -> ComposeLazyConfig:
        """Return the workspace configuration as a typed view.

        Delegates to YamlHandler.config, which is lazily initialized on first access.
        The cast is zero-cost at runtime; it exists solely to propagate the type
        to subclasses without duplicating cast calls at each access site.
        """
        return cast(ComposeLazyConfig, self.handler.config)

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

    def _select_workspace_simply(
        self, candidates: Iterable[str], skip: bool = True
    ) -> str | None:
        candidates = list(candidates)
        if not candidates:
            print("❌️ No workspaces registered yet.", file=sys.stderr)
            print("💡 To register a new workspace, run `dcp ws register(reg)`.")
            return None
        elif len(candidates) == 1 and skip:
            choices = candidates
        else:
            self._display_intro(candidates)
            choices: list[str] = utils.interactive_select(candidates, multiple=False)
        return choices[0]

    def _display_intro(self, candidates: list[str]) -> None:
        msg = "✅️ Found {} registered workspace{}!"
        length = len(candidates)

        print()
        if length > 1:
            print(msg.format(length, "s"))
        else:
            print(msg.format(length, ""))


class WorkspaceRegistrar(AbstractWsExecutor):
    @call_safely
    @handle_config
    def _switch(self, args: Namespace) -> int:
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

    def pad_to(self, line: str, total_width: int) -> str:
        """右端の │ に合わせてスペースパディングして返す"""
        display_width = wcswidth(line)
        pad = total_width - display_width - 1  # 右の │ 分
        return line + " " * max(pad, 0) + "│"

    def show_list(self, workspaces: WorkspaceConfig | None = None, max_width: int | None = 100) -> int:
        workspaces = workspaces or self.config["workspaces"]
        if not workspaces:
            print("❌️ No workspaces registered yet.", file=sys.stderr)
            print("💡 To register a new workspace, run `dcp ws register(reg)`.")
            return 1

        term_width, _ = shutil.get_terminal_size()
        width = min(term_width, max_width) if max_width is not None else term_width
        inner = width - 2

        print("╭" + "─" * inner + "╮")

        label = "│   Workspaces "
        fill = inner - wcswidth(label) + 1
        print(label + " " * max(fill, 0) + "│")

        for ws_key in workspaces:
            label = f"├──── {ws_key} "
            fill = inner - wcswidth(label) + 1
            print(label + "─" * max(fill, 0) + "┤")

            repos_dict: RepoPaths = workspaces[ws_key]
            if not repos_dict:
                print(self.pad_to("│ ❌️ No repos registered yet.", width))
                continue

            for idx, repo_name in enumerate(repos_dict, start=1):
                print(self.pad_to(f"│ 📁 PATH[{idx}]: {repo_name}", width))
                print(
                    self.pad_to(
                        f"│      FILES: {', '.join(repos_dict[repo_name]['files'])}", width
                    )
                )
        print("╰" + "─" * inner + "╯")
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

        workspaces = self.config["workspaces"]
        workspace_name = self._select_workspace_or_create(workspaces)
        address = ("workspaces", workspace_name, str(new_repo), "files")
        for yaml_name in selected_yamls:
            appended = self.handler.append_value(*address, yaml_name)
            if appended:
                self.handler.dump_and_write()
                print(
                    f"✅️ Registered a new repo to {workspace_name}: {str(new_repo)} ({yaml_name})"
                )
            else:
                print(
                    f"✅️ `{str(new_repo)} ({yaml_name})` is already in `{workspace_name}`.",
                    file=sys.stderr,
                )
        if input("Enter 'l' to see the workspace or quit... : ") == "l":
            self.show_list(workspaces={workspace_name: workspaces[workspace_name]})
        print()
        print("💡 To get all workspace lists, run `dcp ws list(li)`.")
        return 0

    def delete_repo(self) -> int:
        workspaces = self.config["workspaces"]
        # User input
        if (
            workspace_name := self._select_workspace_simply(workspaces, skip=False)
        ) is None:
            return 1
        target_workspace: RepoPaths = workspaces[workspace_name]

        print()
        msg = "✅️ Found {} repositor{}!"
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
            print(f"✅️ Deleted: {name}")

        if not target_workspace:
            del workspaces[workspace_name]

        self.handler.dump_and_write()

        print()
        print("💡 To get all workspace lists, run `dcp ws list(li)`.")
        return 0


class WorkspaceProcessor(AbstractWsExecutor):
    BASE_COMMAND = ["docker", "compose"]

    @call_safely
    @handle_config
    def _switch(self, args: Namespace) -> int:

        if (workspace := self.get_target_workspace()) is None:
            return 1
        match args.ws_subcmd:
            case "exec" | "e":
                subcommand, workspace = self._get_exec_details(workspace)
            case "up" | "u":
                subcommand = ["up", "-d"]
            case "build" | "b":
                subcommand = ["build"]
            case "restart" | "re":
                subcommand = ["restart"]
            case "ps":
                subcommand = ["ps"]
            case "stop" | "s":
                subcommand = ["stop"]
            case "down":
                subcommand = ["down"]
            case _:  # pragma: no cover
                # Unreachable branch
                return 1  # pragma: no cover

        return self._iterate_execution(subcommand, workspace)

    def _iterate_execution(self, subcommand: list[str], workspace: RepoPaths) -> int:
        try:
            codes = []
            for workdir, v in workspace.items():
                yaml_names = v["files"]
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

    def get_target_workspace(self) -> RepoPaths | None:
        """Let the user select workspace and returns all paths in it.

        Returns:
            list[str]: All paths in a workspace user selected.
        """

        workspaces = self.config["workspaces"]
        workspace_name = self._select_workspace_simply(workspaces)
        if workspace_name is None:
            return None
        return workspaces[workspace_name]

    def _get_exec_details(self, workspace: RepoPaths) -> tuple[list[str], RepoPaths]:
        if len(workspace) == 1:
            single_paths = list(workspace)
        else:
            print()
            print(f"✅️ Found {len(workspace)} repositories!")
            single_paths = utils.interactive_select(workspace, multiple=False)
        path = single_paths[0]
        new_workdirs: RepoPaths = {path: workspace[path]}

        services = utils.get_service_from_yamls(
            [Path(path) / y for y in new_workdirs[path]["files"]]
        )
        if not services:
            print(f"❌ No services found in `{path}`.", file=sys.stderr)
            raise SystemExit(1)
        elif len(services) == 1:
            single_services = list(services)
        else:
            print()
            print(f"✅️ Found {len(services)} services!")
            single_services = utils.interactive_select(services, multiple=False)

        inner_container_command = input(
            f"Please enter the rest of `docker compose exec {single_services[0]} ...`: "
        ).split()

        subcommand = ["exec"] + single_services + (inner_container_command or ["bash"])
        return subcommand, new_workdirs
