#!/usr/bin/env python3
"""Generate chart inventory metadata and update README."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _discover_repo_root() -> Path:
    """Return the repository root by walking up from this module."""

    module_path = Path(__file__).resolve()
    for candidate in module_path.parents:
        if (candidate / "helm").exists():
            return candidate
    return Path.cwd().resolve()


REPO_ROOT = _discover_repo_root()
README_MARKER_START = "<!-- CHART-INVENTORY:START -->"
README_MARKER_END = "<!-- CHART-INVENTORY:END -->"


def _clean_value(value: str) -> str:
    """Strip quotes and surrounding whitespace from a raw YAML scalar."""

    value = value.strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]
    return value


def parse_chart_yaml(chart_file: Path) -> Dict[str, Any]:
    """Parse a Chart.yaml into a dictionary without external dependencies."""

    data: Dict[str, Any] = {}
    current_list: Optional[List[Dict[str, str]]] = None
    current_item: Optional[Dict[str, str]] = None

    lines = chart_file.read_text().splitlines()
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if indent == 0:
            if current_list is not None and current_item:
                current_list.append(current_item)
            current_list = None
            current_item = None

            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                current_list = []
                data[key] = current_list
            else:
                data[key] = _clean_value(value)
        else:
            if current_list is None:
                continue
            if stripped.startswith("- "):
                if current_item:
                    current_list.append(current_item)
                current_item = {}
                remainder = stripped[2:].strip()
                if remainder and ":" in remainder:
                    sub_key, sub_value = remainder.split(":", 1)
                    current_item[sub_key.strip()] = _clean_value(sub_value)
            else:
                if current_item is None:
                    current_item = {}
                if ":" in stripped:
                    sub_key, sub_value = stripped.split(":", 1)
                    current_item[sub_key.strip()] = _clean_value(sub_value)

    if current_list is not None and current_item:
        current_list.append(current_item)

    return data


def find_chart_dirs() -> List[Path]:
    """Return every chart directory below the known helm roots."""

    chart_roots = [REPO_ROOT / "helm" / "applications", REPO_ROOT / "helm" / "common"]
    chart_dirs: List[Path] = []
    for root in chart_roots:
        if not root.exists():
            continue
        for chart_dir in sorted(root.rglob("Chart.yaml")):
            chart_dirs.append(chart_dir.parent)
    return chart_dirs


def load_chart_metadata(chart_dir: Path) -> Dict[str, Any]:
    """Extract metadata the automation expects from a chart directory."""

    chart_file = chart_dir / "Chart.yaml"
    raw_data = parse_chart_yaml(chart_file)
    chart_name = str(raw_data.get("name", chart_dir.name))
    maintainers = raw_data.get("maintainers") or []
    owners = [m.get("name") for m in maintainers if isinstance(m, dict) and m.get("name")]
    if not owners:
        owners = ["unassigned"]

    dependencies = []
    for dep in raw_data.get("dependencies", []) or []:
        if not isinstance(dep, dict):
            continue
        name = dep.get("name") or "unknown"
        version = dep.get("version") or ""
        repo = dep.get("repository") or ""
        dependencies.append({"name": name, "version": version, "repository": repo})

    return {
        "path": chart_dir.relative_to(REPO_ROOT).as_posix(),
        "name": chart_name,
        "display_name": raw_data.get("title") or chart_name,
        "description": (raw_data.get("description") or "").strip(),
        "type": raw_data.get("type", "application"),
        "version": str(raw_data.get("version", "")),
        "appVersion": str(raw_data.get("appVersion", "")),
        "owners": owners,
        "dependencies": dependencies,
    }


def write_catalog(charts: List[Dict[str, Any]], output_file: Path) -> None:
    """Persist chart metadata to a JSON file for downstream tooling."""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    catalog = {
        "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "charts": charts,
    }
    output_file.write_text(json.dumps(catalog, indent=2) + "\n")


def render_markdown_table(charts: List[Dict[str, Any]]) -> str:
    """Build the Markdown table section for the project README."""

    header = ["Chart", "Version", "App Version", "Owners", "Dependencies"]
    table_lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for chart in charts:
        chart_link = f"[{chart['name']}]({chart['path']})"
        dependencies = ", ".join(
            filter(None, (f"{dep['name']} {dep['version']}".strip() for dep in chart["dependencies"]))
        ) or "—"
        owners = ", ".join(chart["owners"]) if chart["owners"] else "unassigned"
        table_lines.append(
            "| "
            + " | ".join(
                [
                    chart_link,
                    chart["version"] or "—",
                    chart["appVersion"] or "—",
                    owners,
                    dependencies,
                ]
            )
            + " |"
        )
    return "\n".join(table_lines)


def update_readme(readme_file: Path, table: str) -> None:
    """Replace or append the chart inventory section in the README."""

    content = readme_file.read_text()
    generated_block = (
        f"{README_MARKER_START}\n"
        "This section is automatically generated. Do not edit manually.\n\n"
        f"{table}\n"
        f"{README_MARKER_END}"
    )
    if README_MARKER_START not in content or README_MARKER_END not in content:
        appendix = "\n\n## Chart Inventory\n" + generated_block + "\n"
        content = content.rstrip() + appendix
    else:
        pre, rest = content.split(README_MARKER_START, 1)
        _, post = rest.split(README_MARKER_END, 1)
        content = pre.rstrip() + "\n\n" + generated_block + post
    readme_file.write_text(content.rstrip() + "\n")


def main() -> None:
    """CLI entry point for inventory generation."""

    parser = argparse.ArgumentParser(description="Generate chart inventory metadata and README table.")
    parser.add_argument(
        "--catalog",
        type=Path,
        help="Optional path to write chart metadata JSON for downstream tooling.",
    )
    args = parser.parse_args()

    charts = [load_chart_metadata(chart_dir) for chart_dir in find_chart_dirs()]
    if not charts:
        sys.stderr.write("No charts found.\n")
        sys.exit(1)

    charts.sort(key=lambda c: c["path"])

    if args.catalog:
        write_catalog(charts, Path(args.catalog))
    table = render_markdown_table(charts)
    update_readme(REPO_ROOT / "README.md", table)


if __name__ == "__main__":
    main()
