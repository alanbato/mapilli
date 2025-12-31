# Error Handling

This guide covers how to handle errors when using Mapilli.

## Error Types

Mapilli can raise three types of errors:

| Error | Cause | Recovery |
|-------|-------|----------|
| `TimeoutError` | Server didn't respond in time | Retry with longer timeout |
| `ConnectionError` | Network or server unreachable | Check connectivity, retry |
| `ValueError` | Invalid query format or missing host | Fix query string |

## Basic Error Handling

```python
from mapilli import FingerClient

async def safe_query(query: str) -> str | None:
    async with FingerClient(timeout=10.0) as client:
        try:
            response = await client.query(query)
            return response.body
        except TimeoutError:
            print("Request timed out")
            return None
        except ConnectionError as e:
            print(f"Connection failed: {e}")
            return None
        except ValueError as e:
            print(f"Invalid query: {e}")
            return None
```

## Retry Logic

For transient errors, implement retry logic:

```python
import asyncio
from mapilli import FingerClient

async def query_with_retry(
    query: str,
    max_retries: int = 3,
    delay: float = 1.0,
) -> str | None:
    """Query with exponential backoff retry."""
    async with FingerClient(timeout=10.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.query(query)
                return response.body
            except (TimeoutError, ConnectionError) as e:
                if attempt == max_retries - 1:
                    print(f"Failed after {max_retries} attempts: {e}")
                    return None
                wait = delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed, retrying in {wait}s...")
                await asyncio.sleep(wait)
            except ValueError as e:
                # Don't retry invalid queries
                print(f"Invalid query: {e}")
                return None
    return None
```

## Handling Multiple Queries

When querying multiple servers, use `asyncio.gather` with `return_exceptions=True`:

```python
import asyncio
from mapilli import FingerClient

async def query_all(queries: list[str]) -> dict[str, str | Exception]:
    """Query multiple servers, collecting all results."""
    async with FingerClient(timeout=10.0) as client:
        async def safe_query(q: str) -> tuple[str, str | Exception]:
            try:
                response = await client.query(q)
                return (q, response.body)
            except Exception as e:
                return (q, e)

        tasks = [safe_query(q) for q in queries]
        results = await asyncio.gather(*tasks)
        return dict(results)

# Usage
async def main():
    results = await query_all([
        "alice@server1.com",
        "bob@server2.com",
    ])

    for query, result in results.items():
        if isinstance(result, Exception):
            print(f"{query}: Error - {result}")
        else:
            print(f"{query}: {result[:50]}...")
```

## Custom Timeout Per Query

For different servers, you might need different timeouts:

```python
from mapilli import FingerClient

async def query_with_custom_timeout(
    query: str,
    timeout: float = 30.0,
) -> str | None:
    """Query with a custom timeout."""
    async with FingerClient(timeout=timeout) as client:
        try:
            response = await client.query(query)
            return response.body
        except TimeoutError:
            return None
```

## Logging Errors

Use structured logging for production:

```python
import structlog
from mapilli import FingerClient

log = structlog.get_logger()

async def logged_query(query: str) -> str | None:
    async with FingerClient(timeout=10.0) as client:
        try:
            response = await client.query(query)
            log.info("finger_query_success", query=query, bytes=len(response.body))
            return response.body
        except TimeoutError:
            log.warning("finger_query_timeout", query=query)
            return None
        except ConnectionError as e:
            log.error("finger_query_connection_error", query=query, error=str(e))
            return None
        except ValueError as e:
            log.error("finger_query_invalid", query=query, error=str(e))
            return None
```
