from logging import StreamHandler, getLogger

from fast_dcp import config


class TestSetupLogger:
    def teardown_method(self):
        import logging

        logging.getLogger("test").handlers = []

    def test_setup_logger(self, monkeypatch):

        monkeypatch.setattr(config, "DEBUG", True)

        config.setup_logger("test")

        assert len(getLogger("test").handlers) >= 1
        assert any(isinstance(h, StreamHandler) for h in getLogger("test").handlers)

    def test_setup_logger_(self, monkeypatch):
        monkeypatch.setattr(config, "DEBUG", False)

        config.setup_logger("test")

        assert len(getLogger("test").handlers) == 0
        assert not any(isinstance(h, StreamHandler) for h in getLogger("test").handlers)
