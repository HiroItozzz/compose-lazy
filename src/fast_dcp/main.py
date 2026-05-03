from argparse import ArgumentParser

from . import config
from .args import ArgBuilder
from .process import DockerCmdProcessor as Processor
from importlib.metadata import version

VERSION = version(__package__)

logger = config.setup_logger("fast_dcp")


def main() -> None:
    base_parser = ArgumentParser(
        allow_abbrev=False,
        usage="dcp <command> [options]",
        description="Shorthand aliases for docker compose commands.",
        epilog="See also: `dcpu`, `dcpe`",
    )
    base_parser.add_argument("--version", action="version", version=f"fast-dcp {VERSION}")

    subparsers = base_parser.add_subparsers(dest="subcmd")

    # dcp up(u) command
    (
        ArgBuilder(
            subparsers.add_parser(
                "up",
                aliases=["u"],
                usage="dcp up(u) [container_names] [options]",
                description="Shorthand for `docker compose up`.",
                help="docker compose `up`",
            )
        )
        .add_project_args()
        .add_file_args()
        .add_build_args()
        .add_detach_args()
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=Processor())
    )

    # dcp build(b) command
    (
        ArgBuilder(
            subparsers.add_parser(
                "build",
                aliases=["b"],
                usage="dcp build(b) [container_names] [options]",
                description="Shorthand for `docker compose build`.",
                help="docker compose `build`",
            )
        )
        .add_project_args()
        .add_file_args()
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=Processor())
    )

    # dcp exec(e) command
    (
        ArgBuilder(
            subparsers.add_parser(
                "exec",
                aliases=["e"],
                usage="dcp exec(e) <container_name>  [options] [BASH|cmd]",
                description="Shorthand for `docker compose exec`.",
                help="docker compose `exec`",
            )
        )
        .add_container_name_subcmd(multiple=False)
        .add_inner_bash_cmd_args()
        .add_project_args()
        .add_file_args()
        .set_defaults(func=Processor())
    )

    # dcp restart(r) command
    (
        ArgBuilder(
            subparsers.add_parser(
                "restart",
                aliases=["r"],
                usage="dcp restart(r) [container_names]",
                description="Shorthand for `docker compose restart`.",
                help="docker compose `restart`",
            )
        )
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=Processor())
    )

    # dcp ps command
    ArgBuilder(
        subparsers.add_parser(
            "ps",
            usage="dcp ps",
            description="Shorthand for `docker compose ps`.",
            help="docker compose `ps`",
        )
    ).set_defaults(func=Processor())

    # dcp logs(l) command
    (
        ArgBuilder(
            subparsers.add_parser(
                "logs",
                aliases=["l"],
                usage="dcp logs(l) [container_names] [options]",
                description="Shorthand for `docker compose logs`.",
                help="docker compose `logs`",
            )
        )
        .add_container_name_subcmd(multiple=True)
        .add_follow_args()
        .set_defaults(func=Processor())
    )

    # dcp stop(s) command
    (
        ArgBuilder(
            subparsers.add_parser(
                "stop",
                aliases=["s"],
                usage="dcp stop(s) [container_names]",
                description="Shorthand for `docker compose stop`.",
                help="docker compose `stop`",
            )
        )
        .add_container_name_subcmd(multiple=True)
        .set_defaults(func=Processor())
    )

    # dcp down command
    (
        ArgBuilder(
            subparsers.add_parser(
                "down",
                usage="dcp down [options]",
                description="Shorthand for `docker compose down`.",
                help="docker compose `down`",
            )
        )
        .add_file_args()
        .add_project_args()
        .set_defaults(func=Processor())
    )

    args = base_parser.parse_args()
    if args.subcmd is None:
        base_parser.print_help()
        exit(0)
    code = args.func(args)
    exit(code)


def dcpu_main() -> None:
    parser = ArgumentParser(
        allow_abbrev=False,
        usage="dcpu [container_names] [options]",
        description="Shorthand for `docker compose up`.",
        epilog="See also: `dcp`, `dcpe`",
    )
    parser.add_argument("--version", action="version", version=f"fast-dcp {VERSION}")

    # dcpu command
    (
        ArgBuilder(parser)
        .add_container_name_subcmd(multiple=True)
        .add_build_args()
        .add_detach_args()
        .add_file_args()
        .add_project_args()
        .set_defaults(func=Processor().call_dcpu)
    )

    args = parser.parse_args()
    code = args.func(args)
    exit(code)


def dcpe_main() -> None:
    parser = ArgumentParser(
        allow_abbrev=False,
        usage="dcpe <container_name> [options] [BASH|commands]",
        description="Shorthand for `docker compose exec`.",
        epilog="See also: `dcp`, `dcpu`",
    )
    parser.add_argument("--version", action="version", version=f"fast-dcp {VERSION}")
    # dcpe command
    (
        ArgBuilder(parser)
        .add_container_name_subcmd(multiple=False)
        .add_inner_bash_cmd_args()
        .add_file_args()
        .add_project_args()
        .set_defaults(func=Processor().call_dcpe)
    )

    args = parser.parse_args()
    code = args.func(args)
    exit(code)
