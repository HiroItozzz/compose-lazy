import subprocess
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock

import pytest

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
        monkeypatch.setattr(WorkspaceRegistrar, "_switch", MagicMock(return_value=0))
        args = Namespace(subcmd="ws", ws_subcmd="test")
        code = self.registrar(args)

        getattr(YamlHandler, "setup_config").assert_called_once_with("workspaces")
        getattr(WorkspaceRegistrar, "_switch").assert_called_once_with(args)
        assert code == 0

    def test_select_or_create_NO_WORKSPACES(self, monkeypatch):
        mock_input = MagicMock(return_value="ws1")
        monkeypatch.setattr("builtins.input", mock_input)
        prompt = "Please enter a new workspace name: "
        workspaces = {}
        result = self.registrar._select_workspace_or_create(workspaces)

        mock_input.assert_called_once_with(prompt)
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
        prompt = "Please enter a new workspace name: "
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

    def test_switch_TYPEERROR(self, capsys, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(side_effect=TypeError)
        )
        args = Namespace(ws_subcmd="register")
        code = self.registrar._switch(args)

        _, err = capsys.readouterr()
        assert "invalid or outdated" in err
        assert code == 1

    def test_switch_KEYBOARD_INTERRUPT(self, capsys, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(side_effect=KeyboardInterrupt)
        )
        args = Namespace(ws_subcmd="register")
        code = self.registrar._switch(args)

        out, _ = capsys.readouterr()
        assert "\nCancelled." in out
        assert code == 130

    def test_switch_SYSTEM_EXIT(self, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(side_effect=SystemExit)
        )
        args = Namespace(ws_subcmd="register")
        code = self.registrar._switch(args)

        assert code == 0

    def test_switch_EXCEPTION(self, capsys, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(side_effect=Exception)
        )
        args = Namespace(ws_subcmd="register")
        code = self.registrar._switch(args)

        _, err = capsys.readouterr()
        assert "unexpected error " in err
        assert code == 1


class TestShowList(TestWsBase):
    def test_NO_WORKSPACES(self, capsys):
        self.registrar.handler._config = {"workspaces": {}}
        code = self.registrar.show_list()

        out, _ = capsys.readouterr()
        assert "No workspaces registered yet." in out
        assert code == 1

    def test_WITH_WORKSPACES(self, capsys):
        self.registrar.handler._config = {
            "workspaces": {
                "ws1": {
                    "/path/to/repo1": ["compose1.yml"],
                    "/path/to/repo2": ["compose2.yml"],
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
        self.registrar.handler._config = {"workspaces": {"ws1": []}}
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
        assert "☑ Registered new path" in out
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

    def test_VALID_PATH_SELECT_ZERO(self, capsys, monkeypatch, tmp_path):
        self.registrar.handler._config = {"workspaces": {"ws1": []}}
        self.registrar.handler.append_value = MagicMock(return_value=True)
        self.registrar.handler.dump_and_write = MagicMock()
        mock_input = MagicMock(side_effect=[str(tmp_path), "ws_new"])
        monkeypatch.setattr("builtins.input", mock_input)
        monkeypatch.setattr(
            utils,
            "interactive_select",
            MagicMock(return_value=None),
        )
        monkeypatch.setattr(
            utils, "get_file_choices", MagicMock(return_value=["compose.test.yml"])
        )

        code = self.registrar.register_repo()

        out, _ = capsys.readouterr()
        assert "☑ Registered new path to ws_new" in out
        assert "compose.test.yml" in out
        self.registrar.handler.dump_and_write.assert_called_once()
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
        assert "💡 Hint" in out


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
                "/path/to/repo1": ["compose1.yml"],
                "/path/to/repo2": ["compose2.yml"],
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
        assert "☑ Deleted" in out
        self.registrar.handler.dump_and_write.assert_called_once()
        assert code == 0

    def test_DELETE_ALL_REMOVES_WORKSPACE(self, monkeypatch):
        workspaces = {
            "ws1": {
                "/path/to/repo1": ["compose1.yml"],
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
                "/path/to/repo1": ["compose1.yml"],
                "/path/to/repo2": ["compose2.yml"],
            },
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
        self.workspace = {"/path/to/repo": self.compose_files}
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
            "/repo1": ["compose1.yml"],
            "/repo2": ["compose1.yml"],
            "/repo3": ["compose1.yml"],
        }
        code = self.processor._iterate_execution(["up"], workspace)

        assert code == 1

    def test_Docker_NOT_FOUND(self, capsys, tmp_path):
        (tmp_path / "compose.yml").touch()
        workspace = {str(tmp_path): ["compose.yml"]}
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
        assert "❌️ Compose file not found" in err
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
        workspaces = {"ws1": ["/repo1", "/repo2"]}
        self.processor.handler._config = {"workspaces": workspaces}
        monkeypatch.setattr(
            WorkspaceProcessor,
            "_select_workspace_simply",
            MagicMock(return_value="ws1"),
        )

        result = self.processor.get_target_workspace()

        assert result == ["/repo1", "/repo2"]

    def test_returns_None(self, monkeypatch):
        workspaces = {"ws1": ["/repo1", "/repo2"]}
        self.processor.handler._config = {"workspaces": workspaces}
        monkeypatch.setattr(
            WorkspaceProcessor,
            "_select_workspace_simply",
            MagicMock(return_value=None),
        )

        result = self.processor.get_target_workspace()

        assert result is None
