"""Helpers for artifact directory and run-id handling."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple

DEFAULT_ARTIFACTS_DIR = "artifacts"


def default_run_id() -> str:
    """Return the default UTC run identifier."""
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def resolve_output_root(output_dir: str, run_id: str = "") -> Tuple[Path, str]:
    """Resolve the root directory for a command that creates artifacts.

    When the caller uses the default artifacts directory, create a run-scoped
    subdirectory. For custom output directories, write directly into that
    directory and preserve the user-provided layout.
    """
    if output_dir == DEFAULT_ARTIFACTS_DIR:
        effective_run_id = run_id or default_run_id()
        root = Path(output_dir) / effective_run_id
        return root, effective_run_id
    return Path(output_dir), run_id


def resolve_domain_output(
    output_dir: str,
    domain: str,
    filename: str,
    run_id: str = "",
) -> Tuple[Path, Path, Path, str]:
    """Resolve canonical run-root, domain-root, file path, and effective run-id."""
    root, effective_run_id = resolve_output_root(output_dir=output_dir, run_id=run_id)
    domain_root = root / domain
    output_path = domain_root / filename
    return root, domain_root, output_path, effective_run_id


def resolve_run_input_path(
    run_root: Path,
    domain: str,
    filename: str,
    legacy_paths: Iterable[Path] = (),
) -> Path:
    """Return the first existing canonical or legacy path, else the canonical path."""
    canonical = run_root / domain / filename
    candidates = [canonical, *legacy_paths]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return canonical


def resolve_plot_dir(filepath: str) -> Path:
    """Derive a domain-specific plots directory from an artifact input path."""
    artifact_path = Path(filepath).expanduser().resolve()
    parent = artifact_path.parent
    name = artifact_path.name

    if name == "performance.csv":
        run_root = parent.parent if parent.name == "performance" else parent
        return run_root / "plots" / "performance"
    if name == "evictions.yaml":
        run_root = parent.parent if parent.name == "evictions" else parent
        return run_root / "plots" / "evictions"
    if name == "timeseries.csv":
        run_root = parent.parent if parent.name == "observe" else parent
        return run_root / "plots" / "observe"
    return parent / "plots"
