from argparse import ArgumentParser

from . import config
from .add_args import ArgDefiner
from .set_cmd import DockerCmdProcessor as processor

logger = config.setup_logger("fast_dcp")


def main():
    base_parser = ArgumentParser(allow_abbrev=False, usage="aliases docker compose commands.")

    subparsers = base_parser.add_subparsers(dest="subcmd")

    _up = (
        ArgDefiner(subparsers.add_parser("up", aliases=["u"], help="docker compose `up`..."))
        .add_project_args()
        .add_file_args()
        .add_build_args()
        .set_defaults(func=processor())
    )

    _build = (
        ArgDefiner(subparsers.add_parser("build", aliases=["b"], help="docker compose `up`..."))
        .add_project_args()
        .add_file_args()
        .set_defaults(func=processor())
    )

    _exec = (
        ArgDefiner(subparsers.add_parser("exec", aliases=["e"]))
        .add_container_name_subcmd(multiple=False)
        .add_inner_bash_cmd_args()
        .add_project_args()
        .add_file_args()
        .set_defaults(func=processor())
    )

    _restart = (
        ArgDefiner(subparsers.add_parser("restart", aliases=["r"]))
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=processor())
    )

    _ps = ArgDefiner(subparsers.add_parser("ps")).set_defaults(func=processor())

    _logs = (
        ArgDefiner(subparsers.add_parser("logs", aliases=["l"]))
        .add_container_name_subcmd(multiple=True)
        .add_follow_args()
        .set_defaults(func=processor())
    )

    _stop = (
        ArgDefiner(subparsers.add_parser("stop", aliases=["s"]))
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=processor())
    )

    _down = (
        ArgDefiner(subparsers.add_parser("down"))
        .add_file_args()
        .add_project_args()
        .set_defaults(func=processor())
    )

    args = base_parser.parse_args()
    code = args.func(args)
    exit(code)


def dcpu_main():
    return 0


def dcpe_main():
    return 0
