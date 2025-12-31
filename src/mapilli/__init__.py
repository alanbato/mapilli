"""Mapilli - Modern Python asyncio Finger protocol client.

This library provides a modern, async-first implementation of the Finger
protocol (RFC 1288) for Python 3.10+.

Basic Usage:
    >>> import asyncio
    >>> from mapilli import FingerClient

    >>> async def main():
    ...     async with FingerClient() as client:
    ...         response = await client.query("alice@example.com")
    ...         print(response.body)

    >>> asyncio.run(main())

CLI Usage:
    $ mapilli alice@example.com
    $ mapilli -W alice -h example.com
"""

from .client.session import FingerClient
from .protocol.constants import DEFAULT_PORT, DEFAULT_TIMEOUT
from .protocol.request import FingerRequest, QueryType
from .protocol.response import FingerResponse

__all__ = [
    "FingerClient",
    "FingerRequest",
    "FingerResponse",
    "QueryType",
    "DEFAULT_PORT",
    "DEFAULT_TIMEOUT",
]

__version__ = "0.1.0"
