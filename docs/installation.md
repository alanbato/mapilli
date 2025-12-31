# Installation

Mapilli requires Python 3.10 or higher.

## Using pip

```bash
pip install mapilli
```

## Using uv

[uv](https://docs.astral.sh/uv/) is a fast Python package manager:

```bash
uv add mapilli
```

## From Source

Clone the repository and install with uv:

```bash
git clone https://github.com/alanbato/mapilli.git
cd mapilli
uv sync
```

## Verify Installation

After installation, verify that Mapilli is working:

=== "CLI"

    ```bash
    mapilli --version
    ```

=== "Python"

    ```python
    import mapilli
    print(mapilli.__version__)
    ```

## Dependencies

Mapilli has minimal dependencies:

- **rich** - Terminal formatting
- **structlog** - Structured logging
- **typer** - CLI framework

All dependencies are automatically installed when you install Mapilli.
