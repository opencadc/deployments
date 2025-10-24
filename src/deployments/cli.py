#!/usr/bin/env python3
"""Main CLI application for deployments management.

This module provides the main CLI entry point for the deployments package,
using Typer to create a modern, user-friendly command-line interface.

Examples:
    View all available commands:

    .. code-block:: bash

        deploy --help

    Get help for a specific command:

    .. code-block:: bash

        deploy release-matrix --help

Notes:
    - The CLI is registered as 'deploy' in pyproject.toml
    - Subcommands are organized by functionality
    - All commands follow consistent naming and argument patterns
"""

from __future__ import annotations

import typer

# Create the main Typer app
app = typer.Typer(
    name="deploy",
    help="Deployment management CLI for Helm charts and releases.",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:
    """Print version information and exit.

    Args:
        value: Whether the version flag was set

    Examples:
        .. code-block:: bash

            deploy --version
    """
    if value:
        from importlib.metadata import version

        pkg_version = version("deployments")
        typer.echo(f"deployments version {pkg_version}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Deployment management CLI for Helm charts and releases.

    This CLI provides tools for managing Helm chart deployments, building
    release matrices, and automating deployment workflows.

    Examples:
        View all available commands:

        .. code-block:: bash

            deploy --help

        Get help for a specific command:

        .. code-block:: bash

            deploy release-matrix --help
    """
    pass


# Import and register subcommands
# This is done at the end to avoid circular imports
from deployments.release_matrix import app as release_matrix_app

app.add_typer(release_matrix_app, name="release-matrix")


if __name__ == "__main__":
    app()
