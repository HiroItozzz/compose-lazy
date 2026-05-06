from __future__ import annotations

import logging
from argparse import ArgumentParser, Namespace
from typing import Callable, Self

from .process import DockerCmdProcessor

logger = logging.getLogger(__name__)


class ArgBuilder:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def set_defaults(
        self, func: Callable[[Namespace], int] | None = None
    ) -> ArgBuilder:
        func = func or DockerCmdProcessor()
        self.parser.set_defaults(func=func)
        return self

    def add_container_name_subcmd(self, multiple: bool = False) -> ArgBuilder:
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

    def add_inner_bash_cmd_args(self) -> ArgBuilder:
        self.parser.add_argument(
            "inner_bash_cmd",
            nargs="*",
            default=["bash"],
            help="command to run inside the container (default: bash)",
        )
        return self

    def add_file_args(self) -> ArgBuilder:
        self.parser.add_argument(
            "-f",
            "--file",
            nargs="+",
            default=[],
            help="docker compose `-f FILE -f FILE ...`",
        )
        return self

    def add_project_args(self) -> ArgBuilder:
        self.parser.add_argument(
            "-p",
            "--project",
            nargs=1,
            default=[],
            help="docker compose `-p PROJECT_NAME`",
        )
        return self

    def add_build_args(self) -> ArgBuilder:
        self.parser.add_argument(
            "-b",
            "--build",
            action="store_true",
            help="docker compose up --build",
        )
        return self

    def add_detach_args(self) -> ArgBuilder:
        """add optional argument `-d` to `docker compose up` command."""
        self.parser.add_argument(
            "-d", "--detach", action="store_true", help="docker compose up -d"
        )
        return self

    def add_follow_args(self) -> ArgBuilder:
        """add optional argument `-f` to `docker compose logs` command."""
        self.parser.add_argument(
            "-F", "--follow", action="store_true", help="docker compose logs -f"
        )
        return self

    def add_all_args(self) -> ArgBuilder:
        """add optional argument `--all(-a)` to `docker compose ps` command."""
        self.parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="docker compose ps -a(--all)",
        )
        return self

    def add_status_args(self) -> ArgBuilder:
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
            help="docker compose ps -st(--status) <STATUS>",
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
