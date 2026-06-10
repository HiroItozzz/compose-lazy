import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import compose_lazy
from compose_lazy import main


class TestWorkspaceRegistrar:
    def setup_method(self):
        self.working_dir = Path(tempfile.mkdtemp()).resolve()
        self.file = self.working_dir / "compose.test.yaml"
        self.file.write_text("services:\n  app:\n  db:")

    def teardown_method(self):
        shutil.rmtree(self.working_dir)

    @pytest.mark.parametrize(
        "commandline_input,interactive_input",
        [
            (
                ["dcp ws reg", "dcp ws li", "dcp ws del"],
                [".", "test_ws", "\n", "1", "1"],
            )
        ],
    )
    def test_register_list_delete(
        self, commandline_input, interactive_input, capsys, monkeypatch
    ):
        monkeypatch.chdir(self.working_dir)

        mock_config = self.working_dir / "test_config"
        monkeypatch.setattr(compose_lazy.workspace, "CONFIG_PATH", mock_config)
        mock_config.unlink(missing_ok=True)
        mock_input = MagicMock(side_effect=interactive_input)
        monkeypatch.setattr("builtins.input", mock_input)
        expected_config = {
            "workspaces": {
                "test_ws": {
                    "repos": {str(self.working_dir): {"files": ["compose.test.yaml"]}}
                }
            }
        }

        expected_config = [expected_config, expected_config, {"workspaces": {}}]
        result_config = []

        expected_outs = [
            ("Registered",),
            (str(self.working_dir), "compose.test.yaml"),
            ("Deleted",),
        ]

        import yaml

        for cmd in commandline_input:
            monkeypatch.setattr("sys.argv", cmd.split())
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            assert exc_info.value.code == 0

            result_config.append(yaml.safe_load(mock_config.read_text()))

        out, _ = capsys.readouterr()
        assert all(o in out for expected_out in expected_outs for o in expected_out)
        assert expected_config == result_config
