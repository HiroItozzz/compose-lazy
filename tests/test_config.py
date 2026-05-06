class TestSetupLogger:
    def teardown_method(self):
        import logging

        logging.getLogger("test").handlers = []

    def test_setup_logger(self):
        import logging
        from logging import StreamHandler, getLogger

        from fast_dcp.config import setup_logger

        setup_logger("test")

        assert len(getLogger("test").handlers) >= 1
        assert any(
            isinstance(h, StreamHandler) for h in getLogger("test").handlers
        )
