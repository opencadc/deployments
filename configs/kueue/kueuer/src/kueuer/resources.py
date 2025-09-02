# resources.py
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "kubernetes>=29.0.0",
#   "pydantic>=2.7.0",
#   "typer>=0.12.3",
# ]
# ///
"""
Totals cluster resources across Kubernetes nodes filtered by name regex.

- Deduplicates nodes by UID (so overlapping regex lists don't double count).
- By default totals from node .status.capacity; use --field allocatable to sum .status.allocatable instead.
- Returns a mapping: dict[str, dict[str, str]] with { "value": <string>, "unit": <string> }.
- If a resource does not exist on any matched node, it is **omitted**.

Examples:
  uv run resources.py
  uv run resources.py 'gpu-.*' 'node-1[0-9]'
  uv run resources.py --field allocatable --pretty 'worker-.*'
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Annotated, Dict, Iterable, List, Optional, Sequence

import typer
from kubernetes import client, config
from kubernetes.client import CoreV1Api, V1Node
from kubernetes.utils.quantity import parse_quantity
from pydantic import BaseModel, Field, RootModel, ValidationError, field_validator
from rich.console import Console
from typing_extensions import Literal

# High precision for CPU arithmetic (Decimal) and for stringifying without loss
getcontext().prec = 50

app = typer.Typer(help="Cluster utilities")

# =========================
# Pydantic Data Models
# =========================


class ResourceItem(BaseModel):
    value: str = Field(
        ..., description="Numeric value as a string, max precision retained."
    )
    unit: str = Field(
        ..., description="Unit for the value, e.g., 'cores', 'bytes', 'count'."
    )


class ResourceMap(RootModel[Dict[str, ResourceItem]]):
    """Dynamic resource map so unavailable resources can be omitted."""


class Settings(BaseModel):
    patterns: Optional[List[str]] = Field(
        default=None, description="Regex patterns for node names."
    )
    field: Literal["capacity", "allocatable"] = "capacity"
    pretty: bool = False

    @field_validator("patterns")
    @classmethod
    def validate_patterns(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None
        cleaned = [p for p in (s.strip() for s in v) if p]
        return cleaned or None


# =========================
# Internal Calculation Types
# =========================


@dataclass(frozen=True)
class TotalsAcc:
    cpu_cores: Optional[Decimal]  # None -> omit key
    memory_bytes: Optional[int]
    ephemeral_bytes: Optional[int]
    nvidia_gpu: Optional[int]
    amd_gpu: Optional[int]


# =========================
# Kubernetes Helpers
# =========================


def _load_kube() -> CoreV1Api:
    """
    Try standard kubeconfig first, then fall back to in-cluster config.
    """
    try:
        config.load_kube_config()
    except Exception:
        config.load_incluster_config()
    return client.CoreV1Api()


def _compile_patterns(patterns: Optional[Sequence[str]]) -> Optional[List[re.Pattern]]:
    if not patterns:
        return None
    return [re.compile(p) for p in patterns]


def _node_matches(name: str, compiled: Optional[List[re.Pattern]]) -> bool:
    if compiled is None:
        return True
    return any(p.search(name) for p in compiled)


def _collect_nodes(v1: CoreV1Api, patterns: Optional[Sequence[str]]) -> List[V1Node]:
    compiled = _compile_patterns(patterns)
    all_nodes = v1.list_node().items
    # Deduplicate by UID so overlapping regex patterns don't double count
    dedup: Dict[str, V1Node] = {}
    for n in all_nodes:
        name = n.metadata.name or ""
        if _node_matches(name, compiled):
            uid = n.metadata.uid or name  # Fallback to name if UID missing
            dedup[uid] = n
    return list(dedup.values())


def _get_field_map(node: V1Node, field: str) -> Dict[str, str]:
    """
    Extract either .status.capacity or .status.allocatable as a plain dict[str, str].
    """
    status = node.status
    if status is None:
        return {}
    obj = getattr(status, field, None)
    if obj is None:
        return {}
    return dict(obj)  # kubernetes client exposes as dict-like


# =========================
# Quantity Math
# =========================


def _sum_quantity(values: Iterable[str]) -> Decimal:
    """
    Sum Kubernetes resource quantity strings with maximum precision.
    - For cpu: returns Decimal cores (supports 'm')
    - For memory/ephemeral: returns Decimal bytes
    """
    total = Decimal("0")
    any_val = False
    for v in values:
        if v is None:
            continue
        any_val = True
        q = parse_quantity(v)
        total += Decimal(str(q))
    if not any_val:
        # signal "absent" by raising; caller decides to omit
        raise ValueError("no values")
    return total


def _sum_int_quantity(values: Iterable[str]) -> int:
    """
    Sum GPU counts or other integer-like quantities.
    """
    total = 0
    any_val = False
    for v in values:
        if v is None:
            continue
        any_val = True
        q = parse_quantity(v)
        total += int(q)
    if not any_val:
        raise ValueError("no values")
    return total


def _sum_resources(nodes: List[V1Node], field: str) -> TotalsAcc:
    cpu_vals: List[str] = []
    mem_vals: List[str] = []
    eph_vals: List[str] = []
    nvidia_vals: List[str] = []
    amd_vals: List[str] = []

    for n in nodes:
        m = _get_field_map(n, field)
        if not m:
            continue
        if "cpu" in m:
            cpu_vals.append(m["cpu"])
        if "memory" in m:
            mem_vals.append(m["memory"])
        if "ephemeral-storage" in m:
            eph_vals.append(m["ephemeral-storage"])
        if "nvidia.com/gpu" in m:
            nvidia_vals.append(m["nvidia.com/gpu"])
        if "amd.com/gpu" in m:
            amd_vals.append(m["amd.com/gpu"])

    # Convert lists → optional totals (None means "omit key")
    def _try_sum(dec_sum_fn, vals):
        try:
            return dec_sum_fn(vals)
        except Exception:
            return None

    cpu_total = _try_sum(_sum_quantity, cpu_vals)
    mem_total = _try_sum(_sum_quantity, mem_vals)
    eph_total = _try_sum(_sum_quantity, eph_vals)
    nvidia_total = _try_sum(_sum_int_quantity, nvidia_vals)
    amd_total = _try_sum(_sum_int_quantity, amd_vals)

    return TotalsAcc(
        cpu_cores=cpu_total,
        memory_bytes=int(mem_total) if mem_total is not None else None,
        ephemeral_bytes=int(eph_total) if eph_total is not None else None,
        nvidia_gpu=nvidia_total,
        amd_gpu=amd_total,
    )


# =========================
# Public API
# =========================


def total(
    patterns: Optional[List[str]] = None, field: str = "capacity"
) -> Dict[str, Dict[str, str]]:
    """
    Calculate total cluster resources across nodes matching any of the given regex patterns.

    Args:
        patterns: List of regex strings to match node names. If None or empty, includes all nodes.
        field:    Which field to sum: "capacity" (default) or "allocatable".

    Returns:
        dict[str, dict[str, str]] mapping resource name -> {"value": <str>, "unit": <str>}
        Only includes resources that exist on at least one matched node.
    """
    # Validate inputs with Pydantic
    try:
        cfg = Settings(patterns=patterns, field=field)
    except ValidationError as e:
        raise ValueError(str(e)) from e

    v1 = _load_kube()
    nodes = _collect_nodes(v1, cfg.patterns)
    acc = _sum_resources(nodes, cfg.field)

    # Build a dynamic map (omit unavailable resources)
    result: Dict[str, ResourceItem] = {}

    if acc.cpu_cores is not None:
        result["cpu"] = ResourceItem(value=f"{acc.cpu_cores}", unit="cores")
    if acc.memory_bytes is not None:
        result["memory"] = ResourceItem(value=f"{acc.memory_bytes}", unit="bytes")
    if acc.ephemeral_bytes is not None:
        result["ephemeral-storage"] = ResourceItem(
            value=f"{acc.ephemeral_bytes}", unit="bytes"
        )
    if acc.nvidia_gpu is not None:
        result["nvidia.com/gpu"] = ResourceItem(value=f"{acc.nvidia_gpu}", unit="count")
    if acc.amd_gpu is not None:
        result["amd.com/gpu"] = ResourceItem(value=f"{acc.amd_gpu}", unit="count")

    # Validate and dump with Pydantic
    return ResourceMap(result).model_dump()


# =========================
# CLI (Typer)
# =========================


console = Console()


@app.command("resources")
def resources(
    patterns: Annotated[
        Optional[List[str]],
        typer.Option(
            "-p",
            "--pattern",
            metavar="PATTERN",
            help="Regex pattern for node names. Can be specified multiple times.",
        ),
    ] = None,
    field: Annotated[
        str,
        typer.Option(
            "-f",
            "--field",
            help='Resource field to sum on each node: "capacity" or "allocatable".',
        ),
    ] = "capacity",
    scale: Annotated[
        float,
        typer.Option(
            "-s",
            "--scale",
            help="Scale resources by this percentage.",
        ),
    ] = 1.0,
):
    """
    Sum resources across nodes matching any of the provided regex patterns.
    """
    assert field in ["capacity", "allocatable"]
    assert scale > 0.0 and scale <= 1.0, "Percentage must be in (0, 1]"
    try:
        result = total(patterns or None, field=field)
        console.print(result, width=120)
        if scale != 1.0:
            console.print(f"Scaling by {scale * 100}%...")
            for k, v in result.items():
                # Limit to Decimal precision to 3 decimal places
                v["value"] = str(Decimal(v["value"]) * Decimal(scale))
            console.print(result, width=120)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    app()
