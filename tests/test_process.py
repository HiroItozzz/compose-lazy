import subprocess
from argparse import Namespace

import pytest
from unittest.mock import MagicMock

from fast_dcp.process import DockerCmdProcessor


class TestDCPBase:
    def setup_method(self):
        self.processor = DockerCmdProcessor()


class TestDCPSetup(TestDCPBase):
    def test_dcp_setup(self):
        from fast_dcp.process import _BASE_CMD

        args = Namespace(test="result")
        self.processor._setup(args)

        assert self.processor.cmd == list(_BASE_CMD)
        assert self.processor.args == args


class TestDockerCmdProcessorCall(TestDCPBase):
    def setup_method(self):
        super().setup_method()
        self.processor._setup = MagicMock()
        self.processor._run_cmd = MagicMock()

        self.processor._create_up_cmd = MagicMock()
        self.processor._create_build_cmd = MagicMock()
        self.processor._create_exec_cmd = MagicMock()
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
            ("restart", "_create_restart_cmd"),
            ("r", "_create_restart_cmd"),
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
        getattr(self.processor, "_run_cmd").assert_called_once()

    def test_call_dcpu(self):
        args = Namespace()
        self.processor.call_dcpu(args)

        self.processor._setup.assert_called_once()
        self.processor._create_up_cmd.assert_called_once()
        self.processor._run_cmd.assert_called_once()

    def test_call_dcpe(self):
        args = Namespace()
        self.processor.call_dcpe(args)

        self.processor._setup.assert_called_once()
        self.processor._create_exec_cmd.assert_called_once()
        self.processor._run_cmd.assert_called_once()


class TestRunSubprocess(TestDCPBase):
    def test_run_subprocess(self):
        result = MagicMock()
        result.returncode = 1
        subprocess.run = MagicMock(return_value=result)

        test_cmd = ["docker", "compose up"]
        self.processor.cmd = test_cmd
        self.processor._run_cmd()

        subprocess.run.assert_called_once_with(test_cmd)
        assert self.processor._run_cmd() == 1


class TestCreateOptions(TestDCPBase):
    def setup_method(self):
        super().setup_method()
        self.processor._args = MagicMock()

    @pytest.mark.parametrize(
        "file_values,expected_value",
        [
            ([], []),
            (["compose.yaml"], ["-f", "compose.yaml"]),
            (["compose.yml"], ["-f", "compose.yml"]),
            (["compose.yaml", "compose_2.yaml"], ["-f", "compose.yaml", "-f", "compose_2.yaml"]),
            (["compose.yml", "compose_2.yml"], ["-f", "compose.yml", "-f", "compose_2.yml"]),
        ],
    )
    def test_create_file_option_VALID_TYPE(self, file_values, expected_value):
        """test for valid file extensions (yaml/yml)"""
        self.processor._args.file = file_values

        assert self.processor._create_file_option() == expected_value

    @pytest.mark.parametrize(
        "file_values,expected_value",
        [
            (["compose.txt"], ["-f", "compose.txt"]),
            (["compose.txt", "compose_2.txt"], ["-f", "compose.txt", "-f", "compose_2.txt"]),
        ],
    )
    def test_create_file_option_INVALID_TYPE(self, file_values, expected_value, capsys):
        """test for invalid file extensions: warns to stderr but still processes the file"""
        self.processor._args.file = file_values

        assert self.processor._create_file_option() == expected_value
        captured = capsys.readouterr()
        assert "invalid file type" in captured.err

    @pytest.mark.parametrize(
        "project_value,expected_value",
        [
            ([], []),
            (["fast-dcp"], ["-p", "fast-dcp"]),
        ],
    )
    def test_create_project_option(self, project_value, expected_value):
        self.processor._args.project = project_value

        assert self.processor._create_project_option() == expected_value
