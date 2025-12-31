"""Tests for FingerClientProtocol (asyncio.Protocol)."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from mapilli.client.protocol import FingerClientProtocol
from mapilli.protocol.constants import MAX_RESPONSE_SIZE
from mapilli.protocol.response import FingerResponse

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.unit
class TestFingerClientProtocolConnectionMade:
    """Test FingerClientProtocol.connection_made() method."""

    async def test_connection_made_sends_query(self, mocker: MockerFixture) -> None:
        """connection_made() should send query + CRLF."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        mock_transport.write.assert_called_once_with(b"alice\r\n")

    async def test_connection_made_stores_transport(
        self, mocker: MockerFixture
    ) -> None:
        """connection_made() should store transport reference."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)
        mock_transport = mocker.Mock()

        protocol.connection_made(mock_transport)

        assert protocol.transport is mock_transport

    async def test_connection_made_empty_query(self, mocker: MockerFixture) -> None:
        """connection_made() with empty query sends just CRLF."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("", "example.com", 79, future)

        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        mock_transport.write.assert_called_once_with(b"\r\n")

    async def test_connection_made_verbose_query(self, mocker: MockerFixture) -> None:
        """connection_made() with verbose query."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("/W alice", "example.com", 79, future)

        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        mock_transport.write.assert_called_once_with(b"/W alice\r\n")


@pytest.mark.unit
class TestFingerClientProtocolDataReceived:
    """Test FingerClientProtocol.data_received() method."""

    async def test_data_received_accumulates_buffer(
        self, mocker: MockerFixture
    ) -> None:
        """data_received() should accumulate data in buffer."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        protocol.data_received(b"Hello ")
        assert protocol.buffer == b"Hello "

        protocol.data_received(b"World")
        assert protocol.buffer == b"Hello World"

    async def test_data_received_multiple_chunks(self, mocker: MockerFixture) -> None:
        """data_received() handles multiple data chunks."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        chunks = [b"Line 1\r\n", b"Line 2\r\n", b"Line 3\r\n"]
        for chunk in chunks:
            protocol.data_received(chunk)

        assert protocol.buffer == b"Line 1\r\nLine 2\r\nLine 3\r\n"

    async def test_data_received_max_size_exceeded(self, mocker: MockerFixture) -> None:
        """data_received() should close connection if MAX_RESPONSE_SIZE exceeded."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        # Send data exceeding MAX_RESPONSE_SIZE
        oversized_data = b"x" * (MAX_RESPONSE_SIZE + 1)
        protocol.data_received(oversized_data)

        # Transport should be closed
        mock_transport.close.assert_called_once()

        # Future should have exception
        assert future.done()
        with pytest.raises(Exception, match="exceeds maximum size"):
            future.result()

    async def test_data_received_exactly_at_limit(self, mocker: MockerFixture) -> None:
        """data_received() at exactly MAX_RESPONSE_SIZE should not trigger error."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        # Send data exactly at MAX_RESPONSE_SIZE
        exact_data = b"x" * MAX_RESPONSE_SIZE
        protocol.data_received(exact_data)

        # Transport should NOT be closed
        mock_transport.close.assert_not_called()

        # Future should NOT be done yet
        assert not future.done()


@pytest.mark.unit
class TestFingerClientProtocolEofReceived:
    """Test FingerClientProtocol.eof_received() method."""

    async def test_eof_received_returns_false(self) -> None:
        """eof_received() should return False to close connection."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        result = protocol.eof_received()

        assert result is False


@pytest.mark.unit
class TestFingerClientProtocolConnectionLost:
    """Test FingerClientProtocol.connection_lost() method."""

    async def test_connection_lost_sets_response(self, mocker: MockerFixture) -> None:
        """connection_lost() without error should set response in future."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        # Simulate receiving data
        protocol.data_received(b"Login: alice\r\n")

        # Close connection normally
        protocol.connection_lost(None)

        assert future.done()
        response = future.result()
        assert isinstance(response, FingerResponse)
        assert response.body == "Login: alice\r\n"
        assert response.host == "example.com"
        assert response.port == 79
        assert response.query == "alice"

    async def test_connection_lost_with_exception(self, mocker: MockerFixture) -> None:
        """connection_lost() with error should set exception in future."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        # Close connection with error
        error = ConnectionResetError("Connection reset by peer")
        protocol.connection_lost(error)

        assert future.done()
        with pytest.raises(ConnectionResetError, match="Connection reset"):
            future.result()

    async def test_connection_lost_decodes_ascii(self, mocker: MockerFixture) -> None:
        """connection_lost() should decode buffer as ASCII."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        # ASCII data
        protocol.data_received(b"Hello World")
        protocol.connection_lost(None)

        response = future.result()
        assert response.body == "Hello World"

    async def test_connection_lost_replaces_invalid_chars(
        self, mocker: MockerFixture
    ) -> None:
        """connection_lost() should use errors='replace' for invalid ASCII."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        # Data with non-ASCII bytes (> 127)
        protocol.data_received(b"Hello \xff\xfe World")
        protocol.connection_lost(None)

        response = future.result()
        # Invalid bytes should be replaced with replacement character
        assert "Hello" in response.body
        assert "World" in response.body
        assert "\ufffd" in response.body  # Replacement character

    async def test_connection_lost_already_done(self, mocker: MockerFixture) -> None:
        """connection_lost() should be no-op if future already done."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        # Trigger error via oversized data (sets future)
        oversized_data = b"x" * (MAX_RESPONSE_SIZE + 1)
        protocol.data_received(oversized_data)

        assert future.done()

        # Now connection_lost should not try to set again
        protocol.connection_lost(None)  # Should not raise

        # Exception from oversized should still be there
        with pytest.raises(Exception, match="exceeds maximum size"):
            future.result()

    async def test_connection_lost_empty_response(self, mocker: MockerFixture) -> None:
        """connection_lost() with empty buffer creates empty response."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        # No data received, just close
        protocol.connection_lost(None)

        response = future.result()
        assert response.body == ""
        assert response.lines == []


@pytest.mark.unit
class TestFingerClientProtocolFullFlow:
    """Test complete query/response flow."""

    async def test_full_query_flow(self, mocker: MockerFixture) -> None:
        """Test complete query/response lifecycle."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        # 1. Connection established
        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        # Verify query sent
        mock_transport.write.assert_called_once_with(b"alice\r\n")

        # 2. Receive response
        protocol.data_received(b"Login: alice\r\n")
        protocol.data_received(b"Name: Alice Smith\r\n")

        # 3. Connection closes
        protocol.connection_lost(None)

        # 4. Verify response
        response = await future
        assert response.body == "Login: alice\r\nName: Alice Smith\r\n"
        assert response.host == "example.com"
        assert response.port == 79
        assert response.query == "alice"
        assert len(response.lines) == 2

    async def test_chunked_response_flow(self, mocker: MockerFixture) -> None:
        """Test receiving response in many small chunks."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol("alice", "example.com", 79, future)

        mock_transport = mocker.Mock()
        protocol.connection_made(mock_transport)

        # Receive data byte by byte
        message = b"Hello World\r\n"
        for byte in message:
            protocol.data_received(bytes([byte]))

        protocol.connection_lost(None)

        response = await future
        assert response.body == "Hello World\r\n"
