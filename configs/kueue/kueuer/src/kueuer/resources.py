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
- By default totals from node .status.capacity; use --field allocatable to sum
  .status.allocatable instead.
- Returns a mapping: ``cpu`` uses ``{ "value", "unit": "cores" }``; ``memory`` and
  ``ephemeral-storage`` use values in **Gi** (1024³ bytes) with ``unit: "Gi"``.
- For ``nvidia.com/gpu`` and ``amd.com/gpu``: ``{ "kind", "value", "unit": "count" }``
  where ``kind`` comes from node labels (e.g. ``nvidia.com/gpu.product``).
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
from typing import Annotated, Any, Dict, Iterable, List, Optional, Sequence, Union, cast

import typer
from kubernetes.client import CoreV1Api, V1Node
from kubernetes.utils.quantity import parse_quantity
from pydantic import BaseModel, Field, RootModel, ValidationError, field_validator
from rich.console import Console
from typing_extensions import Literal

from kueuer.utils.constants import DECIMAL_PRECISION
from kueuer.utils.k8s_config import get_k8s_config

# High precision for CPU arithmetic (Decimal) and for stringifying without loss
# Rationale: See DECIMAL_PRECISION in utils/constants.py
getcontext().prec = DECIMAL_PRECISION

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


class GpuResourceItem(BaseModel):
    """Cluster totals for a GPU resource."""

    kind: str = Field(
        ...,
        description=(
            "Product name if the cluster uses a single model; empty if unknown; "
            "'mixed' if multiple models."
        ),
    )
    value: str = Field(..., description="Total GPU count.")
    unit: Literal["count"] = "count"


class ResourceMap(RootModel[Dict[str, Union[ResourceItem, GpuResourceItem]]]):
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
    nvidia_by_kind: Optional[Dict[str, int]]
    amd_by_kind: Optional[Dict[str, int]]


# =========================
# Kubernetes Helpers
# =========================


def _load_kube() -> CoreV1Api:
    """
    Get the Core V1 API client using centralized configuration.
    """
    k8s = get_k8s_config()
    return k8s.core_v1


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


def _nvidia_gpu_kind_from_labels(labels: Dict[str, str]) -> str:
    """Resolve GPU product name from common NVIDIA node labels."""
    for key in (
        "nvidia.com/gpu.product",
        "nvidia.com/gfd.gpu.product",
    ):
        v = labels.get(key)
        if v:
            return str(v).strip()
    return ""


def _amd_gpu_kind_from_labels(labels: Dict[str, str]) -> str:
    """Resolve GPU product name from common AMD node labels."""
    for key in (
        "amd.com/gpu.product",
        "amd.com/gpu.family",
    ):
        v = labels.get(key)
        if v:
            return str(v).strip()
    return ""


def _summary_gpu_kind(by_kind: Dict[str, int]) -> str:
    """Single model name, empty if unknown, or 'mixed' if multiple distinct models."""
    active = {k: v for k, v in by_kind.items() if v > 0}
    if not active:
        return ""
    distinct_nonempty = {k for k in active if k}
    if not distinct_nonempty:
        return ""
    if len(distinct_nonempty) == 1:
        return next(iter(distinct_nonempty))
    return "mixed"


def _bytes_to_gi_str(total_bytes: int) -> str:
    """Convert a byte total to a decimal string in Gi (1 Gi = 1024³ bytes)."""
    # Use integer 1024**3 so the divisor is exact (Decimal(1024)**3 can round).
    gi = Decimal(total_bytes) / Decimal(1024**3)
    s = format(gi, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


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
    nvidia_by_kind: Dict[str, int] = {}
    amd_by_kind: Dict[str, int] = {}

    for n in nodes:
        m = _get_field_map(n, field)
        if not m:
            continue
        labels = (n.metadata.labels or {}) if n.metadata else {}
        if "cpu" in m:
            cpu_vals.append(m["cpu"])
        if "memory" in m:
            mem_vals.append(m["memory"])
        if "ephemeral-storage" in m:
            eph_vals.append(m["ephemeral-storage"])
        if "nvidia.com/gpu" in m:
            nvidia_vals.append(m["nvidia.com/gpu"])
            nk = _nvidia_gpu_kind_from_labels(labels)
            nvidia_by_kind[nk] = nvidia_by_kind.get(nk, 0) + int(
                parse_quantity(m["nvidia.com/gpu"])
            )
        if "amd.com/gpu" in m:
            amd_vals.append(m["amd.com/gpu"])
            ak = _amd_gpu_kind_from_labels(labels)
            amd_by_kind[ak] = amd_by_kind.get(ak, 0) + int(
                parse_quantity(m["amd.com/gpu"])
            )

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
        nvidia_by_kind=nvidia_by_kind if nvidia_total is not None else None,
        amd_by_kind=amd_by_kind if amd_total is not None else None,
    )


# =========================
# Public API
# =========================


def total(
    patterns: Optional[List[str]] = None, field: str = "capacity"
) -> Dict[str, Any]:
    """
    Calculate total cluster resources across nodes matching regex patterns.

    Args:
        patterns: Regex strings for node names. If None or empty, includes all nodes.
        field: Which field to sum: "capacity" (default) or "allocatable".

    Returns:
        Mapping of resource name to detail dicts. Memory and ephemeral-storage use
        Gi and ``unit`` ``\"Gi\"``. GPU entries include ``kind``, ``value``, and
        ``unit`` ``\"count\"``. Only includes resources present on at least one node.
    """
    # Validate inputs with Pydantic
    if field not in ("capacity", "allocatable"):
        raise ValueError('field must be "capacity" or "allocatable"')
    try:
        cfg = Settings(
            patterns=patterns,
            field=cast(Literal["capacity", "allocatable"], field),
        )
    except ValidationError as e:
        raise ValueError(str(e)) from e

    v1 = _load_kube()
    nodes = _collect_nodes(v1, cfg.patterns)
    acc = _sum_resources(nodes, cfg.field)

    # Build a dynamic map (omit unavailable resources)
    result: Dict[str, Union[ResourceItem, GpuResourceItem]] = {}

    if acc.cpu_cores is not None:
        result["cpu"] = ResourceItem(value=f"{acc.cpu_cores}", unit="cores")
    if acc.memory_bytes is not None:
        result["memory"] = ResourceItem(
            value=_bytes_to_gi_str(acc.memory_bytes),
            unit="Gi",
        )
    if acc.ephemeral_bytes is not None:
        result["ephemeral-storage"] = ResourceItem(
            value=_bytes_to_gi_str(acc.ephemeral_bytes),
            unit="Gi",
        )
    if acc.nvidia_gpu is not None and acc.nvidia_by_kind is not None:
        result["nvidia.com/gpu"] = GpuResourceItem(
            kind=_summary_gpu_kind(acc.nvidia_by_kind),
            value=str(acc.nvidia_gpu),
        )
    if acc.amd_gpu is not None and acc.amd_by_kind is not None:
        result["amd.com/gpu"] = GpuResourceItem(
            kind=_summary_gpu_kind(acc.amd_by_kind),
            value=str(acc.amd_gpu),
        )

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
            for _k, v in result.items():
                v["value"] = str(Decimal(v["value"]) * Decimal(scale))
            console.print(result, width=120)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    app()
