import logging
import sys
from argparse import ArgumentParser
from importlib.metadata import version

from . import config
from .args import ArgBuilder
from .process import DockerCmdProcessor
from .workspace import WorkspaceProcessor, WorkspaceRegistrar

VERSION = version("compose_lazy")

logger = logging.getLogger(__name__)

processor = DockerCmdProcessor()
ws_registrar = WorkspaceRegistrar()
ws_processor = WorkspaceProcessor()


def main() -> None:
    config.setup_logger("compose_lazy")

    base_parser = ArgumentParser(
        allow_abbrev=False,
        usage="dcp <SUBCOMMAND> [options]",
        description="Shorthand aliases for docker compose commands.",
        epilog="See also: `dcpu -h`, `dcpe -h`, `dcp ws -h`",
    )
    base_parser.suggest_on_error = True  # ty: ignore
    base_parser.add_argument(
        "--version", action="version", version=f"compose-lazy {VERSION}"
    )

    root_subparsers = base_parser.add_subparsers(dest="subcmd")

    # dcp up(u) command
    _up = root_subparsers.add_parser(
        "up",
        aliases=["u"],
        allow_abbrev=False,
        usage="dcp up(u) [SERVICE_NAME ...] [options]",
        description="Shorthand for `docker compose up`.",
        help="docker compose `up`, also available as: dcpu",
    )
    (
        ArgBuilder(_up)
        .add_service_name_subcmd(multiple=True)
        .add_detach_args()
        .add_build_args()
        .add_wait_args()
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp build(b) command
    _build = root_subparsers.add_parser(
        "build",
        aliases=["b"],
        allow_abbrev=False,
        usage="dcp build(b) [SERVICE_NAME ...] [options]",
        description="Shorthand for `docker compose build`.",
        help="docker compose `build`",
    )
    (
        ArgBuilder(_build)
        .add_service_name_subcmd(multiple=True)
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp exec(e) command
    _exec = root_subparsers.add_parser(
        "exec",
        aliases=["e"],
        allow_abbrev=False,
        usage="dcp exec(e) <SERVICE_NAME> [BASH|commands] [options]",
        description="Shorthand for `docker compose exec`.",
        help="docker compose `exec`, also available as: dcpe",
    )
    (
        ArgBuilder(_exec)
        .add_service_name_subcmd(multiple=False)
        .add_inner_cmd_args()
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp run command
    _run = root_subparsers.add_parser(
        "run",
        allow_abbrev=False,
        usage="dcp run <SERVICE_NAME> [BASH|commands]",
        description="Shorthand for `docker compose run`.",
        help="docker compose `run`",
    )
    (
        ArgBuilder(_run)
        .add_service_name_subcmd(multiple=False)
        .add_inner_cmd_args()
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp restart(re) command
    _restart = root_subparsers.add_parser(
        "restart",
        aliases=["re"],
        allow_abbrev=False,
        usage="dcp restart(re) [SERVICE_NAME ...]",
        description="Shorthand for `docker compose restart`.",
        help="docker compose `restart`",
    )
    (
        ArgBuilder(_restart)
        .add_service_name_subcmd(multiple=True)
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp ps command
    _ps = root_subparsers.add_parser(
        "ps",
        allow_abbrev=False,
        usage="dcp ps [SERVICE_NAME ...] [-a] [-st STATUS]",
        description="Shorthand for `docker compose ps`.",
        help="docker compose `ps`",
    )
    (
        ArgBuilder(_ps)
        .add_service_name_subcmd(multiple=True)
        .add_all_args()
        .add_status_args()
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp logs(l) command
    _logs = root_subparsers.add_parser(
        "logs",
        aliases=["l"],
        allow_abbrev=False,
        usage="dcp logs(l) [SERVICE_NAME ...] [-f]",
        description="Shorthand for `docker compose logs`.",
        help="docker compose `logs`",
    )
    (
        ArgBuilder(_logs)
        .add_service_name_subcmd(multiple=True)
        .add_follow_args()
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp stop(s) command
    _stop = root_subparsers.add_parser(
        "stop",
        aliases=["s"],
        allow_abbrev=False,
        usage="dcp stop(s) [SERVICE_NAME ...]",
        description="Shorthand for `docker compose stop`.",
        help="docker compose `stop`",
    )
    (
        ArgBuilder(_stop)
        .add_service_name_subcmd(multiple=True)
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp down command
    _down = root_subparsers.add_parser(
        "down",
        allow_abbrev=False,
        usage="dcp down [-f FILE_NAME ...] [-p PROJECT_NAME] [-ro]",
        description="Shorthand for `docker compose down`.",
        help="docker compose `down`",
    )
    (
        ArgBuilder(_down)
        .add_remove_orphans_args()
        .add_common_compose_options()
        .set_defaults(func=processor)
    )

    # dcp workspace(ws) command
    _workspace = root_subparsers.add_parser(
        "workspace",
        aliases=["ws"],
        allow_abbrev=False,
        usage="dcp workspace(ws) [SUBCOMMAND] [options]",
        description="Operate all repos in a user-defined workspace (a named group of repositories).",
        help="Original command, operate multiple repos at once. See also `dcp ws -h`.",
    )
    ws_subparsers = _workspace.add_subparsers(dest="ws_subcmd")

    # dcp ws register command
    ws_subparsers.add_parser(
        "register",
        aliases=["reg"],
        allow_abbrev=False,
        usage="dcp ws register(reg)",
        description="Register a new repository to a workspace interactively.",
        help="Register a new repo to a workspace.",
    ).set_defaults(func=ws_registrar)

    # dcp ws delete command
    ws_subparsers.add_parser(
        "delete",
        aliases=["del"],
        allow_abbrev=False,
        usage="dcp ws delete(del)",
        description="Delete a repository from a workspace interactively.",
        help="Delete a repo from a workspace.",
    ).set_defaults(func=ws_registrar)

    # dcp ws list command
    ws_subparsers.add_parser(
        "list",
        aliases=["li"],
        allow_abbrev=False,
        usage="dcp ws list(li)",
        description="Show all registered workspaces and their repositories.",
        help="List all registered workspaces.",
    ).set_defaults(func=ws_registrar)

    # dcp ws up command
    ws_subparsers.add_parser(
        "up",
        aliases=["u"],
        allow_abbrev=False,
        usage="dcp ws up(u)",
        description="Run `docker compose up -d` for all repos in a selected workspace.",
        help="docker compose `up` for each repo.",
    ).set_defaults(func=ws_processor)

    # dcp ws build command
    ws_subparsers.add_parser(
        "build",
        aliases=["b"],
        allow_abbrev=False,
        usage="dcp ws build(b)",
        description="Run `docker compose build` for all repos in a selected workspace.",
        help="docker compose `build` for each repo.",
    ).set_defaults(func=ws_processor)

    # dcp ws restart command
    ws_subparsers.add_parser(
        "restart",
        aliases=["re"],
        allow_abbrev=False,
        usage="dcp ws restart(re)",
        description="Run `docker compose restart` for all repos in a selected workspace.",
        help="docker compose `restart` for each repo.",
    ).set_defaults(func=ws_processor)

    # dcp ws stop command
    ws_subparsers.add_parser(
        "stop",
        aliases=["s"],
        allow_abbrev=False,
        usage="dcp ws stop(s)",
        description="Run `docker compose stop` for all repos in a selected workspace.",
        help="docker compose `stop` for each repo.",
    ).set_defaults(func=ws_processor)

    # dcp ws down command
    ws_subparsers.add_parser(
        "down",
        allow_abbrev=False,
        usage="dcp ws down",
        description="Run `docker compose down` for all repos in a selected workspace.",
        help="docker compose `down` for each repo.",
    ).set_defaults(func=ws_processor)

    args = base_parser.parse_args()
    if args.subcmd is None:
        base_parser.print_help()
        sys.exit(0)
    if args.subcmd in ("workspace", "ws") and args.ws_subcmd is None:
        _workspace.print_help()
        sys.exit(0)

    code = args.func(args)
    sys.exit(code)


def dcpu_main() -> None:
    config.setup_logger("compose_lazy")

    parser = ArgumentParser(
        allow_abbrev=False,
        usage="dcpu [SERVICE_NAME] [options]",
        description="Shorthand for `docker compose up`.",
        epilog="See also: `dcp -h`, `dcpe -h`",
    )

    # dcpu command
    (
        ArgBuilder(parser)
        .add_service_name_subcmd(multiple=True)
        .add_detach_args()
        .add_build_args()
        .add_wait_args()
        .add_common_compose_options()
        .set_defaults(func=processor.call_dcpu)
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"compose-lazy {VERSION}"
    )

    args = parser.parse_args()
    code = args.func(args)
    sys.exit(code)


def dcpe_main() -> None:
    config.setup_logger("compose_lazy")

    parser = ArgumentParser(
        allow_abbrev=False,
        usage="dcpe <SERVICE_NAME> [BASH|commands] [options]",
        description="Shorthand for `docker compose exec`.",
        epilog="See also: `dcp -h`, `dcpu -h`",
    )

    # dcpe command
    (
        ArgBuilder(parser)
        .add_service_name_subcmd(multiple=False)
        .add_inner_cmd_args()
        .add_common_compose_options()
        .set_defaults(func=processor.call_dcpe)
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"compose-lazy {VERSION}"
    )

    args = parser.parse_args()
    code = args.func(args)
    sys.exit(code)
