# Building a Finger Client

In this tutorial, you'll learn how to build a complete Finger client application using Mapilli.

## Prerequisites

- Python 3.10 or higher
- Mapilli installed (`pip install mapilli`)

## What We'll Build

We'll create a simple script that:

1. Queries a Finger server for user information
2. Handles errors gracefully
3. Formats the output nicely

## Step 1: Basic Query

Let's start with the simplest possible client:

```python
import asyncio
from mapilli import FingerClient

async def main():
    async with FingerClient() as client:
        response = await client.query("alice@example.com")
        print(response.body)

if __name__ == "__main__":
    asyncio.run(main())
```

This creates a `FingerClient`, queries a user, and prints the response.

## Step 2: Add Error Handling

Real applications need to handle errors:

```python
import asyncio
from mapilli import FingerClient

async def finger_user(query: str) -> str | None:
    """Query a Finger server and return the response."""
    async with FingerClient(timeout=10.0) as client:
        try:
            response = await client.query(query)
            return response.body
        except TimeoutError:
            print(f"Error: Request timed out for {query}")
            return None
        except ConnectionError as e:
            print(f"Error: Could not connect - {e}")
            return None
        except ValueError as e:
            print(f"Error: Invalid query - {e}")
            return None

async def main():
    result = await finger_user("alice@example.com")
    if result:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 3: Query Multiple Users

Use `asyncio.gather` to query multiple users concurrently:

```python
import asyncio
from mapilli import FingerClient

async def finger_user(client: FingerClient, query: str) -> tuple[str, str | None]:
    """Query a user and return (query, result) tuple."""
    try:
        response = await client.query(query)
        return (query, response.body)
    except Exception as e:
        return (query, f"Error: {e}")

async def main():
    users = [
        "alice@example.com",
        "bob@example.com",
        "charlie@example.com",
    ]

    async with FingerClient(timeout=10.0) as client:
        tasks = [finger_user(client, user) for user in users]
        results = await asyncio.gather(*tasks)

    for query, result in results:
        print(f"=== {query} ===")
        print(result)
        print()

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 4: Format Output

Let's add some formatting with Rich:

```python
import asyncio
from mapilli import FingerClient
from rich.console import Console
from rich.panel import Panel

console = Console()

async def finger_user(client: FingerClient, query: str) -> tuple[str, str]:
    """Query a user and return (query, result) tuple."""
    try:
        response = await client.query(query)
        return (query, response.body)
    except TimeoutError:
        return (query, "[red]Request timed out[/red]")
    except ConnectionError as e:
        return (query, f"[red]Connection failed: {e}[/red]")
    except ValueError as e:
        return (query, f"[yellow]Invalid query: {e}[/yellow]")

async def main():
    users = [
        "alice@example.com",
        "bob@example.com",
    ]

    async with FingerClient(timeout=10.0) as client:
        tasks = [finger_user(client, user) for user in users]
        results = await asyncio.gather(*tasks)

    for query, result in results:
        console.print(Panel(result, title=query))

if __name__ == "__main__":
    asyncio.run(main())
```

## Complete Example

Here's the complete application:

```python
#!/usr/bin/env python3
"""A simple Finger client application."""

import asyncio
import sys
from mapilli import FingerClient
from rich.console import Console
from rich.panel import Panel

console = Console()

async def finger_user(client: FingerClient, query: str) -> tuple[str, str]:
    """Query a user and return (query, result) tuple."""
    try:
        response = await client.query(query)
        return (query, response.body)
    except TimeoutError:
        return (query, "[red]Request timed out[/red]")
    except ConnectionError as e:
        return (query, f"[red]Connection failed: {e}[/red]")
    except ValueError as e:
        return (query, f"[yellow]Invalid query: {e}[/yellow]")

async def main(queries: list[str]) -> None:
    """Query multiple users and display results."""
    async with FingerClient(timeout=10.0) as client:
        tasks = [finger_user(client, query) for query in queries]
        results = await asyncio.gather(*tasks)

    for query, result in results:
        console.print(Panel(result, title=query))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python client.py user@host ...[/yellow]")
        sys.exit(1)

    asyncio.run(main(sys.argv[1:]))
```

## Next Steps

- Learn about [Error Handling](../how-to/error-handling.md) best practices
- Explore the [API Reference](../reference/api/client.md)
- Understand the [Finger Protocol](../explanation/finger-protocol.md)
