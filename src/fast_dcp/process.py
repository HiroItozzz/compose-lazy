import glob
import logging
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import yaml

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

    def __call__(self, args: Namespace) -> int:
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

    def _create_up_cmd(self) -> None:
        self.cmd += (
            ["up"]
            + (["--build"] if self.args.build else [])
            + (["-d"] if self.args.detach else [])
            + (["--wait"] if self.args.wait else [])
            + self._create_container_option()
        )

    def _create_build_cmd(self) -> None:
        self.cmd += ["build"] + self._create_container_option()

    def _create_exec_cmd(self) -> None:
        self.cmd += (
            ["exec"]
            + self._create_container_option(multiple=False)
            + self.args.inner_bash_cmd
        )

    def _create_run_cmd(self) -> None:
        self.cmd += (
            ["run"]
            + self._create_container_option(multiple=False)
            + self.args.inner_bash_cmd
        )

    def _create_restart_cmd(self) -> None:
        self.cmd += ["restart"] + self._create_container_option()

    def _create_ps_cmd(self) -> None:
        self.cmd += (
            ["ps"]
            + self._create_container_option()
            + (["--all"] if self.args.all else [])
            + self._create_status_option()
        )

    def _create_logs_cmd(self) -> None:
        self.cmd += (
            ["logs"]
            + self._create_container_option()
            + (["-f"] if self.args.follow else [])
        )

    def _create_stop_cmd(self) -> None:
        self.cmd += ["stop"] + self._create_container_option()

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

    # Container option
    def _create_container_option(self, multiple: bool = True) -> list[str]:
        """Execute interactive selection if `--container` option is active"""
        input_args: list[str] = self.args.container_name

        if input_args:
            return input_args

        if multiple:
            if not self.args.container:
                return input_args

        try:
            return self._get_container_choices(multiple=multiple)
        except KeyboardInterrupt:
            sys.exit(130)
        except SystemExit:
            sys.exit(0)

    def _get_container_choices(self, multiple: bool = True) -> list[str]:
        """Execute interactive session to get container names."""
        file_paths = self._get_compose_file_paths()

        containers = set()
        for path in file_paths:
            with open(path) as f:
                data = yaml.safe_load(f)
            for container_name in (data or {}).get("services", {}).keys():
                containers.add(container_name)

        if not containers:
            print("❌ No services found.", file=sys.stderr)
            raise SystemExit

        if len(containers) == 1:
            c = containers.pop()
            print(f"☑ Service found: {c}")
            return [c]

        # Interactive session: select number(s) to get file args or press "Q" to quit.
        print(f"\n☑ Found {len(containers)} services!")

        return self._interactive_select(sorted(containers), multiple=multiple)

    # File option
    def _create_file_option(self) -> list[str]:
        file_args = []
        input_args: list[str] | None = self.args.file
        if input_args is None:
            return []  # Do nothing
        elif len(input_args) == 0:
            try:
                file_args += self._get_file_choices()
            except KeyboardInterrupt:
                sys.exit(130)
            except SystemExit:
                sys.exit(0)
        else:
            for f in self.args.file:
                if not (Path(f).suffix in [".yaml", ".yml"]):  # noqa: E713
                    # prints a warning, does not raise
                    print(f"invalid file type: {f}", file=sys.stderr)
                file_args += ["-f", f]

        return file_args

    def _get_file_choices(self) -> list[str]:
        """Execute interactive session to create -f args."""

        # List up docker-compose files
        file_dirs: list[str] = self._get_compose_file_paths()
        file_count = len(file_dirs)

        if file_count == 0:
            print("❌ docker-compose files haven't found.", file=sys.stderr)
            raise SystemExit

        if file_count == 1:
            print(f"☑ docker-compose file found: {file_dirs[0]}")
            return ["-f"] + file_dirs

        print(f"\n☑ Found {file_count} docker-compose files!")

        return self._interactive_select(file_dirs, "-f")

    # Profile option
    def _create_profile_option(self) -> list[str]:
        profile_args = []
        input_args: list[str] | None = self.args.profile
        if input_args is None:
            return []  # Do nothing
        elif len(input_args) == 0:
            try:
                profile_args += self._get_profile_choices()
            except KeyboardInterrupt:
                sys.exit(130)
            except SystemExit:
                sys.exit(0)
        else:
            for pf in input_args:
                profile_args += ["--profile", pf]

        return profile_args

    def _get_profile_choices(self) -> list[str]:
        """Execute interactive session to create --profile args."""
        file_paths = self._get_compose_file_paths()

        profiles = set()
        for path in file_paths:
            with open(path) as f:
                data = yaml.safe_load(f)
            for service in (data or {}).get("services", {}).values():
                for p in (service or {}).get("profiles", []):
                    profiles.add(p)

        if not profiles:
            print("❌ No profiles found.", file=sys.stderr)
            raise SystemExit

        if len(profiles) == 1:
            p = profiles.pop()
            print(f"☑ Profile found: {p}")
            return ["--profile", p]

        # Interactive session: select number(s) to get file args or press "Q" to quit.
        print(f"\n☑ Found {len(profiles)} profiles!")

        return self._interactive_select(sorted(profiles), "--profile")

    def _interactive_select(
        self, choice_list: list[str], flag: str | None = None, multiple: bool = True
    ) -> list[str]:

        args = []
        prompt = (
            "\nEnter your choices (e.g., 1,3,4) or 'Q' to quit: "
            if multiple
            else "\nEnter your choice or 'Q' to quit: "
        )
        err_msg = (
            "☓ Invalid selection. Please use valid numbers."
            if multiple
            else "☓ Invalid selection. Please use a valid number."
        )

        # Show choices
        for idx, choice in enumerate(choice_list, start=1):
            print(f"{idx:>5}. {choice}")

        # User input
        while True:
            try:
                if (choices_str := input(prompt)) in ["Q", "q"]:
                    print("\nCancelled.")
                    raise SystemExit

                choices = list(
                    map(
                        lambda i: int(i) - 1,
                        (i.strip() for i in choices_str.split(",") if i),
                    )
                )

                if not multiple and len(choices) > 1:
                    raise ValueError

                for idx in choices:
                    chosen = choice_list[idx]
                    if flag is None:
                        args += [chosen]
                    else:
                        args += [flag, chosen]

            except (ValueError, IndexError):
                print(err_msg, file=sys.stderr)
            except KeyboardInterrupt as e:
                print("\nCancelled.")
                raise e
            else:
                print()
                break
        return args

    @staticmethod
    def _get_compose_file_paths() -> list[str]:
        return glob.glob("*compose*.yml") + glob.glob("*compose*.yaml")
