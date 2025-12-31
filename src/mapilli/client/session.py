"""High-level Finger client API.

This module provides a high-level async/await interface for making
Finger requests, built on top of the low-level FingerClientProtocol.
"""

import asyncio

from ..protocol.constants import DEFAULT_PORT, DEFAULT_TIMEOUT
from ..protocol.request import FingerRequest
from ..protocol.response import FingerResponse
from .protocol import FingerClientProtocol


class FingerClient:
    """High-level Finger client with async/await API.

    This class provides a simple, high-level interface for querying Finger
    servers. It handles connection management, timeouts, and query parsing.

    Examples:
        >>> # Basic usage
        >>> async with FingerClient() as client:
        ...     response = await client.query("alice@example.com")
        ...     print(response.body)

        >>> # Query with verbose output
        >>> async with FingerClient() as client:
        ...     response = await client.query("/W alice", host="example.com")

        >>> # Direct host/port specification
        >>> client = FingerClient(timeout=10.0)
        >>> response = await client.finger("example.com", query="alice")
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Finger client.

        Args:
            timeout: Request timeout in seconds. Default is 30 seconds.
        """
        self.timeout = timeout

    async def __aenter__(self) -> "FingerClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        pass

    async def query(
        self,
        query_string: str = "",
        host: str | None = None,
        port: int = DEFAULT_PORT,
    ) -> FingerResponse:
        """Execute a Finger query.

        Parses the query string to extract username and optional host.
        If host is embedded in query (user@host), uses that host.
        Otherwise uses the provided host parameter.

        Args:
            query_string: Query string (e.g., "alice", "alice@host", "/W alice")
            host: Target host (used if not in query_string)
            port: Target port

        Returns:
            FingerResponse with query result

        Raises:
            ValueError: If no host specified and none in query
            TimeoutError: If request times out
            ConnectionError: If connection fails
        """
        # Parse the query
        request = FingerRequest.parse(
            query_string,
            default_host=host,
            default_port=port,
        )

        # Determine target host
        target_host = request.target_host
        if not target_host:
            raise ValueError("No host specified in query or as parameter")

        # Determine what query to send
        wire_query = request.wire_query

        return await self.finger(
            host=target_host,
            port=request.port,
            query=wire_query,
        )

    async def finger(
        self,
        host: str,
        query: str = "",
        port: int = DEFAULT_PORT,
    ) -> FingerResponse:
        """Execute a raw Finger query to a specific host.

        This is the low-level method that sends the query directly.

        Args:
            host: Target hostname
            query: Raw query string (sent as-is + CRLF)
            port: Target port

        Returns:
            FingerResponse with query result

        Raises:
            TimeoutError: If request times out
            ConnectionError: If connection fails
        """
        loop = asyncio.get_running_loop()
        response_future: asyncio.Future[FingerResponse] = loop.create_future()

        protocol = FingerClientProtocol(query, host, port, response_future)

        try:
            transport, _ = await asyncio.wait_for(
                loop.create_connection(
                    lambda: protocol,
                    host=host,
                    port=port,
                ),
                timeout=self.timeout,
            )
        except TimeoutError as e:
            raise TimeoutError(f"Connection timeout: {host}:{port}") from e
        except OSError as e:
            raise ConnectionError(f"Connection failed: {e}") from e

        try:
            response = await asyncio.wait_for(
                response_future,
                timeout=self.timeout,
            )
            return response
        except TimeoutError as e:
            raise TimeoutError(f"Request timeout: {host}:{port}") from e
        finally:
            transport.close()
