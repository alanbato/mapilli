"""Finger protocol request representation."""

from dataclasses import dataclass
from enum import Enum

from .constants import DEFAULT_PORT, VERBOSE_PREFIX


class QueryType(Enum):
    """Type of Finger query."""

    LIST_USERS = "list"  # Empty query - list all users
    USER_LOCAL = "user"  # Query user at local server
    USER_REMOTE = "remote"  # Query user at remote host (forwarding)
    HOST_ONLY = "host"  # Query host (forwarding, no user)


@dataclass(frozen=True)
class FingerRequest:
    """Represents a Finger protocol request.

    RFC 1288 Query Specification:
    {Q1} ::= [{W}|{W}{S}{U}]{C}
    {Q2} ::= [{W}{S}][{U}]{H}{C}
    {U}  ::= username
    {H}  ::= @hostname | @hostname{H}
    {W}  ::= /W
    {S}  ::= <SP> | <SP>{S}
    {C}  ::= <CRLF>

    Attributes:
        query: The raw query string (without CRLF).
        username: Username to query (may be empty).
        hostname: Target hostname.
        port: Target port.
        verbose: Whether verbose (/W) output is requested.
        query_type: Classification of the query type.
    """

    query: str
    username: str
    hostname: str
    port: int
    verbose: bool
    query_type: QueryType

    @classmethod
    def parse(
        cls,
        query: str,
        default_host: str | None = None,
        default_port: int = DEFAULT_PORT,
    ) -> "FingerRequest":
        """Parse a Finger query string.

        Args:
            query: Query string (e.g., "username", "@host", "user@host", "/W user")
            default_host: Default host if none specified in query
            default_port: Default port if none specified

        Returns:
            FingerRequest instance

        Raises:
            ValueError: If query format is invalid or no host available
        """
        original_query = query
        verbose = False
        username = ""
        hostname = default_host or ""
        port = default_port

        # Check for verbose prefix
        if query.startswith(VERBOSE_PREFIX):
            verbose = True
            query = query[len(VERBOSE_PREFIX) :].lstrip()

        # Parse the query
        if not query:
            # Empty query - list all users
            query_type = QueryType.LIST_USERS
        elif query.startswith("@"):
            # Host-only query: @hostname or @hostname@nexthost...
            hostname = query[1:]  # Remove leading @
            # Handle chained hosts (user@host1@host2)
            if "@" in hostname:
                # Keep as-is for forwarding
                pass
            query_type = QueryType.HOST_ONLY
        elif "@" in query:
            # User at remote host: user@host or user@host@nexthost
            parts = query.split("@", 1)
            username = parts[0]
            hostname = parts[1]
            query_type = QueryType.USER_REMOTE
        else:
            # Local user query
            username = query
            query_type = QueryType.USER_LOCAL

        # Build the wire query (what gets sent over the network)
        wire_query = original_query

        return cls(
            query=wire_query,
            username=username,
            hostname=hostname,
            port=port,
            verbose=verbose,
            query_type=query_type,
        )

    def to_wire(self) -> bytes:
        """Convert request to wire format (query + CRLF).

        Returns:
            Bytes ready to send over TCP
        """
        return (self.query + "\r\n").encode("ascii")

    @property
    def wire_query(self) -> str:
        """Get the query string to send for this request.

        For remote queries, this returns only the local part (user or /W user).
        The hostname is used for connection, not sent in the query.
        """
        if self.query_type == QueryType.LIST_USERS:
            return "/W" if self.verbose else ""
        elif self.query_type == QueryType.USER_LOCAL:
            return f"/W {self.username}" if self.verbose else self.username
        elif self.query_type == QueryType.USER_REMOTE:
            # For remote queries, send user@remaining_hosts
            if "@" in self.hostname:
                # Chained: alice@host1@host2 -> send alice@host2 to host1
                return self.query
            # Simple: alice@host -> send alice to host
            return f"/W {self.username}" if self.verbose else self.username
        else:  # HOST_ONLY
            return f"/W @{self.hostname}" if self.verbose else f"@{self.hostname}"

    @property
    def target_host(self) -> str:
        """Get the immediate target host to connect to."""
        if "@" in self.hostname:
            # For chained hosts, connect to first one
            return self.hostname.split("@")[0]
        return self.hostname
