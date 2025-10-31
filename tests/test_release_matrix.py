"""Integration tests for release matrix functionality.

This module contains integration tests for the release matrix building
functionality, testing the complete workflow from inputs to outputs.

Notes:
    - Tests focus on integration rather than unit testing
    - Uses pytest fixtures for common test data
    - Tests both programmatic API and CLI interface
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from deployments.cli import app
from deployments.release_matrix import build_release_matrix


@pytest.fixture
def sample_paths_released() -> list[str]:
    """Provide sample paths for testing.

    Returns:
        List of sample Helm chart paths that were released.
    """
    return ["helm/applications/skaha", "helm/common"]


@pytest.fixture
def sample_release_outputs() -> dict[str, str]:
    """Provide sample release-please outputs for testing.

    Returns:
        Dictionary of release-please outputs with version, tag, and SHA info.

    Notes:
        Release-please uses the path directly with '--' separator for fields,
        e.g., 'helm/applications/skaha--version' not 'helm--applications--skaha--version'.
    """
    return {
        "helm/applications/skaha--version": "1.2.3",
        "helm/applications/skaha--tag_name": "skaha-1.2.3",
        "helm/applications/skaha--sha": "abc123def456",
        "helm/common--version": "2.0.0",
        "helm/common--tag_name": "common-2.0.0",
        "helm/common--sha": "def456abc123",
    }


@pytest.fixture
def expected_matrix() -> list[dict[str, str]]:
    """Provide expected matrix output for testing.

    Returns:
        Expected release matrix structure.

    Notes:
        The output_key is the same as the chart_path (release-please uses
        the path directly, not a normalized version).
    """
    return [
        {
            "chart_name": "skaha",
            "chart_path": "helm/applications/skaha",
            "chart_version": "1.2.3",
            "tag_name": "skaha-1.2.3",
            "sha": "abc123def456",
            "output_key": "helm/applications/skaha", #gitleaks:allow
        },
        {
            "chart_name": "common",
            "chart_path": "helm/common",
            "chart_version": "2.0.0",
            "tag_name": "common-2.0.0",
            "sha": "def456abc123",
            "output_key": "helm/common", #gitleaks:allow
        },
    ]


def test_build_release_matrix_with_direct_inputs(
    sample_paths_released: list[str],
    sample_release_outputs: dict[str, str],
    expected_matrix: list[dict[str, str]],
) -> None:
    """Test building release matrix with direct function inputs.

    This integration test verifies that the build_release_matrix function
    correctly processes release-please outputs and generates the expected
    matrix structure.

    Args:
        sample_paths_released: Fixture providing sample paths.
        sample_release_outputs: Fixture providing sample outputs.
        expected_matrix: Fixture providing expected result.
    """
    # Act
    result = build_release_matrix(sample_paths_released, sample_release_outputs)

    # Assert
    assert len(result) == 2
    assert result == expected_matrix
    assert result[0]["chart_name"] == "skaha"
    assert result[1]["chart_name"] == "common"


def test_build_release_matrix_with_environment_variables(
    sample_paths_released: list[str],
    sample_release_outputs: dict[str, str],
    expected_matrix: list[dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test building release matrix using environment variables.

    This integration test verifies that the function correctly reads from
    environment variables when no direct inputs are provided, simulating
    the GitHub Actions workflow behavior.

    Args:
        sample_paths_released: Fixture providing sample paths.
        sample_release_outputs: Fixture providing sample outputs.
        expected_matrix: Fixture providing expected result.
        monkeypatch: Pytest fixture for modifying environment.
    """
    # Arrange
    monkeypatch.setenv("PATHS_RELEASED", json.dumps(sample_paths_released))
    monkeypatch.setenv("RELEASE_PLEASE_OUTPUTS", json.dumps(sample_release_outputs))

    # Act
    result = build_release_matrix()

    # Assert
    assert len(result) == 2
    assert result == expected_matrix


def test_cli_build_command_with_arguments() -> None:
    """Test the CLI build command with command-line arguments.

    This integration test verifies that the Typer CLI correctly processes
    command-line arguments and produces the expected JSON output.

    Notes:
        Uses the actual release-please output format with path containing
        forward slashes, e.g., 'helm/applications/skaha--version'.
    """
    # Arrange
    runner = CliRunner()
    paths = '["helm/applications/skaha"]'
    outputs = json.dumps(
        {
            "helm/applications/skaha--version": "1.0.0",
            "helm/applications/skaha--tag_name": "skaha-1.0.0",
            "helm/applications/skaha--sha": "abc123",
        }
    )

    # Act
    result = runner.invoke(
        app,
        [
            "release-matrix",
            "build",
            "--paths-released",
            paths,
            "--outputs",
            outputs,
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert "Release matrix (1 releases):" in result.stdout
    assert '"chart_name": "skaha"' in result.stdout
    assert '"chart_version": "1.0.0"' in result.stdout
    assert '"tag_name": "skaha-1.0.0"' in result.stdout


def test_cli_build_command_with_output_file(tmp_path: Path) -> None:
    """Test the CLI build command with file output.

    This integration test verifies that the CLI correctly writes the matrix
    to a file when the --output-file option is provided.

    Args:
        tmp_path: Pytest fixture providing temporary directory.

    Notes:
        Uses the actual release-please output format with path containing
        forward slashes, e.g., 'helm/common--version'.
    """
    # Arrange
    runner = CliRunner()
    output_file = tmp_path / "matrix.json"
    paths = '["helm/common"]'
    outputs = json.dumps(
        {
            "helm/common--version": "2.0.0",
            "helm/common--tag_name": "common-2.0.0",
            "helm/common--sha": "def456",
        }
    )

    # Act
    result = runner.invoke(
        app,
        [
            "release-matrix",
            "build",
            "--paths-released",
            paths,
            "--outputs",
            outputs,
            "--output-file",
            str(output_file),
        ],
    )

    # Assert
    assert result.exit_code == 0
    assert output_file.exists()

    # Verify file contents
    matrix_data = json.loads(output_file.read_text())
    assert len(matrix_data) == 1
    assert matrix_data[0]["chart_name"] == "common"
    assert matrix_data[0]["chart_version"] == "2.0.0"
