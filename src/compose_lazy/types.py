from typing import TypedDict


class RepoConfig(TypedDict):
    files: list[str]


class WorkspaceConfig(TypedDict):
    repos: dict[str, RepoConfig]


class ComposeLazyConfig(TypedDict):
    workspaces: dict[str, WorkspaceConfig]
