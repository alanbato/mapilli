"""Low-level Finger client protocol implementation.

This module implements the Finger client protocol using asyncio's
Protocol/Transport pattern for efficient, non-blocking I/O.
"""

import asyncio

from ..protocol.constants import MAX_RESPONSE_SIZE
from ..protocol.response import FingerResponse


class FingerClientProtocol(asyncio.Protocol):
    """Client-side protocol for making Finger requests.

    This class implements asyncio.Protocol for handling Finger client connections.
    It manages the connection lifecycle, sends requests, and accumulates responses.

    The protocol follows RFC 1288:
    1. Client connects via TCP to port 79
    2. Client sends query + CRLF
    3. Server sends response (plain text)
    4. Server closes connection

    Attributes:
        query: The query string being sent.
        host: Target host.
        port: Target port.
        response_future: Future that will be set with the FingerResponse.
        transport: The transport handling the connection.
        buffer: Buffer for accumulating incoming data.
    """

    def __init__(
        self,
        query: str,
        host: str,
        port: int,
        response_future: asyncio.Future[FingerResponse],
    ) -> None:
        """Initialize the client protocol.

        Args:
            query: The Finger query to send.
            host: Target hostname.
            port: Target port.
            response_future: Future to set with the final FingerResponse.
        """
        self.query = query
        self.host = host
        self.port = port
        self.response_future = response_future
        self.transport: asyncio.Transport | None = None
        self.buffer = b""

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when connection to server is established.

        Sends the Finger request (query + CRLF).
        """
        self.transport = transport  # type: ignore[assignment]

        # Send Finger request (query + CRLF)
        request = f"{self.query}\r\n"
        if self.transport:
            self.transport.write(request.encode("ascii"))

    def data_received(self, data: bytes) -> None:
        """Called when data is received from the server.

        Accumulates data in buffer. Response is complete when connection closes.
        """
        self.buffer += data

        # Check for excessive response size
        if len(self.buffer) > MAX_RESPONSE_SIZE:
            self._set_error(
                Exception(f"Response exceeds maximum size ({MAX_RESPONSE_SIZE} bytes)")
            )
            if self.transport:
                self.transport.close()

    def eof_received(self) -> bool:
        """Called when the server closes its write side."""
        return False  # Close our side too

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when the connection is closed.

        Sets the response result in the future.
        """
        if self.response_future.done():
            return

        if exc:
            self.response_future.set_exception(exc)
            return

        # Decode response body
        try:
            # RFC 1288: ASCII only, but be lenient with encoding
            body = self.buffer.decode("ascii", errors="replace")
        except Exception as e:
            self.response_future.set_exception(e)
            return

        # Create and set the response
        response = FingerResponse(
            body=body,
            host=self.host,
            port=self.port,
            query=self.query,
        )
        self.response_future.set_result(response)

    def _set_error(self, exc: Exception) -> None:
        """Set an error in the response future."""
        if not self.response_future.done():
            self.response_future.set_exception(exc)
