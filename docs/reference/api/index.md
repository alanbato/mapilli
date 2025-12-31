# API Reference

Mapilli provides a simple async API for querying Finger servers.

## Quick Reference

| Class | Description |
|-------|-------------|
| [`FingerClient`](client.md) | High-level async client |
| [`FingerRequest`](protocol.md#mapilli.protocol.request.FingerRequest) | Request representation |
| [`FingerResponse`](protocol.md#mapilli.protocol.response.FingerResponse) | Response representation |

## Basic Usage

```python
from mapilli import FingerClient

async with FingerClient() as client:
    response = await client.query("alice@example.com")
    print(response.body)
```

## Modules

- [Client](client.md) - `FingerClient` for making queries
- [Protocol](protocol.md) - Request and Response types
