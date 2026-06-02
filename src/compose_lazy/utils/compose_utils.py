import logging
from functools import lru_cache
from pathlib import Path

from .yaml_utils import YamlReader

logger = logging.getLogger(__name__)


def get_services(file_paths: list[Path]) -> set[str]:
    """Extract unique docker-compose service names out of given YAML paths."""
    services = set()
    for path in file_paths:
        reader = YamlReader(path).setup_config()
        for services_name in reader.get_values("services") or {}:
            services.add(services_name)
    return services


def get_profiles(file_paths: list[Path]) -> set[str]:
    """Extract unique docker-compose profile names out of given YAML paths."""
    profiles = set()
    for path in file_paths:
        reader = YamlReader(path).setup_config()
        for service_name in reader.get_values("services") or {}:
            for p in reader.get_values("services", service_name, "profiles") or []:
                profiles.add(p)
    return profiles


@lru_cache
def get_compose_file_paths(path: Path | None = None) -> list[Path]:
    path: Path = path or Path.cwd()
    return [*path.glob("*compose*.yml"), *path.glob("*compose*.yaml")]
