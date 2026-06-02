import logging
import sys
from pathlib import Path

import yaml

from . import cli_utils

logger = logging.getLogger(__name__)

def format_as_flag_args(values: list[str], flag: str) -> list[str]:
    """Convert value list to ['flag', 'value1', 'flag', 'value2'] format."""
    args = []
    for v in values:
        args += [flag, v]
    return args

def get_compose_file_paths(path: Path | None = None) -> list[Path]:
    path: Path = path or Path.cwd()
    return [*path.glob("*compose*.yml"), *path.glob("*compose*.yaml")]


def get_service_from_yamls(file_paths: list[Path]) -> set[str]:
    """Extract unique docker-compose service names out of given YAML paths."""
    services = set()
    for path in file_paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for services_name in (data or {}).get("services", {}).keys():
            services.add(services_name)
    return services


def get_profile_from_yamls(file_paths: list[Path]) -> set[str]:
    """Extract unique docker-compose profile names out of given YAML paths."""
    profiles = set()
    for path in file_paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for service in (data or {}).get("services", {}).values():
            for p in (service or {}).get("profiles", []):
                profiles.add(p)
    return profiles


def get_file_choices(path: Path | None = None) -> list[str]:
    """Execute interactive session to create -f args."""

    # List up docker-compose files
    file_names: list[str] = [f.name for f in get_compose_file_paths(path) if f]

    if not file_names:
        print("❌ No compose files found.", file=sys.stderr)
        raise SystemExit

    if (file_count := len(file_names)) == 1:
        print(f"☑ Compose file found: {file_names[0]}")
        return file_names

    print(f"\n☑ Found {file_count} docker-compose files!")
    return cli_utils.interactive_select(file_names)


def get_profile_choices(path: Path | None = None) -> list[str]:
    """Execute interactive session to create --profile args."""
    file_paths = get_compose_file_paths(path)
    if not file_paths:
        print("❌ No compose files found.", file=sys.stderr)
        raise SystemExit

    profiles = get_profile_from_yamls(file_paths)
    if not profiles:
        print("❌ No profiles found.", file=sys.stderr)
        raise SystemExit

    if len(profiles) == 1:
        p = profiles.pop()
        print(f"☑ Profile found: {p}")
        return [p]

    # Interactive session: select number(s) to get file args or press "Q" to quit.
    print(f"\n☑ Found {len(profiles)} profiles!")

    return cli_utils.interactive_select(profiles)


def get_service_choices(path: Path | None = None, *, multiple: bool = True) -> list[str]:
    """Execute interactive session to get service names."""
    file_paths = get_compose_file_paths(path)
    if not file_paths:
        print("❌ No compose files found.", file=sys.stderr)
        raise SystemExit

    services = get_service_from_yamls(file_paths)

    if not services:
        print("❌ No services found.", file=sys.stderr)
        raise SystemExit

    if len(services) == 1:
        s = services.pop()
        print(f"☑ Service found: {s}")
        return [s]

    # Interactive session: select number(s) to get file args or press "Q" to quit.
    print(f"\n☑ Found {len(services)} services!")

    return cli_utils.interactive_select(services, multiple=multiple)
