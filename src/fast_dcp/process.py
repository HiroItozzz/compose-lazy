import glob
import logging
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

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
        self.cmd = list(_BASE_CMD)
        self._args = args

    def __call__(self, args: Namespace) -> int:
        self._setup(args)
        match args.subcmd:
            case "up" | "u":
                self._create_up_cmd()
            case "build" | "b":
                self._create_build_cmd()
            case "exec" | "e":
                self._create_exec_cmd()
            case "run" | "R":
                self._create_run_cmd()
            case "restart" | "r":
                self._create_restart_cmd()
            case "ps":
                self._create_ps_cmd()
            case "logs" | "l":
                self._create_logs_cmd()
            case "stop" | "s":
                self._create_stop_cmd()
            case "down":
                self._create_down_cmd()
        return self._run_cmd()

    def call_dcpu(self, args: Namespace) -> int:
        self._setup(args)
        self._create_up_cmd()
        return self._run_cmd()

    def call_dcpe(self, args: Namespace) -> int:
        self._setup(args)
        self._create_exec_cmd()
        return self._run_cmd()

    def _run_cmd(self) -> int:
        logger.debug(f"\n----output docker cmd---- \n{self.cmd}")
        print(f"🚀 Executing `{' '.join(self.cmd)}`.")

        try:
            result = subprocess.run(self.cmd)
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def _create_up_cmd(self) -> None:
        self.cmd += (
            self._create_project_option()
            + self._create_file_option()
            + ["up"]
            + (["--build"] if self.args.build else [])
            + (["-d"] if self.args.detach else [])
            + self.args.container_name
        )

    def _create_build_cmd(self) -> None:
        self.cmd += (
            self._create_project_option()
            + self._create_file_option()
            + ["build"]
            + self.args.container_name
        )

    def _create_exec_cmd(self) -> None:
        self.cmd += (
            self._create_project_option()
            + self._create_file_option()
            + ["exec"]
            + self.args.container_name
            + self.args.inner_bash_cmd
        )

    def _create_run_cmd(self) -> None:
        self.cmd += ["run"] + self.args.container_name + self.args.inner_bash_cmd

    def _create_restart_cmd(self) -> None:
        self.cmd += ["restart"] + self.args.container_name

    def _create_ps_cmd(self) -> None:
        self.cmd += (
            ["ps"]
            + self.args.container_name
            + (["--all"] if self.args.all else [])
            + self._create_status_option()
        )

    def _create_logs_cmd(self) -> None:
        self.cmd += (
            ["logs"] + self.args.container_name + (["-f"] if self.args.follow else [])
        )

    def _create_stop_cmd(self) -> None:
        self.cmd += ["stop"] + self.args.container_name

    def _create_down_cmd(self) -> None:
        self.cmd += (
            self._create_project_option()
            + self._create_file_option()
            + ["down"]
            + (["--remove-orphans"] if self.args.remove_orphans else [])
        )

    def _create_file_option(self) -> list[str]:
        file_args = []
        input_args: list[str] | None = self.args.file
        if input_args is None:
            return []  # Do nothing
        elif len(input_args) == 0:
            try:
                file_args += self._show_file_choices()
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

    def _create_project_option(self) -> list[str]:
        if not self.args.project:
            return []
        return ["-p"] + self.args.project

    def _create_status_option(self) -> list[str]:
        if not self.args.status:
            return []
        return ["--status", self.args.status]

    def _show_file_choices(self) -> list[str]:
        """Execute interactive session to create docker-compose file args."""

        # List up docker-compose files
        file_dirs: list[str] = glob.glob("*compose*.yml") + glob.glob("*compose*.yaml")
        file_count = len(file_dirs)

        if file_count == 0:
            print("❌ docker-compose file not found.")
            raise SystemExit

        if file_count == 1:
            print(f"✅ docker-compose file found: {file_dirs[0]}")
            return ["-f"] + file_dirs

        print(f"\n✅ Found {file_count} docker-compose files!")

        # Show choices
        for idx, filedir in enumerate(file_dirs, start=1):
            print(f"{idx:>5}. {filedir}")

        # Interactive session: select number(s) to get file args or press "Q" to quit.
        args = []
        while True:
            try:
                file_index_str = input(
                    "\nEnter your choices (e.g., 1,3,4) or 'Q' to quit: "
                )
                if file_index_str in ["Q", "q"]:
                    print("\nCancelled.")
                    raise SystemExit
                file_index = map(
                    lambda i: int(i) - 1,
                    (i.strip() for i in file_index_str.split(",") if i),
                )
                for idx in file_index:
                    args += ["-f", file_dirs[idx]]
            except (ValueError, IndexError):
                print("❌ Invalid selection. Please use valid numbers.")
            except KeyboardInterrupt as e:
                print("\nCancelled.")
                raise e
            else:
                print()
                break
        return args
