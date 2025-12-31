"""Mapilli Finger Protocol Client CLI.

This module provides a command-line interface for the Mapilli Finger client.
"""

import asyncio
from importlib.metadata import version as get_version
from typing import Annotated

import typer
from rich.console import Console

from .client.session import FingerClient
from .protocol.constants import DEFAULT_PORT, DEFAULT_TIMEOUT

console = Console()
error_console = Console(stderr=True, style="bold red")

app = typer.Typer(
    name="mapilli",
    help="Mapilli - A modern Finger protocol client",
    add_completion=True,
    no_args_is_help=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold cyan]Mapilli[/] {get_version('mapilli')}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    query: Annotated[
        str | None,
        typer.Argument(
            help="Query string (e.g., 'alice', 'alice@host', '@host', '/W alice')",
        ),
    ] = None,
    host: Annotated[
        str | None,
        typer.Option(
            "--host",
            "-h",
            help="Target host (required if not in query)",
        ),
    ] = None,
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            help="Target port",
        ),
    ] = DEFAULT_PORT,
    timeout: Annotated[
        float,
        typer.Option(
            "--timeout",
            "-t",
            help="Request timeout in seconds",
        ),
    ] = DEFAULT_TIMEOUT,
    whois: Annotated[
        bool,
        typer.Option(
            "--whois",
            "-W",
            help="Request verbose/whois output from server (/W prefix)",
        ),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """Query a Finger server.

    Examples:

        mapilli alice@example.com

        mapilli alice -h example.com

        mapilli -W alice@example.com

        mapilli -h example.com
    """
    # If no query and no host, show help
    if query is None and host is None:
        console.print(app.info.help or "Use --help for usage information")
        raise typer.Exit()

    async def _finger() -> None:
        try:
            # Build query with /W prefix if requested
            actual_query = query or ""
            if whois and not actual_query.startswith("/W"):
                actual_query = f"/W {actual_query}".strip()

            async with FingerClient(timeout=timeout) as client:
                response = await client.query(actual_query, host=host, port=port)
                console.print(response.body, end="")

        except ValueError as e:
            error_console.print(f"Error: {e}")
            raise typer.Exit(code=1) from e
        except TimeoutError as e:
            error_console.print(f"Timeout: {e}")
            raise typer.Exit(code=1) from e
        except ConnectionError as e:
            error_console.print(f"Connection error: {e}")
            raise typer.Exit(code=1) from e
        except Exception as e:
            error_console.print(f"Unexpected error: {e}")
            raise typer.Exit(code=1) from e

    asyncio.run(_finger())


if __name__ == "__main__":
    app()
