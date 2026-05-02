from __future__ import annotations

import logging
from argparse import ArgumentParser, Namespace
from typing import Callable

from .set_cmd import DockerCmdProcessor

logger = logging.getLogger(__name__)


class ArgDefiner:
    def __init__(self, parser: ArgumentParser):
        self.parser = parser

    def set_defaults(self, func: Callable[[Namespace], int] = DockerCmdProcessor()) -> ArgDefiner:
        self.parser.set_defaults(func=func)
        return self

    def add_container_name_subcmd(self, multiple: bool = False):
        """add positional argument of container name(s) to command definition."""
        if multiple:
            self.parser.add_argument("container_name", nargs="*", default=[])
        else:
            self.parser.add_argument("container_name", nargs=1)
        return self

    def add_inner_bash_cmd_args(self):
        self.parser.add_argument("inner_bash_cmd", nargs="*", default=["bash"])
        return self

    def add_file_args(self) -> ArgDefiner:
        self.parser.add_argument(
            "-f",
            "--file",
            nargs="*",
            default=[],
            help="docker compose `-f FILE_1 [-f FILE_2 ...]` ...",
        )
        return self

    def add_project_args(self) -> ArgDefiner:
        self.parser.add_argument(
            "-p",
            "--project",
            help="docker compose `-p PROJECT_NAME` ...",
        )
        return self

    def add_build_args(self) -> ArgDefiner:
        self.parser.add_argument("-b", "--build", action="store_true", help="docker compose up `--build`...")
        return self

    def add_follow_args(self):
        self.parser.add_argument("-F", "--follow", action="store_true")
        return self
