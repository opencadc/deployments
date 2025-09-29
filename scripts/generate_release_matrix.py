#!/usr/bin/env python3
"""Generate a GitHub Actions build matrix for release images.

The script reads ``release-images.json`` to determine all Docker build
configurations that need to run when a release is tagged. It outputs an
``include`` matrix compatible with ``fromJson`` inside GitHub Actions.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

RELEASE_TAG = os.environ.get("RELEASE_TAG")
if not RELEASE_TAG:
    raise SystemExit("RELEASE_TAG environment variable is required")

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "release-images.json"

if not CONFIG_PATH.exists():
    raise SystemExit("release-images.json not found at repository root")

with CONFIG_PATH.open("r", encoding="utf-8") as handle:
    payload = json.load(handle)

images: Iterable[Dict[str, Any]] = payload.get("images", [])
if not images:
    raise SystemExit("release-images.json must define an 'images' array")


def join_build_args(build_args: Any) -> str:
    """Convert build args into the newline-delimited format the action expects."""
    if not build_args:
        return ""
    if isinstance(build_args, dict):
        return "\n".join(f"{key}={value}" for key, value in build_args.items())
    if isinstance(build_args, (list, tuple)):
        return "\n".join(str(item) for item in build_args)
    return str(build_args)


def join_platforms(platforms: Any) -> str:
    if not platforms:
        return "linux/amd64"
    if isinstance(platforms, (list, tuple)):
        return ",".join(str(item) for item in platforms)
    return str(platforms)


matrix: List[Dict[str, Any]] = []
for entry in images:
    image = entry.get("image")
    context = entry.get("context")
    dockerfile = entry.get("dockerfile", "Dockerfile")

    if not image or not context:
        raise SystemExit("Each image entry must include 'image' and 'context'")

    release_tags = entry.get("static_tags", [])
    if not isinstance(release_tags, list):
        raise SystemExit("'static_tags' must be a list if provided")

    tags = [f"{image}:{RELEASE_TAG}"]
    tags.extend(f"{image}:{tag}" for tag in release_tags)

    matrix.append(
        {
            "name": entry.get("id") or Path(context).name,
            "image": image,
            "context": str(REPO_ROOT / context),
            "dockerfile": str((REPO_ROOT / context) / dockerfile)
            if dockerfile == "Dockerfile"
            else str(REPO_ROOT / dockerfile),
            "build_args": join_build_args(entry.get("build_args")),
            "tags": tags,
            "platforms": join_platforms(entry.get("platforms")),
        }
    )

output_path = os.environ.get("GITHUB_OUTPUT")
if not output_path:
    raise SystemExit("GITHUB_OUTPUT environment variable is not set")

with open(output_path, "a", encoding="utf-8") as handle:
    handle.write(f"matrix={json.dumps({'include': matrix})}\n")
