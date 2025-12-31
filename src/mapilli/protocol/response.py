"""Finger protocol response representation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FingerResponse:
    """Represents a Finger protocol response.

    Per RFC 1288, responses are plain ASCII text with lines ending in CRLF.
    The connection closes after the response is complete.

    Attributes:
        body: The response text content.
        host: The host that was queried.
        port: The port used for the query.
        query: The original query string.
    """

    body: str
    host: str
    port: int
    query: str

    @property
    def lines(self) -> list[str]:
        """Get response as list of lines."""
        return self.body.splitlines()

    def __str__(self) -> str:
        """Human-readable representation."""
        return self.body
