"""Tests for logging configuration."""

import pytest
import structlog

from mapilli.utils.logging import _level_to_int, configure_logging, get_logger


@pytest.mark.unit
class TestLevelToInt:
    """Test _level_to_int helper function."""

    def test_debug_level(self) -> None:
        """DEBUG should return 10."""
        assert _level_to_int("DEBUG") == 10

    def test_info_level(self) -> None:
        """INFO should return 20."""
        assert _level_to_int("INFO") == 20

    def test_warning_level(self) -> None:
        """WARNING should return 30."""
        assert _level_to_int("WARNING") == 30

    def test_error_level(self) -> None:
        """ERROR should return 40."""
        assert _level_to_int("ERROR") == 40

    def test_critical_level(self) -> None:
        """CRITICAL should return 50."""
        assert _level_to_int("CRITICAL") == 50

    def test_unknown_defaults_to_info(self) -> None:
        """Unknown level should default to INFO (20)."""
        assert _level_to_int("UNKNOWN") == 20

    def test_case_insensitive(self) -> None:
        """Level names should be case-insensitive."""
        assert _level_to_int("debug") == 10
        assert _level_to_int("Debug") == 10
        assert _level_to_int("DEBUG") == 10


@pytest.mark.unit
class TestConfigureLogging:
    """Test configure_logging function."""

    def test_configure_default(self) -> None:
        """Test default configuration (INFO level, console output)."""
        # Should not raise
        configure_logging()

        # Verify structlog is configured
        logger = structlog.get_logger("test")
        assert logger is not None

    def test_configure_json_logs(self) -> None:
        """Test JSON log format configuration."""
        # Should not raise
        configure_logging(json_logs=True)

    def test_configure_debug_level(self) -> None:
        """Test DEBUG log level configuration."""
        configure_logging(log_level="DEBUG")

    def test_configure_error_level(self) -> None:
        """Test ERROR log level configuration."""
        configure_logging(log_level="ERROR")


@pytest.mark.unit
class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_returns_bound_logger(self) -> None:
        """get_logger should return a FilteringBoundLogger."""
        configure_logging()  # Ensure logging is configured
        logger = get_logger("mapilli.test")

        assert logger is not None
        # Should have standard logging methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_get_logger_different_names(self) -> None:
        """get_logger with different names should work."""
        configure_logging()

        logger1 = get_logger("mapilli.module1")
        logger2 = get_logger("mapilli.module2")

        assert logger1 is not None
        assert logger2 is not None
