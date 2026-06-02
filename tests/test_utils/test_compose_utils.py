from pathlib import Path
from unittest.mock import patch

import pytest

from compose_lazy import utils


def test_format_as_flag_args():
    result = utils.format_as_flag_args(["val1", "val2"], flag="--profile")

    assert result == ["--profile", "val1", "--profile", "val2"]


def test_get_compose_file_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docker-compose.yml").touch()
    (tmp_path / "docker-compose.prod.yaml").touch()

    result = utils.get_compose_file_paths()
    assert len(result) == 2


class TestGetServiceChoices:
    def test_get_service_choices_NO_FILE(self, capsys):
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = []

            with pytest.raises(SystemExit):
                utils.get_service_choices()

            captured = capsys.readouterr()
            assert "❌ No compose files found." in captured.err

    def test_get_service_choices_EMPTY(self, capsys, tmp_path, monkeypatch):
        file_name = "docker-compose.yml"
        content = ""

        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = [Path(file_name)]

            with pytest.raises(SystemExit):
                utils.get_service_choices()

            captured = capsys.readouterr()
            assert "❌ No services found." in captured.err

    def test_get_service_choices_SINGLE(self, capsys, tmp_path, monkeypatch):
        file_name = "docker-compose.yml"
        content = """
services:
  db:
"""
        service_name = "db"

        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = [Path(file_name)]
            result = utils.get_service_choices()

        captured = capsys.readouterr()
        assert f"☑ Service found: {service_name}" in captured.out
        assert result == [service_name]

    def test_get_service_choices_MULTIPLE(self, capsys, tmp_path, monkeypatch):
        file_name = "docker-compose.yml"
        content = """
services:
  app:
  db:
"""
        services = {"app", "db"}

        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = [Path(file_name)]
            with patch("compose_lazy.utils.cli_utils.interactive_select") as mock_select:
                utils.get_service_choices()

        captured = capsys.readouterr()
        assert f"☑ Found {len(services)} services!" in captured.out
        mock_select.assert_called_once_with(services, multiple=True)


class TestFileChoices:
    def test_get_file_choices_EMPTY(self, capsys):
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = []

            with pytest.raises(SystemExit):
                utils.get_file_choices()

            captured = capsys.readouterr()
            assert "No compose files found." in captured.err

    def test_get_file_choices_SINGLE(self, capsys):
        file_name = "docker-compose.yml"
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = [Path(file_name)]

            result = utils.get_file_choices()
            captured = capsys.readouterr()

        assert result == [file_name]
        assert f"Compose file found: {file_name}" in captured.out

    def test_get_file_choices_MULTIPLE(self):
        file_names = ["docker-compose.yml", "docker-compose.prod.yml"]
        file_paths = [Path(f) for f in file_names]
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = file_paths
            with patch("compose_lazy.utils.cli_utils.interactive_select") as mock_select:
                utils.get_file_choices()

        mock_select.assert_called_once_with(file_names)


class TestProfileChoices:
    def test_get_profile_choices_NO_FILE(self, capsys):
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = []

            with pytest.raises(SystemExit):
                utils.get_profile_choices()

            captured = capsys.readouterr()
            assert "❌ No compose files found." in captured.err

    def test_get_profile_choices_EMPTY(self, capsys, tmp_path, monkeypatch):
        file_name = "docker-compose.yml"
        content = """
services:
  app:
  db:
"""
        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = [Path(file_name)]
            with pytest.raises(SystemExit):
                utils.get_profile_choices()

            captured = capsys.readouterr()
            assert "❌ No profiles found." in captured.err

    def test_get_profile_choices_SINGLE(self, capsys, tmp_path, monkeypatch):
        file_name = "docker-compose.yml"
        content = """
services:
  app:
    profiles:
      - prod
  db:
    profiles:
      - prod
"""
        profile_name = "prod"

        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        with patch("compose_lazy.utils.get_compose_file_paths") as mock_paths:
            mock_paths.return_value = [Path(file_name)]
            result = utils.get_profile_choices()

        captured = capsys.readouterr()
        assert f"☑ Profile found: {profile_name}" in captured.out
        assert result == [profile_name]

    def test_get_profile_choices_MULTIPLE(self, capsys, tmp_path, monkeypatch):
        file_name = "docker-compose.yml"
        content = """
services:
  app:
    profiles:
      - prod
  db:
    profiles:
      - prod
      - dev
"""
        profiles = {"prod", "dev"}

        monkeypatch.chdir(tmp_path)
        (tmp_path / file_name).write_text(content)
        with patch(
            "compose_lazy.utils.compose_utils.get_compose_file_paths"
        ) as mock_paths:
            mock_paths.return_value = [Path(file_name)]
            with patch("compose_lazy.utils.cli_utils.interactive_select") as mock_select:
                utils.get_profile_choices()

        captured = capsys.readouterr()
        assert f"☑ Found {len(profiles)} profiles!" in captured.out
        mock_select.assert_called_once_with(profiles)
