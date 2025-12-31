"""Tests for FingerClient high-level API."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from mapilli.client.session import FingerClient
from mapilli.protocol.constants import DEFAULT_PORT, DEFAULT_TIMEOUT
from mapilli.protocol.response import FingerResponse

# Import asyncio.TimeoutError for explicit catch in tests

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.unit
class TestFingerClientInit:
    """Test FingerClient initialization."""

    def test_default_timeout(self) -> None:
        """Default timeout should be DEFAULT_TIMEOUT (30s)."""
        client = FingerClient()

        assert client.timeout == DEFAULT_TIMEOUT
        assert client.timeout == 30.0

    def test_custom_timeout(self) -> None:
        """Custom timeout should be stored."""
        client = FingerClient(timeout=10.0)

        assert client.timeout == 10.0


@pytest.mark.unit
class TestFingerClientContextManager:
    """Test async context manager."""

    async def test_aenter_returns_self(self) -> None:
        """__aenter__ should return the client instance."""
        client = FingerClient()

        async with client as ctx:
            assert ctx is client

    async def test_aexit_completes(self) -> None:
        """__aexit__ should complete without error."""
        client = FingerClient()

        # Should not raise
        async with client:
            pass

    async def test_context_manager_reusable(self) -> None:
        """Context manager should be reusable."""
        client = FingerClient()

        async with client:
            pass

        async with client:
            pass


@pytest.mark.unit
class TestFingerClientQuery:
    """Test FingerClient.query() method with mocked finger()."""

    async def test_query_parses_and_calls_finger(self, mocker: MockerFixture) -> None:
        """query() should parse query string and call finger()."""
        client = FingerClient()

        mock_response = FingerResponse(
            body="test", host="example.com", port=79, query="alice"
        )
        mock_finger = mocker.patch.object(client, "finger", return_value=mock_response)

        await client.query("alice", host="example.com")

        mock_finger.assert_called_once_with(host="example.com", port=79, query="alice")

    async def test_query_extracts_host_from_query(self, mocker: MockerFixture) -> None:
        """query() should extract host from user@host format."""
        client = FingerClient()

        mock_response = FingerResponse(
            body="test", host="remotehost.com", port=79, query="alice"
        )
        mock_finger = mocker.patch.object(client, "finger", return_value=mock_response)

        await client.query("alice@remotehost.com")

        # Host extracted from query, wire_query is just "alice"
        mock_finger.assert_called_once_with(
            host="remotehost.com", port=79, query="alice"
        )

    async def test_query_uses_host_parameter(self, mocker: MockerFixture) -> None:
        """query() should use host parameter if not in query."""
        client = FingerClient()

        mock_response = FingerResponse(
            body="test", host="example.com", port=79, query="alice"
        )
        mock_finger = mocker.patch.object(client, "finger", return_value=mock_response)

        await client.query("alice", host="example.com")

        mock_finger.assert_called_once_with(host="example.com", port=79, query="alice")

    async def test_query_no_host_raises_valueerror(self) -> None:
        """query() should raise ValueError if no host available."""
        client = FingerClient()

        with pytest.raises(ValueError, match="No host specified"):
            await client.query("alice")

    async def test_query_verbose_format(self, mocker: MockerFixture) -> None:
        """query() should handle verbose /W prefix."""
        client = FingerClient()

        mock_response = FingerResponse(
            body="test", host="example.com", port=79, query="/W alice"
        )
        mock_finger = mocker.patch.object(client, "finger", return_value=mock_response)

        await client.query("/W alice", host="example.com")

        mock_finger.assert_called_once_with(
            host="example.com", port=79, query="/W alice"
        )

    async def test_query_custom_port(self, mocker: MockerFixture) -> None:
        """query() should use custom port."""
        client = FingerClient()

        mock_response = FingerResponse(
            body="test", host="example.com", port=8079, query="alice"
        )
        mock_finger = mocker.patch.object(client, "finger", return_value=mock_response)

        await client.query("alice", host="example.com", port=8079)

        mock_finger.assert_called_once_with(
            host="example.com", port=8079, query="alice"
        )

    async def test_query_empty_list_users(self, mocker: MockerFixture) -> None:
        """query() with empty string should list users."""
        client = FingerClient()

        mock_response = FingerResponse(
            body="user1\nuser2\n", host="example.com", port=79, query=""
        )
        mock_finger = mocker.patch.object(client, "finger", return_value=mock_response)

        await client.query("", host="example.com")

        mock_finger.assert_called_once_with(host="example.com", port=79, query="")

    async def test_query_chained_hosts(self, mocker: MockerFixture) -> None:
        """query() should handle chained hosts correctly."""
        client = FingerClient()

        mock_response = FingerResponse(
            body="test", host="host1", port=79, query="alice@host1@host2"
        )
        mock_finger = mocker.patch.object(client, "finger", return_value=mock_response)

        await client.query("alice@host1@host2")

        # For chained, connect to first host, send full query
        mock_finger.assert_called_once_with(
            host="host1", port=79, query="alice@host1@host2"
        )


@pytest.mark.integration
class TestFingerClientFinger:
    """Test FingerClient.finger() with mock server."""

    async def test_finger_basic(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test basic finger query with mock server."""
        port, set_response, _ = mock_finger_server
        set_response("alice", sample_finger_responses["user_info"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "alice", port)

        assert "Login: alice" in response.body
        assert response.host == "127.0.0.1"
        assert response.port == port
        assert response.query == "alice"

    async def test_finger_empty_query(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test empty query (list users)."""
        port, _, set_default = mock_finger_server
        set_default(sample_finger_responses["user_list"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "", port)

        assert "alice" in response.body
        assert "bob" in response.body

    async def test_finger_verbose_query(self, mock_finger_server: tuple) -> None:
        """Test verbose query."""
        port, set_response, _ = mock_finger_server
        set_response("/W alice", "Verbose info\r\n")

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "/W alice", port)

        assert "Verbose info" in response.body

    async def test_finger_connection_refused(self, unused_tcp_port: int) -> None:
        """Test connection to closed port raises ConnectionError."""
        async with FingerClient(timeout=2.0) as client:
            with pytest.raises(ConnectionError, match="Connection failed"):
                await client.finger("127.0.0.1", "alice", unused_tcp_port)

    @pytest.mark.slow
    async def test_finger_timeout_response(self, slow_finger_server: tuple) -> None:
        """Test timeout during response raises TimeoutError."""
        port, set_delay = slow_finger_server
        set_delay(10.0)  # 10 second delay

        async with FingerClient(timeout=1.0) as client:
            with pytest.raises((TimeoutError, asyncio.TimeoutError)):
                await client.finger("127.0.0.1", "alice", port)

    async def test_finger_multiline_response(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test multiline response."""
        port, set_response, _ = mock_finger_server
        set_response("test", sample_finger_responses["multiline"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "test", port)

        assert len(response.lines) == 3
        assert response.lines[0] == "Line 1"
        assert response.lines[2] == "Line 3"


@pytest.mark.integration
class TestFingerClientQueryIntegration:
    """Integration tests for FingerClient.query() with mock server."""

    async def test_query_with_embedded_host(self, mock_finger_server: tuple) -> None:
        """Test query("alice@host") extracts host correctly."""
        port, set_response, _ = mock_finger_server
        set_response("alice", "User found\r\n")

        async with FingerClient() as client:
            # Note: We can't use "alice@127.0.0.1" directly since the
            # mock server listens on dynamic port. Use host parameter.
            response = await client.query("alice", host="127.0.0.1", port=port)

        assert "User found" in response.body

    async def test_query_empty_response(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test handling empty response."""
        port, set_response, _ = mock_finger_server
        set_response("empty", sample_finger_responses["empty"])

        async with FingerClient() as client:
            response = await client.query("empty", host="127.0.0.1", port=port)

        assert response.body == ""
        assert response.lines == []


@pytest.mark.unit
class TestFingerClientErrorHandling:
    """Test FingerClient error handling."""

    async def test_connection_refused_raises_connection_error(
        self, unused_tcp_port: int
    ) -> None:
        """Test connection to closed port raises ConnectionError."""
        client = FingerClient(timeout=2.0)

        with pytest.raises(ConnectionError):
            await client.finger("127.0.0.1", "alice", unused_tcp_port)
