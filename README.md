# Mapilli

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://mapilli.readthedocs.io)

**Modern async Python client for the Finger protocol (RFC 1288)**

---

## What is this?

The [Finger protocol](https://www.rfc-editor.org/rfc/rfc1288.html) was the internet's original social network — a way to check if someone was online, read their status, and learn a bit about them. Think of it as the `.plan` file era's equivalent of checking someone's profile.

Mapilli brings this classic protocol into modern Python with a clean async API and a simple command-line tool. Whether you're exploring [tilde communities](https://tildeverse.org/), building retro-inspired status pages, or just learning about networking protocols, Mapilli makes it easy.

## Features

- **Modern async/await API** built on asyncio's Protocol/Transport pattern
- **Full RFC 1288 compliance** including query forwarding and verbose output
- **Both CLI and library** — use from the terminal or import into your code
- **Type hints throughout** for excellent IDE support
- **Flexible query syntax** — `user@host`, `@host`, `/W` verbose prefix
- **Concurrent queries** — query multiple hosts in parallel
- **Configurable timeouts** — don't wait forever for unresponsive servers

## Installation

```bash
pip install mapilli
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add mapilli
```

## Quick Start

### From the Command Line

```bash
# Query a user
mapilli alice@example.com

# Verbose output (more details)
mapilli -W alice@example.com

# List all users on a host
mapilli -h example.com

# Custom timeout
mapilli -t 10 alice@example.com
```

### From Python

```python
import asyncio
from mapilli import FingerClient

async def main():
    async with FingerClient() as client:
        # Query a user
        response = await client.query("alice@example.com")
        print(response.body)

        # Or specify host separately
        response = await client.query("alice", host="example.com")
        print(response.body)

asyncio.run(main())
```

### Concurrent Queries

```python
async with FingerClient() as client:
    queries = ["alice@host1.com", "bob@host2.com", "charlie@host3.com"]
    responses = await asyncio.gather(*[client.query(q) for q in queries])

    for response in responses:
        print(f"{response.host}: {response.body[:50]}...")
```

## Documentation

Full documentation is available at **[mapilli.readthedocs.io](https://mapilli.readthedocs.io)**:

- [Installation Guide](https://mapilli.readthedocs.io/installation/) — all the ways to install
- [Quick Start](https://mapilli.readthedocs.io/quickstart/) — get up and running fast
- [CLI Reference](https://mapilli.readthedocs.io/reference/cli/) — all command-line options
- [API Reference](https://mapilli.readthedocs.io/reference/api/) — complete Python API docs
- [The Finger Protocol](https://mapilli.readthedocs.io/explanation/finger-protocol/) — learn about RFC 1288

## License

MIT License — see [LICENSE.txt](LICENSE.txt) for details.
