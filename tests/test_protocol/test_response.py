"""Tests for FingerResponse dataclass."""

import pytest

from mapilli.protocol.response import FingerResponse


@pytest.mark.unit
class TestFingerResponse:
    """Test FingerResponse dataclass."""

    def test_create_response(self) -> None:
        """Test creating a basic response."""
        response = FingerResponse(
            body="Login: alice\r\nName: Alice\r\n",
            host="example.com",
            port=79,
            query="alice",
        )

        assert response.body == "Login: alice\r\nName: Alice\r\n"
        assert response.host == "example.com"
        assert response.port == 79
        assert response.query == "alice"

    def test_response_is_frozen(self) -> None:
        """Test response is immutable (frozen dataclass)."""
        response = FingerResponse(
            body="test",
            host="example.com",
            port=79,
            query="alice",
        )

        with pytest.raises(AttributeError):
            response.body = "modified"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            response.host = "other.com"  # type: ignore[misc]


@pytest.mark.unit
class TestFingerResponseLines:
    """Test FingerResponse.lines property."""

    def test_lines_single_line(self) -> None:
        """Test lines with single line response."""
        response = FingerResponse(
            body="Single line",
            host="example.com",
            port=79,
            query="",
        )

        assert response.lines == ["Single line"]

    def test_lines_multiline_lf(self) -> None:
        """Test lines splits on LF (\\n)."""
        response = FingerResponse(
            body="Line 1\nLine 2\nLine 3",
            host="example.com",
            port=79,
            query="",
        )

        assert response.lines == ["Line 1", "Line 2", "Line 3"]

    def test_lines_multiline_crlf(self) -> None:
        """Test lines splits on CRLF (\\r\\n)."""
        response = FingerResponse(
            body="Line 1\r\nLine 2\r\nLine 3",
            host="example.com",
            port=79,
            query="",
        )

        assert response.lines == ["Line 1", "Line 2", "Line 3"]

    def test_lines_mixed_endings(self) -> None:
        """Test lines handles mixed line endings."""
        response = FingerResponse(
            body="Line 1\r\nLine 2\nLine 3\rLine 4",
            host="example.com",
            port=79,
            query="",
        )

        # splitlines handles all line ending types
        assert len(response.lines) == 4
        assert response.lines[0] == "Line 1"
        assert response.lines[3] == "Line 4"

    def test_lines_empty_body(self) -> None:
        """Test lines with empty body."""
        response = FingerResponse(
            body="",
            host="example.com",
            port=79,
            query="",
        )

        assert response.lines == []

    def test_lines_trailing_newline(self) -> None:
        """Test lines with trailing newline."""
        response = FingerResponse(
            body="Line 1\nLine 2\n",
            host="example.com",
            port=79,
            query="",
        )

        # splitlines does not include empty string after trailing newline
        assert response.lines == ["Line 1", "Line 2"]

    def test_lines_only_newlines(self) -> None:
        """Test lines with only newlines (blank lines)."""
        response = FingerResponse(
            body="\n\n\n",
            host="example.com",
            port=79,
            query="",
        )

        assert response.lines == ["", "", ""]


@pytest.mark.unit
class TestFingerResponseStr:
    """Test FingerResponse __str__ method."""

    def test_str_returns_body(self) -> None:
        """Test __str__ returns body content."""
        body = "Login: alice\r\nName: Alice Smith\r\n"
        response = FingerResponse(
            body=body,
            host="example.com",
            port=79,
            query="alice",
        )

        assert str(response) == body

    def test_str_empty_body(self) -> None:
        """Test __str__ with empty body."""
        response = FingerResponse(
            body="",
            host="example.com",
            port=79,
            query="",
        )

        assert str(response) == ""

    def test_str_can_be_printed(self) -> None:
        """Test response can be printed directly."""
        response = FingerResponse(
            body="Test output",
            host="example.com",
            port=79,
            query="test",
        )

        # Should not raise
        output = f"{response}"
        assert output == "Test output"
