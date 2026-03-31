"""Models and helpers for lifecycle run manifests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_init_manifest(path: Path, run_id: str) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "run_id": run_id,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "steps": [],
    }


def append_step(
    manifest: Dict[str, Any],
    name: str,
    status: str,
    details: Dict[str, Any] | None = None,
) -> None:
    manifest.setdefault("steps", []).append(
        {
            "name": name,
            "status": status,
            "timestamp": utc_now_iso(),
            "details": details or {},
        }
    )
    manifest["updated_at"] = utc_now_iso()


def save_manifest(path: Path, manifest: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
