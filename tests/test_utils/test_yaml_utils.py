from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from yaml.scanner import ScannerError

from compose_lazy.utils import (
    AttrDict,
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
        monkeypatch.setattr(yaml, "add_representer", MagicMock())
        monkeypatch.setattr(yaml, "add_constructor", MagicMock())

        path = Path("path")
        h = YamlHandler(path)
        yaml.add_representer.assert_called_once()
        yaml.add_constructor.assert_called_once()
        assert h.path == path
        assert h._config is None

    def test_setup_config_PROPERTY(self, tmp_path):
        config_path = tmp_path / "test"
        config_path.touch()
        handler = YamlHandler(config_path)
        assert handler._config is None
        assert handler.config == AttrDict()

    def test_setup_config_PATH_EXISTS(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / "test"
        config_path.touch()
        monkeypatch.setattr(
            YamlHandler, "_read_and_load", MagicMock(return_value=AttrDict())
        )
        keys = "key1", "key2"
        h = YamlHandler(config_path)
        h.setup_config(*keys)

        h._read_and_load.assert_called_once()
        assert set(h.config) == set(keys)
        assert isinstance(h.config, AttrDict)
        assert isinstance(h.config.key1, AttrDict)

    def test_setup_config_KEY_ALREADY_EXISTS(self, tmp_path):
        config_path = tmp_path / "test"
        config_path.write_text("workspaces:\n  ws1: []\n", encoding="utf-8")
        h = YamlHandler(config_path)
        h.setup_config()
        assert "workspaces" in h.config

    def test_setup_config_PATH_NOT_EXISTS(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / "test"
        assert not config_path.exists()

        monkeypatch.setattr(
            YamlHandler, "_read_and_load", MagicMock(return_value=AttrDict())
        )
        keys = "key1", "key2"
        h = YamlHandler(config_path)
        h.setup_config(*keys)

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
    def test_setup_config_ERROR(self, error, msg, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / "test"
        config_path.touch()
        monkeypatch.setattr(YamlHandler, "_read_and_load", MagicMock(side_effect=error))
        keys = "key1", "key2"
        h = YamlHandler(config_path)

        with pytest.raises(SystemExit):
            h.setup_config(*keys)
        _, err = capsys.readouterr()
        assert msg in err

    def test_read_and_load(self, tmp_path):
        config_path = tmp_path / "test"
        config_path.write_text("key: value", encoding="utf-8")
        handler = YamlHandler(config_path)
        result = handler._read_and_load()

        assert result["key"] == "value"

    def test_dump_and_write(self, tmp_path):
        config_path = tmp_path / "test"
        config_path.touch()
        handler = YamlHandler(config_path)
        handler._config = AttrDict(key="value")

        handler.dump_and_write()

        content = config_path.read_text(encoding="utf-8")
        assert "key" in content
        assert "value" in content


class TestYamlHandlerGetValues:
    def setup_method(self):
        self.handler = YamlHandler.__new__(YamlHandler)
        self.values = ["val1", "val2"]
        self.handler._config = {"key1": {"key2": self.values}}

    def test_valid(self):
        result = self.handler.get_values("key1", "key2")

        assert result == self.values

    def test_invalid(self):
        result = self.handler.get_values("key1", "key100")

        assert result is None


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
