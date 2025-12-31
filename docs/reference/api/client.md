# Client API

The client module provides the high-level API for querying Finger servers.

## FingerClient

::: mapilli.client.session.FingerClient
    options:
      show_root_heading: true
      members:
        - __init__
        - query
        - finger
        - __aenter__
        - __aexit__

## Example Usage

### Basic Query

```python
from mapilli import FingerClient

async with FingerClient() as client:
    response = await client.query("alice@example.com")
    print(response.body)
```

### With Custom Timeout

```python
client = FingerClient(timeout=10.0)

async with client:
    response = await client.query("alice@example.com")
```

### Low-Level API

```python
async with FingerClient() as client:
    # Direct query to specific host
    response = await client.finger("example.com", query="alice")
```

### Error Handling

```python
async with FingerClient() as client:
    try:
        response = await client.query("alice@example.com")
    except TimeoutError:
        print("Request timed out")
    except ConnectionError:
        print("Connection failed")
    except ValueError:
        print("Invalid query")
```
