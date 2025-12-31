"""Pytest configuration and shared fixtures for Mapilli tests."""

from __future__ import annotations

import asyncio
import socket
from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from mapilli.protocol.constants import DEFAULT_PORT

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def unused_tcp_port() -> int:
    """Get an unused TCP port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def mock_transport(mocker: MockerFixture):
    """Create a mock asyncio Transport for protocol testing."""
    transport = mocker.Mock()
    transport.write = mocker.Mock()
    transport.close = mocker.Mock()
    transport.is_closing = mocker.Mock(return_value=False)
    return transport


@pytest.fixture
def response_future() -> asyncio.Future:
    """Create a Future for protocol testing."""
    loop = asyncio.new_event_loop()
    future = loop.create_future()
    yield future
    loop.close()


@pytest.fixture
async def mock_finger_server(unused_tcp_port: int):
    """Create an in-process mock Finger server.

    This fixture creates a TCP server that speaks the Finger protocol.
    It accepts a query (terminated by CRLF) and returns a configurable response.

    Yields:
        tuple[int, Callable, Callable]: (port, set_response, set_default_response)
        - port: The TCP port the server is listening on
        - set_response: Function to set response for specific query
        - set_default_response: Function to set default response
    """
    responses: dict[str, str] = {"default": "No such user\r\n"}

    async def handle_client(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a single Finger client connection."""
        try:
            # Read query until CRLF (RFC 1288)
            data = await asyncio.wait_for(reader.readline(), timeout=5.0)
            query = data.decode("ascii").strip()

            # Get response (use query-specific or default)
            response = responses.get(query, responses["default"])

            # Send response
            writer.write(response.encode("ascii"))
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    def set_response(query: str, response: str) -> None:
        """Set the response for a specific query."""
        responses[query] = response

    def set_default_response(response: str) -> None:
        """Set the default response for unknown queries."""
        responses["default"] = response

    server = await asyncio.start_server(
        handle_client,
        "127.0.0.1",
        unused_tcp_port,
    )

    yield unused_tcp_port, set_response, set_default_response

    server.close()
    await server.wait_closed()


@pytest.fixture
async def slow_finger_server(unused_tcp_port: int):
    """Create a mock Finger server that responds slowly.

    Yields:
        tuple[int, Callable]: (port, set_delay)
        - port: The TCP port the server is listening on
        - set_delay: Function to set response delay in seconds
    """
    delay = 0.1  # Default delay

    async def handle_client(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle a single Finger client connection with delay."""
        try:
            _data = await asyncio.wait_for(reader.readline(), timeout=5.0)
            await asyncio.sleep(delay)
            writer.write(b"Delayed response\r\n")
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    def set_delay(new_delay: float) -> None:
        nonlocal delay
        delay = new_delay

    server = await asyncio.start_server(
        handle_client,
        "127.0.0.1",
        unused_tcp_port,
    )

    yield unused_tcp_port, set_delay

    server.close()
    await server.wait_closed()


@pytest.fixture
def sample_finger_responses() -> dict[str, str]:
    """Sample Finger protocol responses for testing."""
    return {
        "user_info": (
            "Login: alice\r\n"
            "Name: Alice Smith\r\n"
            "Directory: /home/alice\r\n"
            "Shell: /bin/bash\r\n"
            "Last login: Mon Dec 30 10:00:00 2025\r\n"
        ),
        "user_list": (
            "Login    Name               TTY       Idle    When    Where\r\n"
            "alice    Alice Smith        pts/0     0:05    Dec 30  192.168.1.1\r\n"
            "bob      Bob Jones          pts/1     1:30    Dec 30  10.0.0.1\r\n"
        ),
        "no_such_user": "finger: alice: no such user\r\n",
        "empty": "",
        "multiline": "Line 1\r\nLine 2\r\nLine 3\r\n",
    }
