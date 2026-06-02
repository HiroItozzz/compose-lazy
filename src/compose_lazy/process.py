import logging
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import yaml

from . import utils

logger = logging.getLogger(__name__)

_BASE_CMD = "docker", "compose"


class DockerCmdProcessor:
    def __init__(self) -> None:
        self.cmd: list[str] = []
        self._args = Namespace()

    @property
    def args(self) -> Namespace:
        return self._args

    def _setup(self, args: Namespace) -> None:
        logger.debug(f"\n----input args----\n{args}")
        self._args = args
        self.cmd = list(_BASE_CMD) + self._create_common_compose_options()

        if hasattr(args, "inner_bash_cmd"):
            self._adjust_service_name()

    def __call__(self, args: Namespace) -> int:
        try:
            self._setup(args)
            match args.subcmd:
                case "up" | "u":
                    self._create_up_cmd()
                case "build" | "b":
                    self._create_build_cmd()
                case "exec" | "e":
                    self._create_exec_cmd()
                case "run":
                    self._create_run_cmd()
                case "restart" | "re":
                    self._create_restart_cmd()
                case "ps":
                    self._create_ps_cmd()
                case "logs" | "l":
                    self._create_logs_cmd()
                case "stop" | "s":
                    self._create_stop_cmd()
                case "down":
                    self._create_down_cmd()
                case _:  # pragma: no cover
                    # Unreachable branch
                    return 1  # pragma: no cover
        except KeyboardInterrupt:
            return 130
        except SystemExit:
            return 1
        return self._execute_command()

    def call_dcpu(self, args: Namespace) -> int:
        self._setup(args)
        self._create_up_cmd()
        return self._execute_command()

    def call_dcpe(self, args: Namespace) -> int:
        self._setup(args)
        self._create_exec_cmd()
        return self._execute_command()

    def _execute_command(self) -> int:
        logger.debug(f"\n----output docker cmd---- \n{self.cmd}")
        print(f"▷ Executing `{' '.join(self.cmd)}`.")

        try:
            result = subprocess.run(self.cmd)
            return result.returncode
        except KeyboardInterrupt:
            return 130
        except FileNotFoundError:
            print("Docker is not found.", file=sys.stderr)
            return 1
        except Exception:
            logger.debug("An unexpected error occurred.", exc_info=True)
            print("An unexpected error occurred.", file=sys.stderr)
            return 1

    def _create_up_cmd(self) -> None:
        self.cmd += (
            ["up"]
            + (["--build"] if self.args.build else [])
            + (["-d"] if self.args.detach else [])
            + (["--wait"] if self.args.wait else [])
            + self._create_service_option()
        )

    def _create_build_cmd(self) -> None:
        self.cmd += ["build"] + self._create_service_option()

    def _create_exec_cmd(self) -> None:
        self.cmd += (
            ["exec"]
            + self._create_service_option(multiple=False)
            + (self.args.inner_bash_cmd or ["bash"])
        )

    def _create_run_cmd(self) -> None:
        self.cmd += (
            ["run"]
            + self._create_service_option(multiple=False)
            + (self.args.inner_bash_cmd or ["bash"])
        )

    def _create_restart_cmd(self) -> None:
        self.cmd += ["restart"] + self._create_service_option()

    def _create_ps_cmd(self) -> None:
        self.cmd += (
            ["ps"]
            + self._create_service_option()
            + (["--all"] if self.args.all else [])
            + self._create_status_option()
        )

    def _create_logs_cmd(self) -> None:
        self.cmd += (
            ["logs"]
            + self._create_service_option()
            + (["-f"] if self.args.follow else [])
        )

    def _create_stop_cmd(self) -> None:
        self.cmd += ["stop"] + self._create_service_option()

    def _create_down_cmd(self) -> None:
        self.cmd += ["down"] + (["--remove-orphans"] if self.args.remove_orphans else [])

    def _create_common_compose_options(self) -> list[str]:
        return (
            self._create_project_option()
            + self._create_file_option()
            + self._create_profile_option()
        )

    def _create_status_option(self) -> list[str]:
        if not self.args.status:
            return []
        return ["--status", self.args.status]

    def _create_project_option(self) -> list[str]:
        if not self.args.project:
            return []
        return ["-p", self.args.project]

    # File option
    def _create_file_option(self) -> list[str]:
        input_args: list[str] | None = self.args.file
        if input_args is None:
            return []  # Do nothing

        if input_args:
            file_args = []
            for f in input_args:
                if Path(f).suffix in [".yaml", ".yml"]:  # noqa: E713
                    file_args += ["-f", f]
                    # if invalid file input, start interactive selection.
                else:
                    print(
                        f"Invalid file type: {f}. Please select interactively.",
                        file=sys.stderr,
                    )
                    break
            else:
                return file_args

        file_list = utils.get_file_choices()

        return self._format_as_flag_args(file_list, "-f")

    # Profile option
    def _create_profile_option(self) -> list[str]:
        input_args: list[str] | None = self.args.profile
        if input_args is None:
            return []  # Do nothing

        if input_args:
            profile_args = []
            for pf in input_args:
                profile_args += ["--profile", pf]
            return profile_args

        profile_list = utils.get_profile_choices()
        return self._format_as_flag_args(profile_list, "--profile")

    # Service option
    def _create_service_option(self, multiple: bool = True) -> list[str]:
        """Return service name args for docker compose command.

        If service_name is given, return it as-is regardless of other options.

        If service_name is empty:
            - multiple=True, service=False : return [] (no selection)
            - multiple=True, service=True  : start interactive selection
            - multiple=False               : start interactive selection automatically
        """
        input_args: list[str] = self.args.service_name

        if input_args:
            return input_args

        if multiple:
            if not self.args.service:
                return input_args

        return utils.get_service_choices(multiple=multiple)

    def _adjust_service_name(self) -> None:
        """Move service_name to inner_bash_cmd if it doesn't match any declared service.

        Enables flows like `dcpe uv run pytest` where the first token is a command,
        not a service name — triggering interactive service selection automatically.
        """
        if not (user_input := self.args.service_name):
            return

        file_paths = utils.get_compose_file_paths()
        existing_services = set()

        for path in file_paths:
            with open(path) as f:
                data = yaml.safe_load(f)
            for services_name in (data or {}).get("services", {}).keys():
                existing_services.add(services_name)

        if set(user_input) <= existing_services:
            return

        self.args.inner_bash_cmd = user_input + self.args.inner_bash_cmd
        self.args.service_name = []

        logger.debug(f"\n----adjusted args----\n{self.args}")
        return

    @staticmethod
    def _format_as_flag_args(values: list[str], flag: str) -> list[str]:
        """Convert value list to ['flag', 'value1', 'flag', 'value2'] format."""
        args = []
        for v in values:
            args += [flag, v]
        return args
