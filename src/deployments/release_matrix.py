#!/usr/bin/env python3
"""Build release matrix from release-please outputs for GitHub Actions.

This script processes the outputs from the release-please GitHub Action and
generates a matrix of releases that can be used in subsequent workflow jobs.

Examples:
    Basic usage with environment variables:

    >>> import os
    >>> os.environ['PATHS_RELEASED'] = '["helm/applications/skaha"]'
    >>> os.environ['RELEASE_PLEASE_OUTPUTS'] = '{"helm/applications/skaha--version": "1.0.0"}'
    >>> matrix = build_release_matrix()
    >>> len(matrix)
    1

    Command-line usage:

    .. code-block:: bash

        deploy release-matrix build \\
            --paths-released '["helm/applications/skaha"]' \\
            --outputs '{"helm/applications/skaha--version": "1.0.0", ...}'

Notes:
    - The script reads release-please-config.json from the repository root
    - Release-please outputs use path with '--' separator for fields
      (e.g., 'helm/applications/skaha--version')
    - The matrix includes chart name, path, version, tag, and SHA for each release
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Annotated, Any, Optional

import typer


def _discover_repo_root() -> Path:
    """Return the repository root by walking up from this module.

    Returns:
        Path: The repository root directory containing release-please-config.json

    Examples:
        >>> root = _discover_repo_root()
        >>> (root / "release-please-config.json").exists()
        True
    """
    module_path = Path(__file__).resolve()
    for candidate in module_path.parents:
        if (candidate / "release-please-config.json").exists():
            return candidate
    return Path.cwd().resolve()


REPO_ROOT = _discover_repo_root()


def load_release_please_config() -> dict[str, Any]:
    """Load the release-please configuration file.

    Returns:
        dict[str, Any]: The parsed release-please configuration

    Raises:
        FileNotFoundError: If release-please-config.json is not found
        json.JSONDecodeError: If the config file is not valid JSON

    Examples:
        >>> config = load_release_please_config()
        >>> 'packages' in config
        True
    """
    config_file = REPO_ROOT / "release-please-config.json"
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    return json.loads(config_file.read_text())


def normalize_path_to_output_key(path: str) -> str:
    """Convert a path to the output key format used by release-please.

    Release-please uses the path as-is in output keys (with forward slashes).

    Args:
        path: The chart path (e.g., 'helm/applications/skaha')

    Returns:
        str: The output key prefix (same as input path)

    Examples:
        >>> normalize_path_to_output_key('helm/applications/skaha')
        'helm/applications/skaha'
        >>> normalize_path_to_output_key('helm/common')
        'helm/common'

    Notes:
        Release-please output format uses the path directly, e.g.:
        - 'helm/applications/skaha--version'
        - 'helm/applications/skaha--tag_name'
        - 'helm/applications/skaha--sha'
    """
    return path


def build_release_matrix(
    paths_released: list[str] | None = None,
    release_outputs: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    """Build the release matrix from release-please outputs.

    Args:
        paths_released: List of paths that had releases created. If None, reads from
            PATHS_RELEASED environment variable.
        release_outputs: Dictionary of all release-please outputs. If None, reads from
            RELEASE_PLEASE_OUTPUTS environment variable.

    Returns:
        list[dict[str, str]]: A list of release entries, each containing:
            - chart_name: The package name from config
            - chart_path: The path to the chart
            - chart_version: The version number
            - tag_name: The git tag name
            - sha: The commit SHA
            - output_key: The normalized output key

    Raises:
        ValueError: If required environment variables are missing when args are None
        KeyError: If a path is not found in the release-please config

    Examples:
        >>> paths = ["helm/applications/skaha"]
        >>> outputs = {
        ...     "helm/applications/skaha--version": "1.0.0",
        ...     "helm/applications/skaha--tag_name": "skaha-1.0.0",
        ...     "helm/applications/skaha--sha": "abc123"
        ... }
        >>> matrix = build_release_matrix(paths, outputs)
        >>> matrix[0]['chart_name']
        'skaha'
        >>> matrix[0]['chart_version']
        '1.0.0'

    Notes:
        Release-please output format uses the path directly with '--' separator
        for field names, e.g., 'helm/applications/skaha--version' not
        'helm--applications--skaha--version'.
    """
    # Load inputs from environment if not provided
    if paths_released is None:
        paths_json = os.environ.get("PATHS_RELEASED")
        if not paths_json:
            raise ValueError("PATHS_RELEASED environment variable is required")
        paths_released = json.loads(paths_json)

    if release_outputs is None:
        outputs_json = os.environ.get("RELEASE_PLEASE_OUTPUTS")
        if not outputs_json:
            raise ValueError("RELEASE_PLEASE_OUTPUTS environment variable is required")
        release_outputs = json.loads(outputs_json)

    # Load release-please config
    config = load_release_please_config()
    packages = config.get("packages", {})

    # Build the matrix
    matrix: list[dict[str, str]] = []

    for path in paths_released:
        # Get package config
        package_config = packages.get(path)
        if not package_config:
            sys.stderr.write(f"Warning: No package config found for path: {path}\n")
            continue

        package_name = package_config.get("package-name", "")
        if not package_name:
            sys.stderr.write(f"Warning: No package-name found for path: {path}\n")
            continue

        # Normalize path for output key
        output_key = normalize_path_to_output_key(path)

        # Extract release outputs for this path
        version = release_outputs.get(f"{output_key}--version", "")
        tag_name = release_outputs.get(f"{output_key}--tag_name", "")
        sha = release_outputs.get(f"{output_key}--sha", "")

        # Add to matrix
        matrix.append(
            {
                "chart_name": package_name,
                "chart_path": path,
                "chart_version": version,
                "tag_name": tag_name,
                "sha": sha,
                "output_key": output_key,
            }
        )

    return matrix


# Create Typer app for release-matrix subcommand
app = typer.Typer(
    name="release-matrix",
    help="Build release matrix from release-please outputs.",
    add_completion=False,
    no_args_is_help=True,
)


@app.command(name="build")
def build_matrix_cli(
    paths_released: Annotated[
        Optional[str],
        typer.Option(
            "--paths-released",
            help="JSON array of paths that had releases created (default: from PATHS_RELEASED env var)",
        ),
    ] = None,
    outputs: Annotated[
        Optional[str],
        typer.Option(
            "--outputs",
            help="JSON object of all release-please outputs (default: from RELEASE_PLEASE_OUTPUTS env var)",
        ),
    ] = None,
    output_file: Annotated[
        Optional[Path],
        typer.Option(
            "--output-file",
            help="Optional file to write the matrix JSON (default: stdout)",
        ),
    ] = None,
) -> None:
    """Build release matrix from release-please outputs for GitHub Actions.

    Reads inputs from command-line arguments or environment variables and outputs
    the release matrix as JSON to stdout. Also sets GITHUB_OUTPUT if running in
    GitHub Actions.

    Examples:
        Command-line usage:

        .. code-block:: bash

            deploy release-matrix build \\
                --paths-released '["helm/applications/skaha"]' \\
                --outputs '{"helm/applications/skaha--version": "1.0.0"}'

        GitHub Actions usage:

        .. code-block:: bash

            export PATHS_RELEASED='["helm/applications/skaha"]'
            export RELEASE_PLEASE_OUTPUTS='{"helm/applications/skaha--version": "1.0.0"}'
            deploy release-matrix build
    """
    # Parse inputs
    paths_released_list = json.loads(paths_released) if paths_released else None
    release_outputs_dict = json.loads(outputs) if outputs else None

    try:
        # Build the matrix
        matrix = build_release_matrix(paths_released_list, release_outputs_dict)

        # Output the matrix
        matrix_json = json.dumps(matrix, indent=2)

        # Print to stdout
        typer.echo(f"Release matrix ({len(matrix)} releases):")
        typer.echo(matrix_json)

        # Write to file if specified
        if output_file:
            output_file.write_text(matrix_json + "\n")
            typer.echo(f"\nMatrix written to: {output_file}")

        # Set GitHub Actions output if running in Actions
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                # Use compact JSON for GitHub Actions
                compact_json = json.dumps(matrix)
                f.write(f"matrix={compact_json}\n")
            typer.echo(f"\nGitHub Actions output set: matrix={compact_json}")

    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
