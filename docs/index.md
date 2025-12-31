# Mapilli

**Modern Python asyncio Finger protocol (RFC 1288) client library**

Mapilli is a modern, async-first implementation of the Finger protocol for Python 3.10+. It provides both a programmatic API and a command-line interface.

## Features

- **Async/await API** - Built on asyncio for non-blocking I/O
- **Simple CLI** - Query Finger servers from the command line
- **RFC 1288 compliant** - Full support for the Finger protocol specification
- **Type hints** - Full type annotations for better IDE support
- **Modern Python** - Requires Python 3.10+

## Quick Example

=== "CLI"

    ```bash
    # Query a user
    mapilli alice@example.com

    # List all users on a host
    mapilli -h example.com

    # Verbose/whois output
    mapilli -W alice@example.com
    ```

=== "Python"

    ```python
    import asyncio
    from mapilli import FingerClient

    async def main():
        async with FingerClient() as client:
            response = await client.query("alice@example.com")
            print(response.body)

    asyncio.run(main())
    ```

## Why Mapilli?

The Finger protocol (RFC 1288) is a simple protocol for querying user information on remote systems. While the protocol dates back to 1991, it's still used in certain environments and is a great example of simple network programming.

Mapilli brings the Finger protocol into the modern Python ecosystem with:

- **asyncio support** for efficient, non-blocking network operations
- **Type safety** with full type annotations
- **Clean API** inspired by modern Python libraries

## Getting Started

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install Mapilli with pip or uv

    [:octicons-arrow-right-24: Installation](installation.md)

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Get up and running in minutes

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

-   :material-book-open-variant:{ .lg .middle } **Tutorials**

    ---

    Step-by-step guides for common tasks

    [:octicons-arrow-right-24: Tutorials](tutorials/index.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete API documentation

    [:octicons-arrow-right-24: Reference](reference/index.md)

</div>

## License

MIT License - see [LICENSE](https://github.com/alanbato/mapilli/blob/main/LICENSE) for details.
