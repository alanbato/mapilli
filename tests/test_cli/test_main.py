"""Tests for Mapilli CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from typer.testing import CliRunner

from mapilli.__main__ import app
from mapilli.protocol.response import FingerResponse

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

runner = CliRunner()


@pytest.mark.unit
class TestCLIVersion:
    """Test --version option."""

    def test_version_flag(self) -> None:
        """--version should print version and exit."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Mapilli" in result.output

    def test_version_short_flag(self) -> None:
        """-V should print version and exit."""
        result = runner.invoke(app, ["-V"])

        assert result.exit_code == 0
        assert "Mapilli" in result.output


@pytest.mark.unit
class TestCLINoArgs:
    """Test CLI with no arguments."""

    def test_no_args_shows_help(self) -> None:
        """No args should show help/usage message."""
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        # Should show some form of help or usage
        assert (
            "help" in result.output.lower()
            or "usage" in result.output.lower()
            or "mapilli" in result.output.lower()
        )


@pytest.mark.unit
class TestCLIQueryExecution:
    """Test CLI query execution with mocked client."""

    def test_user_at_host(self, mocker: MockerFixture) -> None:
        """Test alice@host format."""
        mock_response = FingerResponse(
            body="Login: alice\r\n",
            host="example.com",
            port=79,
            query="alice",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["alice@example.com"])

        assert result.exit_code == 0
        assert "Login: alice" in result.output
        mock_client.query.assert_called_once()

    def test_user_with_host_option(self, mocker: MockerFixture) -> None:
        """Test --host option with username."""
        mock_response = FingerResponse(
            body="User found\r\n",
            host="example.com",
            port=79,
            query="alice",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        # Put options before positional argument
        result = runner.invoke(app, ["--host", "example.com", "alice"])

        assert result.exit_code == 0
        mock_client.query.assert_called_once_with("alice", host="example.com", port=79)

    def test_host_only_option(self, mocker: MockerFixture) -> None:
        """Test --host with no query (list users)."""
        mock_response = FingerResponse(
            body="user1\r\nuser2\r\n",
            host="example.com",
            port=79,
            query="",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--host", "example.com"])

        assert result.exit_code == 0
        mock_client.query.assert_called_once_with("", host="example.com", port=79)


@pytest.mark.unit
class TestCLIVerboseOption:
    """Test --whois/-W verbose option."""

    def test_verbose_option(self, mocker: MockerFixture) -> None:
        """Test -W/--whois option adds /W prefix."""
        mock_response = FingerResponse(
            body="Verbose output\r\n",
            host="example.com",
            port=79,
            query="/W alice",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["-W", "--host", "example.com", "alice"])

        assert result.exit_code == 0
        # Should have /W prefix in query
        call_args = mock_client.query.call_args
        assert "/W" in call_args[0][0]

    def test_verbose_long_option(self, mocker: MockerFixture) -> None:
        """Test --whois long option."""
        mock_response = FingerResponse(
            body="Verbose output\r\n",
            host="example.com",
            port=79,
            query="/W alice",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--whois", "--host", "example.com", "alice"])

        assert result.exit_code == 0


@pytest.mark.unit
class TestCLIPortOption:
    """Test --port option."""

    def test_custom_port(self, mocker: MockerFixture) -> None:
        """Test -p/--port option."""
        mock_response = FingerResponse(
            body="Response\r\n",
            host="example.com",
            port=8079,
            query="alice",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--host", "example.com", "-p", "8079", "alice"])

        assert result.exit_code == 0
        mock_client.query.assert_called_once_with(
            "alice", host="example.com", port=8079
        )

    def test_port_long_option(self, mocker: MockerFixture) -> None:
        """Test --port long option."""
        mock_response = FingerResponse(
            body="Response\r\n",
            host="example.com",
            port=8079,
            query="alice",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(
            app, ["--host", "example.com", "--port", "8079", "alice"]
        )

        assert result.exit_code == 0


@pytest.mark.unit
class TestCLITimeoutOption:
    """Test --timeout option."""

    def test_custom_timeout(self, mocker: MockerFixture) -> None:
        """Test -t/--timeout option."""
        mock_response = FingerResponse(
            body="Response\r\n",
            host="example.com",
            port=79,
            query="alice",
        )

        mock_client = AsyncMock()
        mock_client.query = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_finger_client = mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--host", "example.com", "-t", "10.0", "alice"])

        assert result.exit_code == 0
        mock_finger_client.assert_called_once_with(timeout=10.0)


@pytest.mark.unit
class TestCLIErrorHandling:
    """Test CLI error handling and exit codes."""

    def test_valueerror_exits_1(self, mocker: MockerFixture) -> None:
        """ValueError should show error and exit 1."""
        mock_client = AsyncMock()
        mock_client.query = AsyncMock(side_effect=ValueError("No host specified"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--host", "example.com", "alice"])

        assert result.exit_code == 1
        assert "Error" in result.output or "error" in result.output.lower()

    def test_timeout_exits_1(self, mocker: MockerFixture) -> None:
        """TimeoutError should show error and exit 1."""
        mock_client = AsyncMock()
        mock_client.query = AsyncMock(side_effect=TimeoutError("Connection timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--host", "example.com", "alice"])

        assert result.exit_code == 1
        assert "Timeout" in result.output or "timeout" in result.output.lower()

    def test_connection_error_exits_1(self, mocker: MockerFixture) -> None:
        """ConnectionError should show error and exit 1."""
        mock_client = AsyncMock()
        mock_client.query = AsyncMock(side_effect=ConnectionError("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--host", "example.com", "alice"])

        assert result.exit_code == 1
        assert "Connection" in result.output or "error" in result.output.lower()

    def test_unexpected_error_exits_1(self, mocker: MockerFixture) -> None:
        """Unexpected errors should show error and exit 1."""
        mock_client = AsyncMock()
        mock_client.query = AsyncMock(side_effect=RuntimeError("Something went wrong"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mocker.patch(
            "mapilli.__main__.FingerClient",
            return_value=mock_client,
        )

        result = runner.invoke(app, ["--host", "example.com", "alice"])

        assert result.exit_code == 1
