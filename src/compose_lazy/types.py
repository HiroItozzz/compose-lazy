from typing import TypeAlias, TypedDict


class RepoConfig(TypedDict):
    files: list[str]


RepoPaths: TypeAlias = dict[str, RepoConfig]  # {path: {"files": [yaml_files]}}
WorkspaceConfig: TypeAlias = dict[str, RepoPaths]  # {workspace_name: RepoPaths}


class ComposeLazyConfig(TypedDict):
    workspaces: WorkspaceConfig
