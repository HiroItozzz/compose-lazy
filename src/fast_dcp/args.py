import logging
from argparse import ArgumentParser, Namespace
from typing import Callable, Self

from .process import DockerCmdProcessor

logger = logging.getLogger(__name__)


class ArgBuilder:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def set_defaults(self, func: Callable[[Namespace], int] | None = None) -> Self:
        func = func or DockerCmdProcessor()
        self.parser.set_defaults(func=func)
        return self

    def add_common_compose_options(self) -> Self:
        return self._add_file_args()._add_profile_args()._add_project_args()

    def add_container_name_subcmd(self, multiple: bool = False) -> Self:
        """add positional argument of container name(s) to command definition."""
        if multiple:
            self.parser.add_argument(
                "container_name",
                action="extend",
                nargs="*",
                default=[],
                help="(optional) target container names",
            )
        else:
            self.parser.add_argument(
                "container_name",
                action="extend",
                nargs=1,
                default=[],
                help="(required) target container name",
            )
        return self

    def add_inner_bash_cmd_args(self) -> Self:
        self.parser.add_argument(
            "inner_bash_cmd",
            nargs="*",
            default=["bash"],
            help="command to run inside the container (default: bash)",
        )
        return self

    def add_build_args(self) -> Self:
        self.parser.add_argument(
            "-b",
            "--build",
            action="store_true",
            help="docker compose up `--build`",
        )
        return self

    def add_detach_args(self) -> Self:
        """add optional argument `-d` to `docker compose up` command."""
        self.parser.add_argument(
            "-d", "--detach", action="store_true", help="docker compose up `-d`"
        )
        return self

    def add_follow_args(self) -> Self:
        """add optional argument `-f` to `docker compose logs` command."""
        self.parser.add_argument(
            "-fo", "--follow", action="store_true", help="docker compose logs `-f`"
        )
        return self

    def add_all_args(self) -> Self:
        """add optional argument `--all(-a)` to `docker compose ps` command."""
        self.parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="docker compose ps `-a`",
        )
        return self

    def add_status_args(self) -> Self:
        self.parser.add_argument(
            "-st",
            "--status",
            choices=[
                "created",
                "restarting",
                "running",
                "removing",
                "paused",
                "exited",
                "dead",
            ],
            help="docker compose ps `--status` <STATUS>",
        )
        return self

    def add_remove_orphans_args(self) -> Self:
        self.parser.add_argument(
            "-ro",
            "--remove-orphans",
            action="store_true",
            help="docker compose down `--remove-orphans`",
        )
        return self

    def add_wait_args(self) -> Self:
        self.parser.add_argument(
            "-w",
            "--wait",
            action="store_true",
            help="docker compose up `--wait`",
        )
        return self

    def _add_file_args(self) -> Self:
        self.parser.add_argument(
            "-f",
            "--file",
            nargs="*",
            help="specify compose file(s). if omitted with -f, select interactively",
        )
        return self

    def _add_project_args(self) -> Self:
        self.parser.add_argument(
            "-p",
            "--project",
            default="",
            help="docker compose `-p PROJECT_NAME`",
        )
        return self

    def _add_profile_args(self) -> Self:
        self.parser.add_argument(
            "-pf",
            "--profile",
            nargs="*",
            help="specify profile(s). if omitted with -pf, select interactively",
        )
        return self
