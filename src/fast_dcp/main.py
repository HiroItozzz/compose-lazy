from argparse import ArgumentParser

from . import config
from .args import ArgDefiner
from .process import DockerCmdProcessor as processor

logger = config.setup_logger("fast_dcp")


def main() -> None:
    base_parser = ArgumentParser(allow_abbrev=False, usage="aliases docker compose commands.")
    subparsers = base_parser.add_subparsers(dest="subcmd")

    # dcp up(u) command
    (
        ArgDefiner(subparsers.add_parser("up", aliases=["u"], help="docker compose `up`..."))
        .add_project_args()
        .add_file_args()
        .add_build_args()
        .add_detach_args()
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=processor())
    )

    # dcp build(b) command
    (
        ArgDefiner(subparsers.add_parser("build", aliases=["b"], help="docker compose `up`..."))
        .add_project_args()
        .add_file_args()
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=processor())
    )

    # dcp exec(e) command
    (
        ArgDefiner(subparsers.add_parser("exec", aliases=["e"]))
        .add_container_name_subcmd(multiple=False)
        .add_inner_bash_cmd_args()
        .add_project_args()
        .add_file_args()
        .set_defaults(func=processor())
    )

    # dcp restart(r) command
    (
        ArgDefiner(subparsers.add_parser("restart", aliases=["r"]))
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=processor())
    )

    # dcp ps command
    ArgDefiner(subparsers.add_parser("ps")).set_defaults(func=processor())

    # dcp logs(l) command
    (
        ArgDefiner(subparsers.add_parser("logs", aliases=["l"]))
        .add_container_name_subcmd(multiple=True)
        .add_follow_args()
        .set_defaults(func=processor())
    )

    # dcp stop(s) command
    (
        ArgDefiner(subparsers.add_parser("stop", aliases=["s"]))
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=processor())
    )

    # dcp down command
    _dcp_down = (
        ArgDefiner(subparsers.add_parser("down"))
        .add_file_args()
        .add_project_args()
        .set_defaults(func=processor())
    )

    args = base_parser.parse_args()
    code = args.func(args)
    exit(code)


def dcpu_main() -> None:
    parser = ArgumentParser(allow_abbrev=False, usage="aliases docker compose commands.")

    # dcpu command
    (
        ArgDefiner(parser)
        .add_container_name_subcmd(multiple=True)
        .add_project_args()
        .add_file_args()
        .add_build_args()
        .add_detach_args()
        .set_defaults(func=processor().call_dcpu)
    )

    args = parser.parse_args()
    code = args.func(args)
    exit(code)


def dcpe_main() -> None:
    parser = ArgumentParser(allow_abbrev=False, usage="aliases docker compose commands.")

    # dcpe command
    (
        ArgDefiner(parser)
        .add_container_name_subcmd(multiple=False)
        .add_inner_bash_cmd_args()
        .add_project_args()
        .add_file_args()
        .set_defaults(func=processor().call_dcpe)
    )

    args = parser.parse_args()
    code = args.func(args)
    exit(code)
