import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def get_services(file_paths: list[Path]) -> set[str]:
    """Extract unique docker-compose service names out of given YAML paths."""
    services = set()
    for path in file_paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for services_name in (data or {}).get("services", {}).keys():
            services.add(services_name)
    return services


def get_profiles(file_paths: list[Path]) -> set[str]:
    """Extract unique docker-compose profile names out of given YAML paths."""
    profiles = set()
    for path in file_paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for service in (data or {}).get("services", {}).values():
            for p in (service or {}).get("profiles", []):
                profiles.add(p)
    return profiles


def get_compose_file_paths(path: Path | None = None) -> list[Path]:
    path: Path = path or Path.cwd()
    return [*path.glob("*compose*.yml"), *path.glob("*compose*.yaml")]
