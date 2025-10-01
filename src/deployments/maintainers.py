#!/usr/bin/env python3
"""Populate Helm chart maintainers based on recent git history."""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


def _discover_repo_root() -> Path:
    """Return the repository root by walking up from this module."""

    module_path = Path(__file__).resolve()
    for candidate in module_path.parents:
        if (candidate / "helm").exists():
            return candidate
    return Path.cwd().resolve()


REPO_ROOT = _discover_repo_root()
CHART_ROOTS: Sequence[Path] = (
    REPO_ROOT / "helm" / "applications",
    REPO_ROOT / "helm" / "common",
)
LOG_FORMAT = "%H%x1f%an%x1f%ae%x1f%ad"
MAX_MAINTAINERS = 2
MONTHS_WINDOW = 12


@dataclass
class Maintainer:
    """Single maintainer entry for Chart.yaml."""

    name: str
    email: str

    def as_yaml(self) -> List[str]:
        """Render maintainer dictionary in YAML list form."""
        lines = [f"  - name: {self.name}"]
        if self.email:
            lines.append(f"    email: {self.email}")
        return lines


@dataclass
class Commit:
    """Git commit metadata used for maintainer inference."""

    author: str
    email: str
    date: dt.datetime


def read_chart_paths() -> List[Path]:
    """Return all chart directories that contain a Chart.yaml file."""
    charts: List[Path] = []
    for root in CHART_ROOTS:
        if not root.exists():
            continue
        for chart_file in sorted(root.rglob("Chart.yaml")):
            charts.append(chart_file.parent)
    return charts


def git_log_for_path(path: Path) -> List[Commit]:
    """Read commit history for a chart path."""
    command = [
        "git",
        "log",
        f"--pretty=format:{LOG_FORMAT}",
        "--date=iso-strict",
        "--",
        str(path.relative_to(REPO_ROOT)),
    ]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git log failed for {path}: {result.stderr.strip()}")

    commits: List[Commit] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        _, author, email, raw_date = line.split("\x1f")
        try:
            commit_date = dt.datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        except ValueError:
            continue
        commits.append(Commit(author=author.strip(), email=email.strip(), date=commit_date))
    return commits


def select_recent_commits(commits: Sequence[Commit], months: int) -> List[Commit]:
    """Filter commits to the trailing N months relative to the latest commit."""
    if not commits:
        return []
    latest = max(commit.date for commit in commits)
    cutoff = latest - dt.timedelta(days=months * 30)
    return [commit for commit in commits if commit.date >= cutoff]


def choose_maintainers(commits: Sequence[Commit]) -> List[Maintainer]:
    """Return top authors limited to MAX_MAINTAINERS."""
    windowed = select_recent_commits(commits, MONTHS_WINDOW)
    if not windowed:
        return []

    counts: Counter[str] = Counter()
    email_lookup: Dict[str, str] = {}
    for commit in windowed:
        key = commit.author
        counts[key] += 1
        email_lookup.setdefault(key, commit.email)

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))
    maintainers: List[Maintainer] = []
    for author, _ in ranked[:MAX_MAINTAINERS]:
        maintainers.append(Maintainer(name=author, email=email_lookup.get(author, "")))
    return maintainers


def replace_maintainers_block(chart_file: Path, maintainers: Sequence[Maintainer]) -> bool:
    """Rewrite the maintainers block in Chart.yaml."""
    if not maintainers:
        return False

    lines = chart_file.read_text().splitlines()
    new_block: List[str] = ["maintainers:"]
    for maintainer in maintainers:
        new_block.extend(maintainer.as_yaml())

    start = None
    for idx, line in enumerate(lines):
        if line.startswith("maintainers:") and line[: len("maintainers:")].strip() == "maintainers:":
            start = idx
            break
    if start is not None:
        end = start + 1
        while end < len(lines):
            candidate = lines[end]
            if candidate and not candidate.startswith((" ", "\t")):
                break
            end += 1
        lines[start:end] = new_block
    else:
        insert_at = determine_insert_index(lines)
        addition: List[str] = []
        if insert_at > 0 and lines[insert_at - 1].strip():
            addition.append("")
        addition.extend(new_block)
        lines[insert_at:insert_at] = addition

    chart_file.write_text("\n".join(lines).rstrip() + "\n")
    return True


def determine_insert_index(lines: Sequence[str]) -> int:
    """Choose an insertion point close to the chart metadata header."""
    preferred_keys = ("description:", "name:", "apiVersion:")
    for key in preferred_keys:
        for idx, line in enumerate(lines):
            if line.startswith(key):
                return idx + 1
    return len(lines)


def update_chart(chart_dir: Path, dry_run: bool) -> bool:
    """Update maintainers for a single chart directory."""
    chart_file = chart_dir / "Chart.yaml"
    commits = git_log_for_path(chart_dir)
    maintainers = choose_maintainers(commits)
    if not maintainers:
        print(f"No recent maintainers found for {chart_dir.relative_to(REPO_ROOT)}")
        return False
    if dry_run:
        names = ", ".join(m.name for m in maintainers)
        print(f"Would update {chart_dir.relative_to(REPO_ROOT)} maintainers: {names}")
        return False
    if replace_maintainers_block(chart_file, maintainers):
        names = ", ".join(m.name for m in maintainers)
        print(f"Updated {chart_dir.relative_to(REPO_ROOT)} maintainers: {names}")
        return True
    return False


def run(dry_run: bool) -> int:
    """Process all charts and update maintainers where applicable."""
    for chart_dir in read_chart_paths():
        update_chart(chart_dir, dry_run)
    return 0


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Only report planned changes")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    """Entry point for CLI execution."""
    args = parse_args(argv)
    return run(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
