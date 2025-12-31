"""End-to-end integration tests with mock Finger server."""

from __future__ import annotations

import asyncio

import pytest

from mapilli.client.session import FingerClient


@pytest.mark.integration
class TestEndToEndFingerQueries:
    """End-to-end tests with mock Finger server."""

    async def test_user_info_query(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test querying user information."""
        port, set_response, _ = mock_finger_server
        set_response("alice", sample_finger_responses["user_info"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "alice", port)

        assert "Login: alice" in response.body
        assert "Name: Alice Smith" in response.body
        assert response.host == "127.0.0.1"
        assert response.port == port
        assert response.query == "alice"

    async def test_user_list_query(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test listing all users (empty query)."""
        port, _, set_default = mock_finger_server
        set_default(sample_finger_responses["user_list"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "", port)

        lines = response.lines
        assert len(lines) > 0
        assert "alice" in response.body.lower()
        assert "bob" in response.body.lower()

    async def test_no_such_user(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test query for non-existent user."""
        port, set_response, _ = mock_finger_server
        set_response("nonexistent", sample_finger_responses["no_such_user"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "nonexistent", port)

        assert "no such user" in response.body

    async def test_empty_response(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test handling empty response."""
        port, set_response, _ = mock_finger_server
        set_response("quiet", sample_finger_responses["empty"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "quiet", port)

        assert response.body == ""
        assert response.lines == []

    async def test_multiline_response(
        self,
        mock_finger_server: tuple,
        sample_finger_responses: dict,
    ) -> None:
        """Test multiline response parsing."""
        port, set_response, _ = mock_finger_server
        set_response("multi", sample_finger_responses["multiline"])

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "multi", port)

        assert len(response.lines) == 3
        assert response.lines[0] == "Line 1"
        assert response.lines[1] == "Line 2"
        assert response.lines[2] == "Line 3"


@pytest.mark.integration
class TestFingerClientQueryMethod:
    """Test FingerClient.query() with mock server."""

    async def test_query_method_with_host_param(
        self,
        mock_finger_server: tuple,
    ) -> None:
        """Test query("alice", host="127.0.0.1", port=port)."""
        port, set_response, _ = mock_finger_server
        set_response("alice", "User found\r\n")

        async with FingerClient() as client:
            response = await client.query("alice", host="127.0.0.1", port=port)

        assert "User found" in response.body

    async def test_query_method_verbose(
        self,
        mock_finger_server: tuple,
    ) -> None:
        """Test query with verbose /W prefix."""
        port, set_response, _ = mock_finger_server
        set_response("/W alice", "Verbose output\r\n")

        async with FingerClient() as client:
            response = await client.query("/W alice", host="127.0.0.1", port=port)

        assert "Verbose output" in response.body

    async def test_query_method_empty(
        self,
        mock_finger_server: tuple,
    ) -> None:
        """Test empty query lists users."""
        port, _, set_default = mock_finger_server
        set_default("user1\r\nuser2\r\n")

        async with FingerClient() as client:
            response = await client.query("", host="127.0.0.1", port=port)

        assert "user1" in response.body
        assert "user2" in response.body


@pytest.mark.integration
@pytest.mark.slow
class TestTimeoutBehavior:
    """Test timeout handling with slow server."""

    async def test_slow_server_timeout(
        self,
        slow_finger_server: tuple,
    ) -> None:
        """Test timeout with slow server."""
        port, set_delay = slow_finger_server
        set_delay(10.0)  # 10 second delay

        async with FingerClient(timeout=1.0) as client:
            with pytest.raises((TimeoutError, asyncio.TimeoutError)):
                await client.finger("127.0.0.1", "alice", port)

    async def test_slow_server_succeeds_within_timeout(
        self,
        slow_finger_server: tuple,
    ) -> None:
        """Test slow server succeeds if response arrives within timeout."""
        port, set_delay = slow_finger_server
        set_delay(0.1)  # 100ms delay

        async with FingerClient(timeout=5.0) as client:
            response = await client.finger("127.0.0.1", "alice", port)

        assert "Delayed response" in response.body


@pytest.mark.integration
class TestConnectionErrors:
    """Test connection error handling."""

    async def test_connection_refused(
        self,
        unused_tcp_port: int,
    ) -> None:
        """Test connection to closed port raises ConnectionError."""
        async with FingerClient(timeout=2.0) as client:
            with pytest.raises(ConnectionError):
                await client.finger("127.0.0.1", "alice", unused_tcp_port)

    async def test_invalid_host(self) -> None:
        """Test connection to invalid host raises error."""
        async with FingerClient(timeout=2.0) as client:
            with pytest.raises((ConnectionError, OSError, TimeoutError)):
                await client.finger("invalid.host.that.does.not.exist", "alice", 79)


@pytest.mark.integration
class TestResponseMetadata:
    """Test response metadata is correctly populated."""

    async def test_response_contains_host(
        self,
        mock_finger_server: tuple,
    ) -> None:
        """Test response contains queried host."""
        port, set_response, _ = mock_finger_server
        set_response("test", "Response\r\n")

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "test", port)

        assert response.host == "127.0.0.1"

    async def test_response_contains_port(
        self,
        mock_finger_server: tuple,
    ) -> None:
        """Test response contains queried port."""
        port, set_response, _ = mock_finger_server
        set_response("test", "Response\r\n")

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "test", port)

        assert response.port == port

    async def test_response_contains_query(
        self,
        mock_finger_server: tuple,
    ) -> None:
        """Test response contains original query."""
        port, set_response, _ = mock_finger_server
        set_response("myquery", "Response\r\n")

        async with FingerClient() as client:
            response = await client.finger("127.0.0.1", "myquery", port)

        assert response.query == "myquery"
