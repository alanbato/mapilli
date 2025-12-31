"""Tests for FingerRequest parsing and wire format."""

import pytest

from mapilli.protocol.constants import DEFAULT_PORT
from mapilli.protocol.request import FingerRequest, QueryType


@pytest.mark.unit
class TestQueryType:
    """Test QueryType enum."""

    def test_query_type_values(self) -> None:
        """Test QueryType enum has expected values."""
        assert QueryType.LIST_USERS.value == "list"
        assert QueryType.USER_LOCAL.value == "user"
        assert QueryType.USER_REMOTE.value == "remote"
        assert QueryType.HOST_ONLY.value == "host"

    def test_query_type_count(self) -> None:
        """Test QueryType has exactly 4 values."""
        assert len(QueryType) == 4


@pytest.mark.unit
class TestFingerRequestParseEmptyQuery:
    """Test FingerRequest.parse() with empty queries (LIST_USERS)."""

    def test_parse_empty_query(self) -> None:
        """Empty query should result in LIST_USERS type."""
        request = FingerRequest.parse("", default_host="example.com")

        assert request.query_type == QueryType.LIST_USERS
        assert request.username == ""
        assert request.hostname == "example.com"
        assert request.verbose is False

    def test_parse_empty_query_no_default_host(self) -> None:
        """Empty query without default host results in empty hostname."""
        request = FingerRequest.parse("")

        assert request.query_type == QueryType.LIST_USERS
        assert request.hostname == ""

    def test_parse_verbose_empty(self) -> None:
        """Verbose prefix with empty query."""
        request = FingerRequest.parse("/W", default_host="example.com")

        assert request.query_type == QueryType.LIST_USERS
        assert request.verbose is True
        assert request.username == ""


@pytest.mark.unit
class TestFingerRequestParseLocalUser:
    """Test FingerRequest.parse() with local user queries (USER_LOCAL)."""

    def test_parse_username_only(self) -> None:
        """Simple username should result in USER_LOCAL type."""
        request = FingerRequest.parse("alice", default_host="example.com")

        assert request.query_type == QueryType.USER_LOCAL
        assert request.username == "alice"
        assert request.hostname == "example.com"
        assert request.verbose is False

    def test_parse_verbose_username(self) -> None:
        """Verbose prefix with username."""
        request = FingerRequest.parse("/W alice", default_host="example.com")

        assert request.query_type == QueryType.USER_LOCAL
        assert request.username == "alice"
        assert request.verbose is True

    def test_parse_verbose_with_spaces(self) -> None:
        """Verbose prefix with multiple spaces before username."""
        request = FingerRequest.parse("/W   alice", default_host="example.com")

        assert request.query_type == QueryType.USER_LOCAL
        assert request.username == "alice"
        assert request.verbose is True


@pytest.mark.unit
class TestFingerRequestParseRemoteUser:
    """Test FingerRequest.parse() with remote user queries (USER_REMOTE)."""

    def test_parse_user_at_host(self) -> None:
        """user@host format should result in USER_REMOTE type."""
        request = FingerRequest.parse("alice@remotehost.com")

        assert request.query_type == QueryType.USER_REMOTE
        assert request.username == "alice"
        assert request.hostname == "remotehost.com"
        assert request.verbose is False

    def test_parse_user_at_host_overrides_default(self) -> None:
        """Host in query should override default_host."""
        request = FingerRequest.parse(
            "alice@remotehost.com", default_host="example.com"
        )

        assert request.hostname == "remotehost.com"

    def test_parse_verbose_user_at_host(self) -> None:
        """Verbose prefix with user@host."""
        request = FingerRequest.parse("/W alice@remotehost.com")

        assert request.query_type == QueryType.USER_REMOTE
        assert request.username == "alice"
        assert request.hostname == "remotehost.com"
        assert request.verbose is True

    def test_parse_user_chained_hosts(self) -> None:
        """User with chained hosts: alice@host1@host2."""
        request = FingerRequest.parse("alice@host1@host2")

        assert request.query_type == QueryType.USER_REMOTE
        assert request.username == "alice"
        assert request.hostname == "host1@host2"

    def test_parse_user_multiple_chained_hosts(self) -> None:
        """User with multiple chained hosts: alice@host1@host2@host3."""
        request = FingerRequest.parse("alice@host1@host2@host3")

        assert request.query_type == QueryType.USER_REMOTE
        assert request.username == "alice"
        assert request.hostname == "host1@host2@host3"


@pytest.mark.unit
class TestFingerRequestParseHostOnly:
    """Test FingerRequest.parse() with host-only queries (HOST_ONLY)."""

    def test_parse_at_host(self) -> None:
        """@host format should result in HOST_ONLY type."""
        request = FingerRequest.parse("@remotehost.com")

        assert request.query_type == QueryType.HOST_ONLY
        assert request.username == ""
        assert request.hostname == "remotehost.com"
        assert request.verbose is False

    def test_parse_verbose_at_host(self) -> None:
        """Verbose prefix with @host."""
        request = FingerRequest.parse("/W @remotehost.com")

        assert request.query_type == QueryType.HOST_ONLY
        assert request.hostname == "remotehost.com"
        assert request.verbose is True

    def test_parse_chained_hosts_only(self) -> None:
        """Chained hosts without user: @host1@host2."""
        request = FingerRequest.parse("@host1@host2")

        assert request.query_type == QueryType.HOST_ONLY
        assert request.username == ""
        assert request.hostname == "host1@host2"


@pytest.mark.unit
class TestFingerRequestParsePort:
    """Test FingerRequest.parse() port handling."""

    def test_parse_default_port(self) -> None:
        """Default port should be 79."""
        request = FingerRequest.parse("alice", default_host="example.com")

        assert request.port == DEFAULT_PORT
        assert request.port == 79

    def test_parse_custom_port(self) -> None:
        """Custom port parameter should be used."""
        request = FingerRequest.parse(
            "alice", default_host="example.com", default_port=8079
        )

        assert request.port == 8079


@pytest.mark.unit
class TestFingerRequestWireQuery:
    """Test FingerRequest.wire_query property."""

    def test_wire_query_list_users(self) -> None:
        """LIST_USERS sends empty string."""
        request = FingerRequest.parse("", default_host="example.com")

        assert request.wire_query == ""

    def test_wire_query_list_users_verbose(self) -> None:
        """LIST_USERS verbose sends /W."""
        request = FingerRequest.parse("/W", default_host="example.com")

        assert request.wire_query == "/W"

    def test_wire_query_user_local(self) -> None:
        """USER_LOCAL sends username."""
        request = FingerRequest.parse("alice", default_host="example.com")

        assert request.wire_query == "alice"

    def test_wire_query_user_local_verbose(self) -> None:
        """USER_LOCAL verbose sends /W username."""
        request = FingerRequest.parse("/W alice", default_host="example.com")

        assert request.wire_query == "/W alice"

    def test_wire_query_user_remote_simple(self) -> None:
        """USER_REMOTE simple sends username only (not user@host)."""
        request = FingerRequest.parse("alice@host.com")

        # When querying alice@host.com, we connect to host.com
        # and send just "alice"
        assert request.wire_query == "alice"

    def test_wire_query_user_remote_simple_verbose(self) -> None:
        """USER_REMOTE simple verbose sends /W username."""
        request = FingerRequest.parse("/W alice@host.com")

        assert request.wire_query == "/W alice"

    def test_wire_query_user_remote_chained(self) -> None:
        """USER_REMOTE chained sends full query for forwarding."""
        request = FingerRequest.parse("alice@host1@host2")

        # For chained hosts, we send the full query to the first host
        # which then forwards it
        assert request.wire_query == "alice@host1@host2"

    def test_wire_query_host_only(self) -> None:
        """HOST_ONLY sends @hostname."""
        request = FingerRequest.parse("@remotehost.com")

        assert request.wire_query == "@remotehost.com"

    def test_wire_query_host_only_verbose(self) -> None:
        """HOST_ONLY verbose sends /W @hostname."""
        request = FingerRequest.parse("/W @remotehost.com")

        assert request.wire_query == "/W @remotehost.com"


@pytest.mark.unit
class TestFingerRequestTargetHost:
    """Test FingerRequest.target_host property."""

    def test_target_host_simple(self) -> None:
        """Simple hostname returns as-is."""
        request = FingerRequest.parse("alice@example.com")

        assert request.target_host == "example.com"

    def test_target_host_from_default(self) -> None:
        """Target host from default_host."""
        request = FingerRequest.parse("alice", default_host="example.com")

        assert request.target_host == "example.com"

    def test_target_host_chained(self) -> None:
        """Chained hosts returns first host."""
        request = FingerRequest.parse("alice@host1@host2")

        assert request.target_host == "host1"

    def test_target_host_chained_multiple(self) -> None:
        """Multiple chained hosts returns first host."""
        request = FingerRequest.parse("alice@host1@host2@host3")

        assert request.target_host == "host1"

    def test_target_host_host_only_chained(self) -> None:
        """HOST_ONLY chained returns first host."""
        request = FingerRequest.parse("@host1@host2")

        assert request.target_host == "host1"


@pytest.mark.unit
class TestFingerRequestToWire:
    """Test FingerRequest.to_wire() method."""

    def test_to_wire_adds_crlf(self) -> None:
        """to_wire() should append CRLF."""
        request = FingerRequest.parse("alice", default_host="example.com")

        wire = request.to_wire()

        assert wire.endswith(b"\r\n")

    def test_to_wire_encodes_ascii(self) -> None:
        """to_wire() should encode as ASCII bytes."""
        request = FingerRequest.parse("alice", default_host="example.com")

        wire = request.to_wire()

        assert isinstance(wire, bytes)
        # The query is stored as the original input
        assert b"alice\r\n" == wire

    def test_to_wire_verbose_query(self) -> None:
        """to_wire() with verbose query."""
        request = FingerRequest.parse("/W alice", default_host="example.com")

        wire = request.to_wire()

        assert wire == b"/W alice\r\n"

    def test_to_wire_empty_query(self) -> None:
        """to_wire() with empty query sends just CRLF."""
        request = FingerRequest.parse("", default_host="example.com")

        wire = request.to_wire()

        assert wire == b"\r\n"


@pytest.mark.unit
class TestFingerRequestFrozen:
    """Test FingerRequest is frozen dataclass."""

    def test_request_is_immutable(self) -> None:
        """Request attributes cannot be modified after creation."""
        request = FingerRequest.parse("alice", default_host="example.com")

        with pytest.raises(AttributeError):
            request.username = "bob"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            request.hostname = "other.com"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            request.verbose = True  # type: ignore[misc]
