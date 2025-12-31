# Quick Start

This guide will get you up and running with Mapilli in just a few minutes.

## Command Line

After [installation](installation.md), the `mapilli` command is available.

### Query a User

```bash
mapilli alice@example.com
```

### Query with Separate Host

```bash
mapilli alice -h example.com
```

### List All Users

Query without a username to list all users:

```bash
mapilli -h example.com
```

### Verbose Output

Request verbose (whois-style) output:

```bash
mapilli -W alice@example.com
```

## Python API

### Basic Usage

```python
import asyncio
from mapilli import FingerClient

async def main():
    async with FingerClient() as client:
        response = await client.query("alice@example.com")
        print(response.body)

asyncio.run(main())
```

### Query Options

```python
async with FingerClient() as client:
    # Host in query string
    response = await client.query("alice@example.com")

    # Separate host parameter
    response = await client.query("alice", host="example.com")

    # List all users
    response = await client.query(host="example.com")

    # Verbose output
    response = await client.query("/W alice@example.com")
```

### Custom Timeout

```python
client = FingerClient(timeout=10.0)

async with client:
    response = await client.query("alice@example.com")
```

### Error Handling

```python
async with FingerClient(timeout=5.0) as client:
    try:
        response = await client.query("alice@example.com")
        print(response.body)
    except TimeoutError:
        print("Request timed out")
    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except ValueError as e:
        print(f"Invalid query: {e}")
```

## Next Steps

- Learn more in the [Tutorials](tutorials/index.md)
- See the [CLI Reference](reference/cli.md) for all options
- Explore the [API Reference](reference/api/index.md)
