import logging
import subprocess
from argparse import Namespace

logger = logging.getLogger(__name__)

_BASE_CMD = "docker", "compose"


class DockerCmdProcessor:
    def __init__(self):
        self.cmd = list(_BASE_CMD)
        self._args: Namespace | None = None

    @property
    def args(self) -> Namespace | None:
        return self._args

    def __call__(self, args: Namespace) -> int:
        logger.debug(f"\n----input args----\n{args}")
        self._args = args
        match args.subcmd:
            case "up" | "u":
                self._create_up_cmd()
            case "build" | "b":
                self._create_build_cmd()
            case "exec" | "e":
                self._create_exec_cmd()
            case "restart" | "r":
                self._create_restart_cmd()
            case "ps":
                self._create_ps_cmd()
            case "logs" | "l":
                self._create_logs_cmd()
            case "stop":
                self._create_stop_cmd()
            case "down":
                self._create_down_cmd()
        logger.debug(f"\n----output docker cmd---- \n{self.cmd}")
        return self._run_subprocess()

    def _run_subprocess(self) -> int:
        print(f"executing `{' '.join(self.cmd)}`")
        subprocess.run(self.cmd)
        return 0

    def _create_up_cmd(self) -> None:
        self.cmd += self._create_project_option() \
                    + self._create_file_option() \
                    + ["up"]
        if self.args.build:
            self.cmd += ["--build"]

    def _create_build_cmd(self) -> None:
        self.cmd += self._create_project_option() \
                    + self._create_file_option() \
                    + ["build"]

    def _create_exec_cmd(self) -> None:
        self.cmd += ["exec"] \
                    + self.args.container_name \
                    + self.args.inner_bash_cmd

    def _create_restart_cmd(self) -> None:
        self.cmd += ["restart"] \
                    + self.args.container_name

    def _create_ps_cmd(self) -> None:
        self.cmd += ["ps"]

    def _create_logs_cmd(self) -> None:
        self.cmd += ["logs"] \
                    + self.args.container_name \
                    + (["-f"] if self.args.follow else [])

    def _create_stop_cmd(self) -> None:
        self.cmd += ["stop"] \
                    + self.args.container_name

    def _create_down_cmd(self) -> None:
        self.cmd += ["down"] \
                    + self.args.container_name

    def _create_file_option(self) -> list[str]:
        file_args = []
        for f in self.args.file:
            if not (f.rsplit(".", maxsplit=1)[-1] in ["yaml", "yml"]):
                print(f"invalid file type: {f}")
            file_args += ["-f", f]
        return file_args

    def _create_project_option(self) -> list[str]:
        if not self.args.project:
            return []
        return ["-p", self.args.project]
