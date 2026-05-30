import subprocess
from argparse import Namespace
from unittest.mock import MagicMock, patch

import pytest

from fast_dcp.workspace import (
    AbstractWsExecutor,
    WorkspaceExecutor,
    WorkspaceRegistrar,
)


class TestWsBase:
    def setup_method(self):
        with patch.object(AbstractWsExecutor, "__init__", return_value=None):
            self.registrar = WorkspaceRegistrar.__new__(WorkspaceRegistrar)
            self.executor = WorkspaceExecutor.__new__(WorkspaceExecutor)

        self.registrar.handler = MagicMock()
        self.executor.handler = MagicMock()


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
    def test_call(self, ws_subcmd, expected_method, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(return_value=0)
        )
        monkeypatch.setattr(WorkspaceRegistrar, "delete_repo", MagicMock(return_value=0))
        monkeypatch.setattr(WorkspaceRegistrar, "show_list", MagicMock(return_value=0))

        args = Namespace(ws_subcmd=ws_subcmd)
        self.registrar(args)

        getattr(WorkspaceRegistrar, expected_method).assert_called_once()

    def test_call_KEYBOARD_INTERRUPT(self, capsys, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(side_effect=KeyboardInterrupt)
        )
        args = Namespace(ws_subcmd="register")
        code = self.registrar(args)

        out, _ = capsys.readouterr()
        assert "\nCancelled." in out
        assert code == 130

    def test_call_SYSTEM_EXIT(self, monkeypatch):
        monkeypatch.setattr(
            WorkspaceRegistrar, "register_repo", MagicMock(side_effect=SystemExit)
        )
        args = Namespace(ws_subcmd="register")
        code = self.registrar(args)

        assert code == 0


class TestShowList(TestWsBase):
    def test_NO_WORKSPACES(self, capsys):
        self.registrar.handler.config = {"workspaces": {}}
        code = self.registrar.show_list()

        out, _ = capsys.readouterr()
        assert "No workspaces registered yet." in out
        assert code == 1

    def test_WITH_WORKSPACES(self, capsys):
        self.registrar.handler.config = {
            "workspaces": {
                "ws1": ["/path/to/repo1", "/path/to/repo2"],
            }
        }
        code = self.registrar.show_list()

        out, _ = capsys.readouterr()
        assert "ws1" in out
        assert "/path/to/repo1" in out
        assert code == 0

    def test_EMPTY_WORKSPACE(self, capsys):
        self.registrar.handler.config = {"workspaces": {"ws1": []}}
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

    def test_VALID_PATH_NEW(self, capsys, monkeypatch, tmp_path):
        self.registrar.handler.config = {"workspaces": {}}
        self.registrar.handler.append_value = MagicMock(return_value=True)
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_name",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value=str(tmp_path)))

        code = self.registrar.register_repo()

        out, _ = capsys.readouterr()
        assert "☑ Registered new path" in out
        self.registrar.handler.dump_and_write.assert_called_once()
        assert code == 0

    def test_VALID_PATH_DUPLICATE(self, capsys, monkeypatch, tmp_path):
        self.registrar.handler.config = {"workspaces": {}}
        self.registrar.handler.append_value = MagicMock(return_value=False)
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_name",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value=str(tmp_path)))

        code = self.registrar.register_repo()

        _, err = capsys.readouterr()
        assert "already in" in err
        self.registrar.handler.dump_and_write.assert_not_called()
        assert code == 0


class TestDeleteRepo(TestWsBase):
    def test_NO_WORKSPACES(self, capsys):
        self.registrar.handler.config = {"workspaces": {}}
        code = self.registrar.delete_repo()

        _, err = capsys.readouterr()
        assert "No workspaces registered yet." in err
        assert code == 1

    def test_DELETE(self, capsys, monkeypatch):
        workspaces = {"ws1": ["/path/to/repo1", "/path/to/repo2"]}
        self.registrar.handler.config = {"workspaces": workspaces}
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_name",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value="1"))

        code = self.registrar.delete_repo()

        out, _ = capsys.readouterr()
        assert "☑ Deleted" in out
        self.registrar.handler.dump_and_write.assert_called_once()
        assert code == 0

    def test_DELETE_ALL_REMOVES_WORKSPACE(self, monkeypatch):
        workspaces = {"ws1": ["/path/to/repo1"]}
        self.registrar.handler.config = {"workspaces": workspaces}
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_name",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(return_value="1"))

        self.registrar.delete_repo()

        assert "ws1" not in self.registrar.handler.config["workspaces"]


    def test_DELETE_OUT_OF_RANGE(self, capsys, monkeypatch):
        workspaces = {"ws1": ["/path/to/repo1", "/path/to/repo2"]}
        self.registrar.handler.config = {"workspaces": workspaces}
        self.registrar.handler.dump_and_write = MagicMock()
        monkeypatch.setattr(
            WorkspaceRegistrar,
            "_select_workspace_name",
            MagicMock(return_value="ws1"),
        )
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=["3", "1"]))

        self.registrar.delete_repo()

        _, err = capsys.readouterr()
        assert "Invalid selection" in err


# ─────────────────────────────────────────────
# WorkspaceExecutor
# ─────────────────────────────────────────────


class TestExecutorCall(TestWsBase):
    def setup_method(self):
        super().setup_method()
        self.executor.get_target_workspace = MagicMock(return_value=["/path/to/repo"])
        self.executor._execute_command = MagicMock(return_value=0)

    @pytest.mark.parametrize(
        "ws_subcmd,expected_cmd",
        [
            ("up", ["docker", "compose", "up", "-d"]),
            ("u", ["docker", "compose", "up", "-d"]),
            ("restart", ["docker", "compose", "restart"]),
            ("re", ["docker", "compose", "restart"]),
            ("stop", ["docker", "compose", "stop"]),
            ("s", ["docker", "compose", "stop"]),
            ("down", ["docker", "compose", "down"]),
        ],
    )
    def test_call(self, ws_subcmd, expected_cmd):
        args = Namespace(ws_subcmd=ws_subcmd)
        code = self.executor(args)

        self.executor._execute_command.assert_called_once_with(
            expected_cmd, "/path/to/repo"
        )
        assert code == 0

    def test_call_KEYBOARD_INTERRUPT(self, capsys):
        self.executor.get_target_workspace = MagicMock(side_effect=KeyboardInterrupt)
        args = Namespace(ws_subcmd="up")
        with pytest.raises(SystemExit) as exc_info:
            self.executor(args)

        out, _ = capsys.readouterr()
        assert "\nCancelled." in out
        assert exc_info.value.code == 130

    def test_returns_nonzero_on_failure(self):
        self.executor._execute_command = MagicMock(side_effect=[0, 1, 0])
        self.executor.get_target_workspace = MagicMock(
            return_value=["/repo1", "/repo2", "/repo3"]
        )
        args = Namespace(ws_subcmd="up")
        code = self.executor(args)

        assert code == 1


class TestExecuteCommand(TestWsBase):
    def test_execute_command(self, capsys):
        result = MagicMock()
        result.returncode = 0
        subprocess.run = MagicMock(return_value=result)

        code = self.executor._execute_command(
            ["docker", "compose", "up", "-d"], "/path/to/repo"
        )

        subprocess.run.assert_called_once_with(
            ["docker", "compose", "up", "-d"], cwd="/path/to/repo"
        )
        assert code == 0


class TestGetTargetWorkspace(TestWsBase):
    def test_get_target_workspace(self, monkeypatch):
        workspaces = {"ws1": ["/repo1", "/repo2"]}
        self.executor.handler.config = {"workspaces": workspaces}
        monkeypatch.setattr(
            WorkspaceExecutor,
            "_select_workspace_name",
            MagicMock(return_value="ws1"),
        )

        result = self.executor.get_target_workspace()

        assert result == ["/repo1", "/repo2"]


# ─────────────────────────────────────────────
# AbstractWsExecutor._select_workspace_name
# ─────────────────────────────────────────────


class TestSelectWorkspaceName(TestWsBase):
    cases_number = (
        ("1\n", {"ws1": [], "ws2": []}, True, "ws1"),
        ("2\n", {"ws1": [], "ws2": []}, True, "ws2"),
        ("3\n1\n", {"ws1": [], "ws2": []}, True, "ws1"),  # invalid then valid
        ("3\n1\n", {"ws1": [], "ws2": []}, False, "ws1"),  # allow_add=False
    )

    @pytest.mark.parametrize("keys,workspace_dict,allow_add,expected", cases_number)
    def test_number_input(self, keys, workspace_dict, allow_add, expected, monkeypatch):
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO(keys))
        result = self.registrar._select_workspace_name(
            workspace_dict, allow_add=allow_add
        )
        assert result == expected

    def test_string_input_allow_add(self, monkeypatch):
        """Return the string as a new workspace name when allow_add=True."""
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO("new_ws\n"))
        result = self.registrar._select_workspace_name({"ws1": []}, allow_add=True)
        assert result == "new_ws"

    def test_string_input_not_allow_add(self, capsys, monkeypatch):
        """Show error message on string input when allow_add=False, then accept a valid number."""
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO("abc\n1\n"))
        result = self.registrar._select_workspace_name({"ws1": []}, allow_add=False)
        _, err = capsys.readouterr()
        assert "Invalid selection" in err
        assert result == "ws1"

    def test_empty_workspace_dict(self, monkeypatch):
        """Return the string as a new workspace name when workspace_dict is empty."""
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO("new_ws\n"))
        result = self.registrar._select_workspace_name({}, allow_add=True)
        assert result == "new_ws"

    def test_single_workspace_message(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO("1\n"))
        self.registrar._select_workspace_name({"ws1": []})
        out, _ = capsys.readouterr()
        assert "Found 1 registered workspace." in out

    def test_multiple_workspaces_message(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.stdin", __import__("io").StringIO("1\n"))
        self.registrar._select_workspace_name({"ws1": [], "ws2": []})
        out, _ = capsys.readouterr()
        assert "Found 2 registered workspaces." in out
