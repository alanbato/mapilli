"""Tests for protocol constants."""

import pytest

from mapilli.protocol.constants import (
    CRLF,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    MAX_RESPONSE_SIZE,
    VERBOSE_PREFIX,
)


@pytest.mark.unit
class TestProtocolConstants:
    """Test Finger protocol constants match RFC 1288 specification."""

    def test_default_port(self) -> None:
        """DEFAULT_PORT should be 79 per RFC 1288."""
        assert DEFAULT_PORT == 79

    def test_max_response_size(self) -> None:
        """MAX_RESPONSE_SIZE should be 10 MB (DoS protection)."""
        assert MAX_RESPONSE_SIZE == 10 * 1024 * 1024
        assert MAX_RESPONSE_SIZE == 10_485_760

    def test_default_timeout(self) -> None:
        """DEFAULT_TIMEOUT should be 30 seconds."""
        assert DEFAULT_TIMEOUT == 30.0
        assert isinstance(DEFAULT_TIMEOUT, float)

    def test_crlf(self) -> None:
        """CRLF should be bytes b'\\r\\n'."""
        assert CRLF == b"\r\n"
        assert isinstance(CRLF, bytes)
        assert len(CRLF) == 2

    def test_verbose_prefix(self) -> None:
        """VERBOSE_PREFIX should be '/W' per RFC 1288."""
        assert VERBOSE_PREFIX == "/W"
        assert isinstance(VERBOSE_PREFIX, str)
