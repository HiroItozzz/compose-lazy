from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from yaml.scanner import ScannerError

from fast_dcp.workspace import (
    AttrDict,
    WorkspaceExecutor,
    WorkspaceRegistrar,
    YamlHandler,
)


class TestAttrDict:
    def test_getattr_VALID(self):
        d = AttrDict()
        value = "v"
        d.key = value

        assert d.key == value

    def test_getattr_ERROR(self):
        d = AttrDict()

        with pytest.raises(AttributeError):
            _ = d.key

    def test_dir(self):
        d = AttrDict()
        key = "key"
        d[key] = "value"
        assert key in dir(d)


class TestYamlHandlerInit:
    def test_init(self, monkeypatch):
        monkeypatch.setattr(YamlHandler, "_setup_config", MagicMock())
        monkeypatch.setattr(yaml, "add_representer", MagicMock())
        monkeypatch.setattr(yaml, "add_constructor", MagicMock())

        path = Path("path")
        keys = 1, 2, 3
        h = YamlHandler(path, *keys)
        yaml.add_representer.assert_called_once()
        yaml.add_constructor.assert_called_once()
        h._setup_config.assert_called_once_with(*keys)

    def test_init_PATH_EXISTS(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / "test"
        config_path.touch()
        monkeypatch.setattr(
            YamlHandler, "_read_and_load", MagicMock(return_value=AttrDict())
        )
        keys = "key1", "key2"
        h = YamlHandler(config_path, *keys)

        h._read_and_load.assert_called_once()
        assert set(h.config) == set(keys)
        assert isinstance(h.config, AttrDict)
        assert isinstance(h.config.key1, AttrDict)
        
    def test_setup_config_KEY_ALREADY_EXISTS(self, tmp_path):
        config_path = tmp_path / "test"
        config_path.write_text("workspaces:\n  ws1: []\n", encoding="utf-8")
        handler = YamlHandler(config_path, "workspaces")
        assert "workspaces" in handler.config

    def test_init_PATH_NOT_EXISTS(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / "test"
        assert not config_path.exists()

        monkeypatch.setattr(
            YamlHandler, "_read_and_load", MagicMock(return_value=AttrDict())
        )
        keys = "key1", "key2"
        h = YamlHandler(config_path, *keys)

        assert config_path.exists()
        assert set(h.config) == set(keys)

    @pytest.mark.parametrize(
        "error,msg",
        (
            [
                (ScannerError, "❌ Couldn't load yaml: "),
                (FileNotFoundError, "❌ Couldn't find directory: "),
            ]
        ),
    )
    def test_init_ERROR(self, error, msg, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / "test"
        config_path.touch()
        monkeypatch.setattr(YamlHandler, "_read_and_load", MagicMock(side_effect=error))
        keys = "key1", "key2"

        with pytest.raises(SystemExit):
            YamlHandler(config_path, *keys)
        _, err = capsys.readouterr()
        assert msg in err

    def test_read_and_load(self, tmp_path, monkeypatch):
        config_path = tmp_path / "test"
        config_path.write_text("key: value", encoding="utf-8")
        monkeypatch.setattr(YamlHandler, "__init__", lambda self, *args, **kwargs: None)
        handler = YamlHandler.__new__(YamlHandler)
        handler.path = config_path
        result = handler._read_and_load()

        assert result["key"] == "value"

    def test_dump_and_write(self, tmp_path, monkeypatch):
        monkeypatch.setattr(YamlHandler, "__init__", lambda self, *args, **kwargs: None)
        handler = YamlHandler.__new__(YamlHandler)
        config_path = tmp_path / "test"
        config_path.touch()
        handler.path = config_path
        handler._config = AttrDict(key="value")

        handler.dump_and_write()

        content = config_path.read_text(encoding="utf-8")
        assert "key" in content
        assert "value" in content


class TestYamlHandlerAppendValue:
    def setup_method(self):
        self.handler = YamlHandler.__new__(YamlHandler)
        self.handler._config = AttrDict()

    def test_append_value_NEW(self):
        result = self.handler.append_value("cat1", "cat2", "value")
        assert result is True
        assert "value" in self.handler._config["cat1"]["cat2"]

    def test_append_value_DUPLICATE(self):
        self.handler.append_value("cat1", "cat2", "value")
        result = self.handler.append_value("cat1", "cat2", "value")
        assert result is False

    def test_append_value_SORTED(self):
        self.handler.append_value("cat1", "cat2", "b")
        self.handler.append_value("cat1", "cat2", "a")
        assert self.handler._config["cat1"]["cat2"] == ["a", "b"]

    def test_append_value_DEEP(self):
        result = self.handler.append_value("cat1", "cat2", "cat3", "value")
        assert result is True
        assert "value" in self.handler._config["cat1"]["cat2"]["cat3"]

