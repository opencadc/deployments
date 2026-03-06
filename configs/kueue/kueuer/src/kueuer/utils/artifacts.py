"""Helpers for artifact directory and run-id handling."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple


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
