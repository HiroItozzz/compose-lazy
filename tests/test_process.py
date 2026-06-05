import subprocess
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from compose_lazy import utils
from compose_lazy.process import DockerCmdProcessor as Processor


class TestDCPBase:
    def setup_method(self):
        self.processor = Processor()


class TestDCPSetup(TestDCPBase):
    def test_dcp_setup(self, monkeypatch):
        monkeypatch.setattr(
            Processor,
            "_create_common_compose_options",
            MagicMock(return_value=["test"]),
        )

        from compose_lazy.process import _BASE_CMD

        args = Namespace(test="result", project="", file="", profile="")
        self.processor._setup(args)

        assert self.processor.args == args
        assert self.processor.cmd == list(_BASE_CMD) + ["test"]
        Processor._create_common_compose_options.assert_called_once()


class TestProcessorCall(TestDCPBase):
    def setup_method(self):
        super().setup_method()
        self.processor._setup = MagicMock()
        self.processor._execute_command = MagicMock()

        self.processor._create_up_cmd = MagicMock()
        self.processor._create_build_cmd = MagicMock()
        self.processor._create_exec_cmd = MagicMock()
        self.processor._create_run_cmd = MagicMock()
        self.processor._create_restart_cmd = MagicMock()
        self.processor._create_ps_cmd = MagicMock()
        self.processor._create_logs_cmd = MagicMock()
        self.processor._create_stop_cmd = MagicMock()
        self.processor._create_down_cmd = MagicMock()

    @pytest.mark.parametrize(
        "subcmd,expected_method",
        [
            ("up", "_create_up_cmd"),
            ("u", "_create_up_cmd"),
            ("build", "_create_build_cmd"),
            ("b", "_create_build_cmd"),
            ("exec", "_create_exec_cmd"),
            ("e", "_create_exec_cmd"),
            ("run", "_create_run_cmd"),
            ("restart", "_create_restart_cmd"),
            ("re", "_create_restart_cmd"),
            ("ps", "_create_ps_cmd"),
            ("logs", "_create_logs_cmd"),
            ("l", "_create_logs_cmd"),
            ("stop", "_create_stop_cmd"),
            ("s", "_create_stop_cmd"),
            ("down", "_create_down_cmd"),
        ],
    )
    def test_instance_call(self, subcmd, expected_method):
        """test case for __call__ method with all match-case branches covered"""

        args = Namespace(subcmd=subcmd)
        self.processor(args)

        getattr(self.processor, "_setup").assert_called_once()
        getattr(self.processor, expected_method).assert_called_once()
        getattr(self.processor, "_execute_command").assert_called_once()

    def test_call_dcpu(self):
        args = Namespace()
        self.processor.call_dcpu(args)

        self.processor._setup.assert_called_once()
        self.processor._create_up_cmd.assert_called_once()
        self.processor._execute_command.assert_called_once()

    def test_call_dcpe(self):
        args = Namespace()
        self.processor.call_dcpe(args)

        self.processor._setup.assert_called_once()
        self.processor._create_exec_cmd.assert_called_once()
        self.processor._execute_command.assert_called_once()


class TestExecuteCommand(TestDCPBase):
    def test_execute_command(self):
        result = MagicMock()
        result.returncode = 1
        subprocess.run = MagicMock(return_value=result)

        test_cmd = ["docker", "compose up"]
        self.processor.cmd = test_cmd
        self.processor._execute_command()

        subprocess.run.assert_called_once_with(test_cmd)
        assert self.processor._execute_command() == 1

    def test_FILE_NOT_FOUND(self, capsys, monkeypatch):
        monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=FileNotFoundError))
        self.processor.cmd = ["docker", "compose", "up", "-d"]
        code = self.processor._execute_command()

        _, err = capsys.readouterr()
        assert "Docker is not found." in err
        assert code == 1

    def test_UNEXPECTED_ERROR(self, capsys, monkeypatch):
        monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=RuntimeError))
        self.processor.cmd = ["docker", "compose", "up", "-d"]
        code = self.processor._execute_command()

        _, err = capsys.readouterr()
        assert "An unexpected error occurred." in err
        assert code == 1


class TestAdjustServiceName(TestDCPBase):
    @pytest.mark.parametrize("service_name", [None, []])
    def test_NO_ARGS(self, service_name):
        self.processor.args.service_name = service_name
        self.processor.args.inner_cmd = []

        self.processor._adjust_service_name()
        assert self.processor.args.service_name == service_name
        assert self.processor.args.inner_cmd == []

    def test_VALID_USER_INPUT(self, tmp_path, monkeypatch):
        file_name = "compose.yml"
        content = "services:\n  app:\n  db:"
        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        monkeypatch.setattr(
            utils, "get_compose_file_paths", MagicMock(return_value=[Path(file_name)])
        )

        # User input
        self.processor.args.service_name = ["db", "app"]
        self.processor.args.inner_cmd = []

        self.processor._adjust_service_name()

        assert self.processor.args.service_name == ["db", "app"]
        assert self.processor.args.inner_cmd == []

    def test_INVALID_USER_INPUT(self, tmp_path, monkeypatch):
        file_name = "compose.yml"
        content = "services:\n  app:\n  db:"
        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        monkeypatch.setattr(
            utils, "get_compose_file_paths", MagicMock(return_value=[Path(file_name)])
        )

        # User input
        self.processor.args.service_name = ["manage.py"]
        self.processor.args.inner_cmd = ["runserver"]

        self.processor._adjust_service_name()

        assert self.processor.args.service_name == []
        assert self.processor.args.inner_cmd == ["manage.py", "runserver"]


class TestCreateOptions(TestDCPBase):
    def setup_method(self):
        super().setup_method()
        self.processor._args = MagicMock()

    def test_create_common_compose_options(self, monkeypatch):
        monkeypatch.setattr(Processor, "_create_project_option", MagicMock())
        monkeypatch.setattr(Processor, "_create_file_option", MagicMock())
        monkeypatch.setattr(Processor, "_create_profile_option", MagicMock())

        self.processor._create_common_compose_options()

        Processor._create_project_option.assert_called_once()
        Processor._create_file_option.assert_called_once()
        Processor._create_profile_option.assert_called_once()

    # File Option
    @pytest.mark.parametrize(
        "file_values,expected_value",
        [
            (None, []),
            (["compose.yaml"], ["-f", "compose.yaml"]),
            (["compose.yml"], ["-f", "compose.yml"]),
            (
                    ["compose.yaml", "compose_2.yaml"],
                    ["-f", "compose.yaml", "-f", "compose_2.yaml"],
            ),
            (
                    ["compose.yml", "compose_2.yml"],
                    ["-f", "compose.yml", "-f", "compose_2.yml"],
            ),
        ],
    )
    def test_create_file_option_VALID_TYPE(self, file_values, expected_value):
        """test for valid file extensions (yaml/yml)"""
        self.processor._args.file = file_values

        assert self.processor._create_file_option() == expected_value

    @pytest.mark.parametrize(
        "file_values",
        [
            ["compose.txt"],
            ["compose.txt", "compose_2.txt"],
        ],
    )
    def test_create_file_option_INVALID_TYPE(self, file_values, capsys, monkeypatch):
        """test for invalid file extensions: warns to stderr and start interactive selection"""
        monkeypatch.setattr(utils, "get_file_choices", MagicMock())
        self.processor._args.file = file_values

        self.processor._create_file_option()

        captured = capsys.readouterr()
        assert "Invalid file type" in captured.err
        utils.get_file_choices.assert_called_once()

    @pytest.mark.parametrize(
        "exception",
        [KeyboardInterrupt, SystemExit],
    )
    def test_create_file_option_ERROR_RAISED(self, exception):
        self.processor._args.file = []
        with patch(
                "compose_lazy.utils.get_file_choices",
                MagicMock(side_effect=exception),
        ):
            with pytest.raises((SystemExit, KeyboardInterrupt)):
                self.processor._create_file_option()

    # Profile Option
    @pytest.mark.parametrize(
        "profile_values,expected_value",
        [
            (None, []),
            (["test"], ["--profile", "test"]),
            (
                    ["test", "test_2"],
                    ["--profile", "test", "--profile", "test_2"],
            ),
        ],
    )
    def test_create_profile_option_VALID_TYPE(self, profile_values, expected_value):
        self.processor._args.profile = profile_values

        assert self.processor._create_profile_option() == expected_value

    @pytest.mark.parametrize(
        "exception",
        [KeyboardInterrupt, SystemExit],
    )
    def test_create_profile_option_ERROR_RAISED(self, exception):
        self.processor._args.profile = []
        with patch(
                "compose_lazy.utils.get_profile_choices",
                MagicMock(side_effect=exception),
        ):
            with pytest.raises((SystemExit, KeyboardInterrupt)):
                self.processor._create_profile_option()

    # Project Option
    @pytest.mark.parametrize(
        "project_value,expected_value",
        [
            ("", []),
            ("compose-lazy", ["-p", "compose-lazy"]),
        ],
    )
    def test_create_project_option(self, project_value, expected_value):
        self.processor._args.project = project_value

        assert self.processor._create_project_option() == expected_value


class TestCreateServiceOption(TestDCPBase):
    @pytest.mark.parametrize(
        "service_name,service,multiple,expected",
        [
            (["test"], False, False, ["test"]),
            (["test"], True, False, ["test"]),
            (["test"], False, True, ["test"]),
            (["test"], True, True, ["test"]),
            ([], False, True, []),
        ],
    )
    def test_VALID(self, service_name, service, multiple, expected):
        self.processor._args.service_name = service_name
        self.processor._args.service = service

        result = self.processor._create_service_option(multiple)
        assert result == expected

    @pytest.mark.parametrize(
        "service_name,service,multiple",
        [
            ([], False, False),
            ([], True, True),
        ],
    )
    def test_WITHOUT_SERVICE_NAMES(self, service_name, service, multiple, monkeypatch):
        """`_get_service_choices` method called."""
        monkeypatch.setattr(utils, "get_service_choices", MagicMock())

        self.processor._args.service_name = service_name
        self.processor._args.service = service

        self.processor._create_service_option(multiple)

        utils.get_service_choices.assert_called_once_with(multiple=multiple)

    @pytest.mark.parametrize(
        "service_name,service,multiple,expected",
        [
            ([], False, False, KeyboardInterrupt),
            ([], True, True, SystemExit),
        ],
    )
    def test_ERROR_RAISED(self, service_name, service, multiple, expected, monkeypatch):
        monkeypatch.setattr(utils, "get_service_choices", MagicMock(side_effect=expected))
        self.processor._args.service_name = service_name
        self.processor._args.service = service

        with pytest.raises((SystemExit, KeyboardInterrupt)):
            self.processor._create_service_option(multiple=multiple)
