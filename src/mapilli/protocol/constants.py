"""Finger protocol constants per RFC 1288."""

DEFAULT_PORT = 79
"""Default TCP port for Finger protocol."""

MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10 MB
"""Maximum response size (protection against malicious servers)."""

DEFAULT_TIMEOUT = 30.0
"""Default request timeout in seconds."""

CRLF = b"\r\n"
"""Carriage Return Line Feed - protocol line terminator."""

VERBOSE_PREFIX = "/W"
"""Prefix for verbose (Whois-style) output."""
