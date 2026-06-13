import subprocess
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import pytest

import compose_lazy.workspace
from compose_lazy import utils
from compose_lazy.utils import YamlHandler
from compose_lazy.workspace import (
    WorkspaceProcessor,
    WorkspaceRegistrar,
)


class TestWsBase:
    def setup_method(self):
        self.registrar = WorkspaceRegistrar()
        self.processor = WorkspaceProcessor()


# ─────────────────────────────────────────────
# AbstractWsExecutor
# ─────────────────────────────────────────────


class TestCommonMethods(TestWsBase):
    def test_call(self, monkeypatch):
        monkeypatch.setattr(YamlHandler, "setup_config", MagicMock())
        monkeypatch.setattr(WorkspaceRegistrar, "_migrate_workspace_schema", MagicMock())
        monkeypatch.setattr(WorkspaceRegistrar, "_switch", MagicMock(return_value=0))
        args = Namespace(subcmd="ws", ws_subcmd="test")
        code = self.registrar(args)

        getattr(YamlHandler, "setup_config").assert_called_once_with("workspaces")
        getattr(WorkspaceRegistrar, "_migrate_workspace_schema").assert_called_once()
        getattr(WorkspaceRegistrar, "_switch").assert_called_once_with(args)
        assert code == 0

    def test_select_or_create_NO_WORKSPACES(self, monkeypatch):
        mock_input = MagicMock(return_value="ws1")
        monkeypatch.setattr("builtins.input", mock_input)
        workspaces = {}
        result = self.registrar._select_workspace_or_create(workspaces)

        mock_input.assert_called_once()
        assert result == "ws1"

    def test_select_or_create_WORKSPACE_EXISTS(self, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_display_intro",
            MagicMock(),
        )
        monkeypatch.setattr(
            utils,
            "interactive_select",
            MagicMock(return_value=["ws2"]),
        )
        workspaces = {"ws1": [], "ws2": []}
        result = self.registrar._select_workspace_or_create(workspaces)

        WorkspaceRegistrar._display_intro.assert_called_once()
        getattr(utils, "interactive_select").assert_called_once_with(
            list(workspaces), multiple=False, allow_zero=True
        )
        assert result == "ws2"

    def test_select_or_create_WORKSPACE_EXISTS_AND_SELECT_0(self, monkeypatch):
        mock_input = MagicMock(return_value="ws99")
        monkeypatch.setattr("builtins.input", mock_input)
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_display_intro",
            MagicMock(),
        )
        monkeypatch.setattr(
            utils,
            "interactive_select",
            MagicMock(return_value=None),
        )
        prompt = "Enter a new workspace name: "
        workspaces = {"ws1": [], "ws2": []}
        result = self.registrar._select_workspace_or_create(workspaces)

        WorkspaceRegistrar._display_intro.assert_called_once()
        getattr(utils, "interactive_select").assert_called_once_with(
            list(workspaces), multiple=False, allow_zero=True
        )
        mock_input.assert_called_once_with(prompt)
        assert result == "ws99"

    def test_select_simply(self, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_display_intro",
            MagicMock(),
        )
        monkeypatch.setattr(
            utils,
            "interactive_select",
            MagicMock(return_value=["ws2"]),
        )
        workspaces = {"ws1": [], "ws2": []}
        result = self.registrar._select_workspace_simply(workspaces)

        WorkspaceRegistrar._display_intro.assert_called_once()
        utils.interactive_select.assert_called_once_with(list(workspaces), multiple=False)
        assert result == "ws2"

    def test_select_simply_no_interaction(self, monkeypatch):
        monkeypatch.setattr(WorkspaceRegistrar, "_display_intro", MagicMock())
        monkeypatch.setattr(utils, "interactive_select", MagicMock())
        result = self.registrar._select_workspace_simply({"ws1": {}})

        WorkspaceRegistrar._display_intro.assert_not_called()
        utils.interactive_select.assert_not_called()
        assert result == "ws1"

    def test_select_simply_returns_None(self, monkeypatch):
        monkeypatch.setattr(WorkspaceRegistrar, "_display_intro", MagicMock())
        monkeypatch.setattr(utils, "interactive_select", MagicMock())
        result = self.registrar._select_workspace_simply({})

        WorkspaceRegistrar._display_intro.assert_not_called()
        utils.interactive_select.assert_not_called()
        assert result is None

    def test_display_intro_LENGTH_IS_1(self, capsys):
        workspaces = {"ws1": []}
        self.registrar._display_intro(workspaces)

        out, _ = capsys.readouterr()
        assert "Found 1 registered workspace" in out

    def test_display_intro_LENGTH_OVER_2(self, capsys):
        workspaces = {"ws1": [], "ws2": []}
        self.registrar._display_intro(workspaces)

        out, _ = capsys.readouterr()
        assert "Found 2 registered workspaces" in out


SAMPLE_CONFIG_v0_8_0 = """workspaces:
  ws1:
    /path/to/repo1:
    - compose.test1.yml
    - compose.test11.yml
  ws2:
    /path/to/repo2:
    - compose.test2.yml"""

SAMPLE_CONFIG_v0_9_2 = """workspaces:
  ws1:
    /path/to/repo1:
      files:
        - compose.test1.yml
        - compose.test11.yml
  ws2:
    /path/to/repo2:
      files:
        - compose.test2.yml
"""


SAMPLE_CONFIG_v0_9_3 = """workspaces:
  ws1:
    repos:
      /path/to/repo1:
        files:
        - compose.test1.yml
        - compose.test11.yml
  ws2:
    repos:
      /path/to/repo2:
        files:
        - compose.test2.yml
"""


class TestMigration:
    @pytest.mark.parametrize(
        "config,expected",
        [
            (SAMPLE_CONFIG_v0_8_0, True),
            (SAMPLE_CONFIG_v0_9_2, True),
            (SAMPLE_CONFIG_v0_9_3, False),
        ],
    )
    def test_migration(self, config, expected, tmp_path, monkeypatch):
        test_config_path = tmp_path / "test_config"
        test_config_path.write_text(config)
        monkeypatch.setattr(compose_lazy.workspace, "CONFIG_PATH", test_config_path)
        monkeypatch.setattr(YamlHandler, "dump_and_write", (mock_write := MagicMock()))
        registrar = WorkspaceRegistrar()
        registrar.handler._config = registrar.handler._read_and_load()
        expected_config = {
            "workspaces": {
                "ws1": {
                    "repos": {
                        "/path/to/repo1": {
                            "files": ["compose.test1.yml", "compose.test11.yml"]
                        }
                    }
                },
                "ws2": {"repos": {"/path/to/repo2": {"files": ["compose.test2.yml"]}}},
            }
        }

        result = registrar._migrate_workspace_schema()

        assert result is expected
        assert mock_write.call_count == expected
        assert registrar.handler.config == expected_config


# ─────────────────────────────────────────────
# WorkspaceRegistrar
# ─────────────────────────────────────────────


class TestRegistrarCall(TestWsBase):
    @pytest.mark.parametrize(
        "ws_subcmd,expected_method",
        [
            ("register", "register_repo"),
            ("reg", "register_repo"),
            ("delete", "delete_repo"),
            ("del", "delete_repo"),
            ("list", "show_list"),
            ("li", "show_list"),
        ],
    )
    def test_switch(self, ws_subcmd, expected_method, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(return_value=0)
        )
        monkeypatch.setattr(WorkspaceRegistrar, "delete_repo", MagicMock(return_value=0))
        monkeypatch.setattr(WorkspaceRegistrar, "show_list", MagicMock(return_value=0))

        args = Namespace(ws_subcmd=ws_subcmd)
        self.registrar._switch(args)

        getattr(WorkspaceRegistrar, expected_method).assert_called_once()


class TestShowList(TestWsBase):
    def test_NO_WORKSPACES(self, capsys):
        self.registrar.handler._config = {"workspaces": {}}
        code = self.registrar.show_list()

        out, err = capsys.readouterr()
        assert "No workspaces" in err
        assert "dcp ws register(reg)" in out
        assert code == 1

    def test_WITH_WORKSPACES(self, capsys):
        self.registrar.handler._config = {
            "workspaces": {
                "ws1": {
                    "repos": {
                        "/path/to/repo1": {"files": ["compose1.yml"]},
                        "/path/to/repo2": {"files": ["compose2.yml"]},
                    }
                },
            }
        }
        code = self.registrar.show_list()

        out, _ = capsys.readouterr()
        assert "ws1" in out
        assert "/path/to/repo1" in out
        assert "compose2.yml" in out
        assert code == 0

    def test_EMPTY_WORKSPACE(self, capsys):
        self.registrar.handler._config = {"workspaces": {"ws1": {"repos": {}}}}
        code = self.registrar.show_list()

        out, _ = capsys.readouterr()
        assert "No repos registered yet." in out
        assert code == 0


class TestRegisterRepo(TestWsBase):
    def test_INVALID_PATH(self, capsys, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "builtins.input", MagicMock(return_value=str(tmp_path / "nonexistent"))
        )
        code = self.registrar.register_repo()

        _, err = capsys.readouterr()
        assert "❌ The path doesn't exists" in err
        assert code == 1

    @pytest.mark.parametrize(
        "selected_yamls",
        [["compose.test.yml"], ["compose.test.yaml", "compose.test2.yml"]],
    )
    def test_VALID_PATH_NEW(self, selected_yamls, capsys, monkeypatch, tmp_path):
        self.registrar.handler._config = {"workspaces": {}}
        self.registrar.handler.append_value = MagicMock(return_value=True)
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            utils, "get_file_choices", MagicMock(return_value=selected_yamls)
        )
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_or_create",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value=str(tmp_path)))

        code = self.registrar.register_repo()

        out, _ = capsys.readouterr()
        assert "Registered" in out
        assert str(tmp_path) in out
        assert all((f in out for f in selected_yamls))
        self.registrar.handler.dump_and_write.assert_called()
        utils.get_file_choices.assert_called_once_with(tmp_path)
        assert code == 0

    def test_VALID_PATH_DUPLICATE(self, capsys, monkeypatch, tmp_path):
        (tmp_path / "compose.test.yml").touch()
        self.registrar.handler._config = {"workspaces": {}}
        self.registrar.handler.append_value = MagicMock(return_value=False)
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            utils, "get_file_choices", MagicMock(return_value=["compose.test.yml"])
        )
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_or_create",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value=str(tmp_path)))

        code = self.registrar.register_repo()

        _, err = capsys.readouterr()
        assert "already in" in err
        assert "compose.test.yml" in err
        self.registrar.handler.dump_and_write.assert_not_called()
        assert code == 0

    def test_VALID_PATH_SELECT_ZERO_SHOW_LIST(self, capsys, monkeypatch, tmp_path):
        ws_1 = {"ws1": {"path": {"files": ["compose.yml"]}}}
        ws_2 = {"ws_new": {str(tmp_path): {"files": ["compose.test.yml"]}}}
        config_before = {"workspaces": ws_1}
        config_after = {"workspaces": ws_1 | ws_2}

        monkeypatch.setattr(
            WorkspaceRegistrar,
            "config",
            PropertyMock(side_effect=[config_after, config_after]),
        )

        self.registrar.handler.append_value = MagicMock(return_value=True)
        monkeypatch.setattr(YamlHandler, "dump_and_write", mock_dump := MagicMock())
        mock_input = MagicMock(side_effect=[str(tmp_path), "ws_new", "l"])
        monkeypatch.setattr("builtins.input", mock_input)
        monkeypatch.setattr(
            utils,
            "interactive_select",
            MagicMock(return_value=None),
        )
        monkeypatch.setattr(
            utils, "get_file_choices", MagicMock(return_value=["compose.test.yml"])
        )
        monkeypatch.setattr(
            WorkspaceRegistrar, "show_list", mock_show_list := MagicMock()
        )

        code = self.registrar.register_repo()

        out, _ = capsys.readouterr()
        assert "Registered" in out
        assert "compose.test.yml" in out
        mock_dump.assert_called_once()
        mock_show_list.assert_called_once()
        assert code == 0

    def test_HINT_ALWAYS_PRINTED(self, capsys, monkeypatch, tmp_path):
        self.registrar.handler._config = {"workspaces": {}}
        self.registrar.handler.append_value = MagicMock(return_value=True)
        self.registrar.handler.dump_and_write = MagicMock()

        monkeypatch.setattr(
            utils, "get_file_choices", MagicMock(return_value=["compose.test.yml"])
        )
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_or_create",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value=str(tmp_path)))

        self.registrar.register_repo()

        out, _ = capsys.readouterr()
        assert "dcp ws list(li)" in out


class TestDeleteRepo(TestWsBase):
    def test_NO_WORKSPACES(self, capsys):
        self.registrar.handler._config = {"workspaces": {}}
        code = self.registrar.delete_repo()

        _, err = capsys.readouterr()
        assert "No workspaces registered yet." in err
        assert code == 1

    def test_DELETE(self, capsys, monkeypatch):
        workspaces = {
            "ws1": {
                "repos": {
                    "/path/to/repo1": {"files": ["compose1.yml"]},
                    "/path/to/repo2": {"files": ["compose2.yml"]},
                }
            },
        }
        self.registrar.handler._config = {"workspaces": workspaces}
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_simply",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value="1"))

        code = self.registrar.delete_repo()

        out, _ = capsys.readouterr()
        assert "✅️ Deleted" in out
        self.registrar.handler.dump_and_write.assert_called_once()
        assert code == 0

    def test_DELETE_ALL_REMOVES_WORKSPACE(self, monkeypatch):
        workspaces = {
            "ws1": {
                "repos": {
                    "/path/to/repo1": {"files": ["compose1.yml"]},
                }
            }
        }
        self.registrar.handler._config = {"workspaces": workspaces}
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_simply",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value="1"))

        self.registrar.delete_repo()

        assert "ws1" not in self.registrar.handler.config["workspaces"]

    @pytest.mark.parametrize("commands", [("3", "1"), ("0", "1"), ("-1", "1")])
    def test_DELETE_OUT_OF_RANGE(self, commands, capsys, monkeypatch):
        workspaces = {
            "ws1": {
                "repos": {
                    "/path/to/repo1": {"files": ["compose1.yml"]},
                    "/path/to/repo2": {"files": ["compose2.yml"]},
                },
            }
        }
        self.registrar.handler._config = {"workspaces": workspaces}
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_simply",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=commands))

        self.registrar.delete_repo()

        _, err = capsys.readouterr()
        assert "Invalid selection" in err


# ─────────────────────────────────────────────
# WorkspaceExecutor
# ─────────────────────────────────────────────


class TestProcessorCall(TestWsBase):
    def setup_method(self):
        super().setup_method()
        self.compose_files = ["compose.test.yml", "compose.test2.yml"]
        self.workspace = {"repos": {"/path/to/repo": {"files": self.compose_files}}}
        self.processor.get_target_workspace = MagicMock(return_value=self.workspace)
        self.processor._execute_command = MagicMock(return_value=0)

    def test_call(self, monkeypatch):
        monkeypatch.setattr(YamlHandler, "setup_config", MagicMock())
        monkeypatch.setattr(WorkspaceProcessor, "_switch", MagicMock(return_value=0))
        args = Namespace(subcmd="ws", ws_subcmd="test")
        code = self.processor(args)

        getattr(YamlHandler, "setup_config").assert_called_once_with("workspaces")
        getattr(WorkspaceProcessor, "_switch").assert_called_once_with(args)
        assert code == 0

    @pytest.mark.parametrize(
        "ws_subcmd,executed_subcommand",
        [
            ("up", ["up", "-d"]),
            ("u", ["up", "-d"]),
            ("build", ["build"]),
            ("b", ["build"]),
            ("ps", ["ps"]),
            ("restart", ["restart"]),
            ("re", ["restart"]),
            ("stop", ["stop"]),
            ("s", ["stop"]),
            ("down", ["down"]),
        ],
    )
    def test_switch(self, ws_subcmd, executed_subcommand, monkeypatch):
        monkeypatch.setattr(WorkspaceProcessor, "_iterate_execution", MagicMock())
        args = Namespace(ws_subcmd=ws_subcmd)
        self.processor._switch(args)

        self.processor._iterate_execution.assert_called_once_with(
            executed_subcommand, self.workspace
        )

    @pytest.mark.parametrize(
        "ws_subcmd,expected_method",
        [
            ("exec", "_get_exec_details"),
            ("e", "_get_exec_details"),
            ("logs", "_get_logs_details"),
            ("lo", "_get_logs_details"),
        ],
    )
    def test_switch_exec(self, ws_subcmd, expected_method, monkeypatch):
        monkeypatch.setattr(
            WorkspaceProcessor,
            expected_method,
            MagicMock(return_value=(["test"], {"repos": {"ws1": {}}})),
        )
        monkeypatch.setattr(WorkspaceProcessor, "_iterate_execution", MagicMock())
        args = Namespace(ws_subcmd=ws_subcmd)
        self.processor._switch(args)

        getattr(self.processor, expected_method).assert_called_once_with(self.workspace)
        self.processor._iterate_execution.assert_called_once_with(
            ["test"], {"repos": {"ws1": {}}}
        )

    def test_switch_returns_1(self, monkeypatch):
        self.processor.get_target_workspace = MagicMock(return_value=None)
        monkeypatch.setattr(WorkspaceProcessor, "_iterate_execution", MagicMock())
        args = Namespace(ws_subcmd="up")
        code = self.processor._switch(args)

        assert code == 1
        self.processor._iterate_execution.assert_not_called()

    def test_iterate_execution(self, monkeypatch):
        subcommand = ["up", "-d"]
        base_command = ["docker", "compose"]
        file_args = ["-f", "compose.test.yml", "-f", "compose.test2.yml"]
        expected_command = base_command + file_args + subcommand

        monkeypatch.setattr(Path, "is_dir", MagicMock(return_value=True))
        monkeypatch.setattr(Path, "exists", MagicMock(return_value=True))
        mock_formatter = MagicMock(return_value=file_args)
        monkeypatch.setattr(utils, "format_as_flag_args", mock_formatter)

        code = self.processor._iterate_execution(subcommand, self.workspace)

        utils.format_as_flag_args.assert_called_once_with(self.compose_files, "-f")
        self.processor._execute_command.assert_called_once_with(
            expected_command, "/path/to/repo"
        )
        assert code == 0

    def test_iterate_execution_path_NOT_exists(self, capsys, monkeypatch):
        monkeypatch.setattr(Path, "is_dir", MagicMock(return_value=False))

        code = self.processor._iterate_execution(["up"], self.workspace)
        _, err = capsys.readouterr()

        self.processor._execute_command.assert_not_called()
        assert "directory not found" in err
        assert code == 1

    def test_returns_nonzero_on_failure(self):
        self.processor._execute_command = MagicMock(side_effect=[0, 1, 0])
        workspace = {
            "repos": {
                "/repo1": {"files": ["compose1.yml"]},
                "/repo2": {"files": ["compose1.yml"]},
                "/repo3": {"files": ["compose1.yml"]},
            }
        }
        code = self.processor._iterate_execution(["up"], workspace)

        assert code == 1

    def test_Docker_NOT_FOUND(self, capsys, tmp_path):
        (tmp_path / "compose.yml").touch()
        workspace = {"repos": {str(tmp_path): {"files": ["compose.yml"]}}}
        self.processor._execute_command = MagicMock(side_effect=FileNotFoundError)

        code = self.processor._iterate_execution(["up"], workspace)

        _, err = capsys.readouterr()
        assert "Docker is not found." in err
        assert code == 1

    def test_switch_MISSING_COMPOSE_FILE(self, capsys, monkeypatch):
        monkeypatch.setattr(Path, "is_dir", MagicMock(return_value=True))
        monkeypatch.setattr(Path, "exists", MagicMock(return_value=False))
        args = Namespace(ws_subcmd="up")
        code = self.processor._switch(args)

        _, err = capsys.readouterr()
        assert "❌ Compose file not found" in err
        assert code == 1
        self.processor._execute_command.assert_not_called()

    def test_UNEXPECTED_ERROR(self, capsys):
        self.processor.get_target_workspace = MagicMock(side_effect=RuntimeError)
        args = Namespace(ws_subcmd="up")
        code = self.processor(args)

        _, err = capsys.readouterr()
        assert "An unexpected error occurred." in err
        assert code == 1


class TestExecuteCommand(TestWsBase):
    def test_execute_command(self, capsys):
        result = MagicMock()
        result.returncode = 0
        subprocess.run = MagicMock(return_value=result)

        code = self.processor._execute_command(
            ["docker", "compose", "up", "-d"], "/path/to/repo"
        )

        subprocess.run.assert_called_once_with(
            ["docker", "compose", "up", "-d"], cwd="/path/to/repo"
        )
        assert code == 0


class TestGetTargetWorkspace(TestWsBase):
    def test_get_target_workspace(self, monkeypatch):
        workspaces = {"ws1": {"/repo1": "test.yml"}, "ws2": {"/repo2": "test2.yml"}}
        self.processor.handler._config = {"workspaces": workspaces}
        monkeypatch.setattr(
            WorkspaceProcessor,
            "_select_workspace_simply",
            MagicMock(return_value="ws1"),
        )

        result = self.processor.get_target_workspace()

        assert result == {"/repo1": "test.yml"}

    def test_returns_None(self, monkeypatch):
        workspaces = {"ws1": {"/repo1": "", "/repo2": ""}}
        self.processor.handler._config = {"workspaces": workspaces}
        monkeypatch.setattr(
            WorkspaceProcessor,
            "_select_workspace_simply",
            MagicMock(return_value=None),
        )

        result = self.processor.get_target_workspace()

        assert result is None


class TestGetExecDetails(TestWsBase):
    def test_get_exec_details(self, capsys, tmp_path_factory, monkeypatch):
        dir1 = tmp_path_factory.mktemp("dir1")
        dir2 = tmp_path_factory.mktemp("dir2")
        content1 = "services:\n  app:\n  db:"
        content2 = "services:\n  db:\n  frontend:"
        (dir1 / "compose1.yml").write_text(content1)
        (dir2 / "compose2.yml").write_text(content2)
        workspace = {
            "repos": {
                str(dir1): {"files": ["compose1.yml"]},
                str(dir2): {"files": ["compose2.yml"]},
            }
        }
        dir2_services = {"db", "frontend"}

        mock_repo = MagicMock(return_value=str(dir2))
        monkeypatch.setattr(WorkspaceProcessor, "_select_repo", mock_repo)
        mock_select = MagicMock(return_value=["db"])
        monkeypatch.setattr(utils, "interactive_select", mock_select)
        mock_get_service = MagicMock(return_value=dir2_services)
        monkeypatch.setattr(utils, "get_service_from_yamls", mock_get_service)
        mock_input = MagicMock(return_value="psql")
        monkeypatch.setattr("builtins.input", mock_input)

        expected_cmd = ["exec", "db", "psql"]
        expected_workspace = {"repos": {str(dir2): {"files": ["compose2.yml"]}}}

        result = self.processor._get_exec_details(workspace=workspace)
        out, _ = capsys.readouterr()

        mock_repo.assert_called_once_with(workspace["repos"])
        mock_get_service.assert_called_once_with([dir2 / "compose2.yml"])
        assert "services!" in out
        mock_select.assert_called_once_with(dir2_services, multiple=False)

        assert result == (expected_cmd, expected_workspace)

    def test_no_selection_empty_input(self, capsys, tmp_path_factory, monkeypatch):
        dir1 = tmp_path_factory.mktemp("dir1")
        content1 = "services:\n  app:"
        (dir1 / "compose1.yml").write_text(content1)
        workspace = {"repos": {str(dir1): {"files": ["compose1.yml"]}}}
        dir1_services = {"app"}

        mock_repo = MagicMock(return_value=str(dir1))
        monkeypatch.setattr(WorkspaceProcessor, "_select_repo", mock_repo)
        mock_select = MagicMock()
        monkeypatch.setattr(utils, "interactive_select", mock_select)
        mock_get_service = MagicMock(return_value=dir1_services)
        monkeypatch.setattr(utils, "get_service_from_yamls", mock_get_service)
        mock_input = MagicMock(return_value="")
        monkeypatch.setattr("builtins.input", mock_input)

        expected_cmd = ["exec", "app", "bash"]
        expected_workspace = {"repos": {str(dir1): {"files": ["compose1.yml"]}}}

        result = self.processor._get_exec_details(workspace=workspace)
        out, _ = capsys.readouterr()

        assert "services!" not in out
        assert "Found" not in out
        mock_repo.assert_called_once_with(workspace["repos"])
        mock_get_service.assert_called_once_with([dir1 / "compose1.yml"])

        utils.interactive_select.assert_not_called()

        assert result == (expected_cmd, expected_workspace)

    def test_SystemExit(self, capsys, tmp_path_factory, monkeypatch):
        dir1 = tmp_path_factory.mktemp("dir1")
        content1 = "services:"
        (dir1 / "compose1.yml").write_text(content1)
        workspace = {"repos": {str(dir1): {"files": ["compose1.yml"]}}}

        mock_get_service = MagicMock(return_value={})
        monkeypatch.setattr(utils, "get_service_from_yamls", mock_get_service)

        with pytest.raises(SystemExit):
            self.processor._get_exec_details(workspace=workspace)

        _, err = capsys.readouterr()

        assert "No services" in err


class TestGetLogsDetails(TestWsBase):
    def test_get_logs_details(self, capsys, tmp_path_factory, monkeypatch):
        dir1 = tmp_path_factory.mktemp("dir1")
        dir2 = tmp_path_factory.mktemp("dir2")
        content1 = "services:\n  app:\n  db:"
        content2 = "services:\n  db:\n  frontend:"
        (dir1 / "compose1.yml").write_text(content1)
        (dir2 / "compose2.yml").write_text(content2)
        workspace = {
            "repos": {
                str(dir1): {"files": ["compose1.yml"]},
                str(dir2): {"files": ["compose2.yml"]},
            }
        }
        dir2_services = {"db", "frontend"}

        mock_repo = MagicMock(return_value=str(dir2))
        monkeypatch.setattr(WorkspaceProcessor, "_select_repo", mock_repo)
        mock_select = MagicMock(return_value=["db", "frontend"])
        monkeypatch.setattr(utils, "interactive_select", mock_select)
        mock_get_service = MagicMock(return_value=dir2_services)
        monkeypatch.setattr(utils, "get_service_from_yamls", mock_get_service)

        expected_cmd = ["logs", "db", "frontend", "-f"]
        expected_workspace = {"repos": {str(dir2): {"files": ["compose2.yml"]}}}

        result = self.processor._get_logs_details(workspace=workspace)
        out, _ = capsys.readouterr()

        mock_repo.assert_called_once_with(workspace["repos"])
        mock_get_service.assert_called_once_with([dir2 / "compose2.yml"])
        assert "services!" in out
        mock_select.assert_called_once_with(dir2_services)

        assert result == (expected_cmd, expected_workspace)

    def test_no_selection_empty_input(self, capsys, tmp_path_factory, monkeypatch):
        dir1 = tmp_path_factory.mktemp("dir1")
        content1 = "services:\n  app:"
        (dir1 / "compose1.yml").write_text(content1)
        workspace = {"repos": {str(dir1): {"files": ["compose1.yml"]}}}
        dir1_services = {"app"}

        mock_repo = MagicMock(return_value=str(dir1))
        monkeypatch.setattr(WorkspaceProcessor, "_select_repo", mock_repo)
        monkeypatch.setattr(utils, "interactive_select", MagicMock())
        mock_get_service = MagicMock(return_value=dir1_services)
        monkeypatch.setattr(utils, "get_service_from_yamls", mock_get_service)

        expected_cmd = ["logs", "app", "-f"]
        expected_workspace = {"repos": {str(dir1): {"files": ["compose1.yml"]}}}

        result = self.processor._get_logs_details(workspace=workspace)
        out, _ = capsys.readouterr()

        assert "services!" not in out
        assert "Found" not in out
        mock_repo.assert_called_once_with(workspace["repos"])
        mock_get_service.assert_called_once_with([dir1 / "compose1.yml"])

        utils.interactive_select.assert_not_called()

        assert result == (expected_cmd, expected_workspace)

    def test_SystemExit(self, capsys, tmp_path_factory, monkeypatch):
        dir1 = tmp_path_factory.mktemp("dir1")
        content1 = "services:"
        (dir1 / "compose1.yml").write_text(content1)
        workspace = {"repos": {str(dir1): {"files": ["compose1.yml"]}}}

        mock_get_service = MagicMock(return_value={})
        monkeypatch.setattr(utils, "get_service_from_yamls", mock_get_service)

        with pytest.raises(SystemExit):
            self.processor._get_logs_details(workspace=workspace)

        _, err = capsys.readouterr()

        assert "No services" in err


class TestSelectRepo(TestWsBase):
    @pytest.mark.parametrize(
        "candidates,expected",
        [
            (["repo1"], "repo1"),
            ({"repo1": {"files": {}}}, "repo1"),
        ],
    )
    def test_length_1(self, candidates, expected):
        result = self.processor._select_repo(candidates)
        assert result == expected

    @pytest.mark.parametrize(
        "candidates,expected",
        [
            (["repo1", "repo2"], "repo2"),
            ({"repo1": {"files": {}}, "repo2": {"files": {}}}, "repo2"),
        ],
    )
    def test_length_2(self, candidates, expected, monkeypatch):
        monkeypatch.setattr(
            utils, "interactive_select", MagicMock(return_value=["repo2"])
        )
        result = self.processor._select_repo(candidates)

        utils.interactive_select.assert_called_once_with(list(candidates), multiple=False)
        assert result == expected
