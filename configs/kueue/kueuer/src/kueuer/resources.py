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
- Results are grouped by a configurable node label (see CLI ``--node-label-key``;
  ``total()`` requires ``node_label_key`` with no default in code). Nodes without
  the label are grouped under ``""``. Each group has ``count`` (nodes in group),
  ``cpu``, ``memory``, ``ephemeral-storage`` (binary **GiB**, 1024³; values up to
  3 decimal places), per-bucket **weights** (same 3 decimal places; pool CPU
  cores per GiB / per GPU kind—see ``ResourceWeights``), and GPU lists.
- ``nvidia.com/gpu`` is a list of ``{ "kind", "value", "unit": "count" }`` per
  distinct ``nvidia.com/gpu.product`` label, summed across nodes. When
  capacity/allocatable reports 0 or omits ``nvidia.com/gpu`` but the NVIDIA
  Device Plugin exposes counts on labels (e.g. ``nvidia.com/gpu.count``), those
  label values are used with ``kind`` from ``nvidia.com/gpu.product``.
- ``amd.com/gpu`` uses the same list shape, summed by ``amd.com/gpu.product``.
- If a resource does not exist for nodes in a group, it is **omitted** for that
  group.

Examples:
  uv run resources.py
  uv run resources.py 'gpu-.*' 'node-1[0-9]'
  uv run resources.py --field allocatable --pretty 'worker-.*'
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, getcontext, localcontext
from typing import Annotated, Any, Dict, Iterable, List, Optional, Sequence, cast

import typer
from kubernetes.client import CoreV1Api, V1Node
from kubernetes.utils.quantity import parse_quantity
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from rich.console import Console
from typing_extensions import Literal

from kueuer.utils.constants import DECIMAL_PRECISION
from kueuer.utils.k8s_config import get_k8s_config

# High precision for CPU arithmetic (Decimal) and for stringifying without loss
# Rationale: See DECIMAL_PRECISION in utils/constants.py
getcontext().prec = DECIMAL_PRECISION

# Reported fractional precision for CPU, GiB display quantities, and weight ratios.
REPORT_MAX_DECIMAL_PLACES = 3

# Intermediate precision for weight ratio division before rounding to ``REPORT_MAX_DECIMAL_PLACES``.
_WEIGHT_RATIO_DIV_PREC = max(80, DECIMAL_PRECISION)

app = typer.Typer(help="Cluster utilities")

# =========================
# Pydantic Data Models
# =========================


class ResourceItem(BaseModel):
    value: str = Field(
        ...,
        description="Numeric string with at most three fractional decimal places.",
    )
    unit: str = Field(
        ...,
        description="Binary GiB for memory/ephemeral totals, 'cores', or 'count'.",
    )


class GpuResourceItem(BaseModel):
    """Per-model GPU totals within a node-type group."""

    kind: str = Field(
        ...,
        description="Product name from node labels (e.g. nvidia.com/gpu.product).",
    )
    value: str = Field(..., description="Total GPU count for this kind.")
    unit: Literal["count"] = "count"


class ResourceWeights(BaseModel):
    """Pool-level ratios vs CPU cores (dimensionless); see module docstring for interpretation."""

    model_config = ConfigDict(populate_by_name=True)

    cpu: str = Field(
        default="1",
        description="Baseline; other weights are pool CPU per unit of that resource.",
    )
    memory: Optional[str] = Field(
        None,
        description="Pool CPU cores divided by total memory in binary GiB.",
    )
    ephemeral_storage: Optional[str] = Field(
        None,
        serialization_alias="ephemeral-storage",
        description="Pool CPU cores divided by total ephemeral storage in binary GiB.",
    )
    nvidia_gpu: Optional[Dict[str, str]] = Field(
        None,
        serialization_alias="nvidia.com/gpu",
        description="Per GPU product: pool CPU cores divided by count of that kind.",
    )


class NodeTypeResources(BaseModel):
    """Resource totals for one value of the grouping node label."""

    model_config = ConfigDict(populate_by_name=True)

    count: int = Field(
        ...,
        ge=0,
        description="Number of nodes in this group (unique nodes after pattern filter).",
    )
    cpu: Optional[ResourceItem] = None
    memory: Optional[ResourceItem] = None
    ephemeral_storage: Optional[ResourceItem] = Field(
        default=None,
        serialization_alias="ephemeral-storage",
    )
    nvidia_gpu: Optional[List[GpuResourceItem]] = Field(
        default=None,
        serialization_alias="nvidia.com/gpu",
    )
    amd_gpu: Optional[List[GpuResourceItem]] = Field(
        default=None,
        serialization_alias="amd.com/gpu",
    )
    weights: Optional[ResourceWeights] = Field(
        None,
        description=(
            "CPU-normalized pool composition weights (decimal strings, same precision "
            "as other reported quantities). "
            "Omitted if the pool has no CPU total to divide by."
        ),
    )


class ClusterResourcesResult(BaseModel):
    """Cluster resources grouped by ``node_label_key`` label values."""

    node_label_key: str = Field(
        ...,
        description="Kubernetes node label key used to form each group.",
    )
    by_label_value: Dict[str, NodeTypeResources]


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


def _node_nvidia_gpu_contrib(
    labels: Dict[str, str], m: Dict[str, str]
) -> Optional[tuple[int, str]]:
    """
    NVIDIA GPUs advertised for this node: count and product kind.

    Prefer ``.status.capacity``/``allocatable`` when ``nvidia.com/gpu`` is
    positive. If it is zero or absent, fall back to ``nvidia.com/gpu.count`` so
    MIG / device-plugin-only reporting still aggregates correctly.
    """
    kind = _nvidia_gpu_kind_from_labels(labels)
    cap_s = m.get("nvidia.com/gpu")
    cap_n = int(parse_quantity(cap_s)) if cap_s else 0
    lc_raw = labels.get("nvidia.com/gpu.count")
    label_n: Optional[int] = None
    if lc_raw is not None and str(lc_raw).strip() != "":
        label_n = int(parse_quantity(str(lc_raw).strip()))

    if cap_n > 0:
        return (cap_n, kind)
    if label_n is not None and label_n > 0:
        return (label_n, kind)
    return None


def _gpu_kind_totals_to_list(by_kind: Optional[Dict[str, int]]) -> Optional[List[GpuResourceItem]]:
    """Convert per-kind counts to a stable list for JSON output."""
    if not by_kind:
        return None
    items = [
        GpuResourceItem(kind=k, value=str(v))
        for k, v in sorted(by_kind.items(), key=lambda kv: (kv[0] == "", kv[0]))
        if v > 0
    ]
    return items or None


def _format_decimal_report(value: Decimal) -> str:
    """Stringify a non-negative Decimal with at most ``REPORT_MAX_DECIMAL_PLACES`` places."""
    if value < 0:
        raise ValueError("value must be non-negative")
    q = Decimal("1").scaleb(-REPORT_MAX_DECIMAL_PLACES)
    rounded = value.quantize(q, rounding=ROUND_HALF_UP)
    s = format(rounded, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


# Binary gibibyte (Kubernetes-style): 1 GiB = 1024³ bytes.
_GIB_BYTES = Decimal(1024**3)


def _bytes_to_binary_gib_decimal(total_bytes: int) -> Decimal:
    """Convert byte totals to binary GiB (full ``Decimal``, unrounded)."""
    if total_bytes < 0:
        raise ValueError("byte total must be non-negative")
    return Decimal(total_bytes) / _GIB_BYTES


def _gib_resource_item(total_bytes: int) -> ResourceItem:
    """Memory / ephemeral totals: always reported in GiB with limited display precision."""
    if total_bytes == 0:
        return ResourceItem(value="0", unit="GiB")
    v = _bytes_to_binary_gib_decimal(total_bytes)
    return ResourceItem(value=_format_decimal_report(v), unit="GiB")


def _gib_display_to_bytes(value: Decimal) -> Decimal:
    """Interpret a displayed GiB quantity as bytes."""
    return value * _GIB_BYTES


def _decimal_ratio_string(numerator: Decimal, denominator: Decimal) -> str:
    """``numerator / denominator`` rounded to ``REPORT_MAX_DECIMAL_PLACES`` (half-up)."""
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    with localcontext() as ctx:
        ctx.prec = _WEIGHT_RATIO_DIV_PREC
        ratio = numerator / denominator
    return _format_decimal_report(ratio)


def _compute_resource_weights(acc: TotalsAcc) -> Optional[ResourceWeights]:
    """
    Weights normalize pool totals to a per-CPU baseline: ``cpu`` is 1; other
    fields are ``TOTAL_CPU / TOTAL_QUANTITY`` in compatible units (GiB for
    memory and ephemeral; per-GPU-kind counts for NVIDIA).

    **Interpretation (heuristic):** For a node pool with totals ``(C, M, E, …)``,
    weights map ``(c, m, e, …)`` requests to a linear ``c·1 + m·w_mem + …`` style
    score *if* you treat the pool's aggregate ratio as a fixed substitution rate
    between CPU and other resources. That is a **comparative** normalization, not a
    guarantee of schedulability, pricing, or optimal packing—heterogeneous nodes,
    fragmentation, and priorities are not captured.
    """
    cpu = acc.cpu_cores
    if cpu is None or cpu <= 0:
        return None

    mem_w: Optional[str] = None
    if acc.memory_bytes is not None and acc.memory_bytes > 0:
        mem_w = _decimal_ratio_string(cpu, _bytes_to_binary_gib_decimal(acc.memory_bytes))

    eph_w: Optional[str] = None
    if acc.ephemeral_bytes is not None and acc.ephemeral_bytes > 0:
        eph_w = _decimal_ratio_string(cpu, _bytes_to_binary_gib_decimal(acc.ephemeral_bytes))

    nv_map: Optional[Dict[str, str]] = None
    if acc.nvidia_by_kind:
        entries: Dict[str, str] = {}
        for kind, cnt in sorted(
            acc.nvidia_by_kind.items(),
            key=lambda kv: (kv[0] == "", kv[0]),
        ):
            if cnt <= 0:
                continue
            entries[kind] = _decimal_ratio_string(cpu, Decimal(cnt))
        nv_map = entries or None

    return ResourceWeights(
        cpu="1",
        memory=mem_w,
        ephemeral_storage=eph_w,
        nvidia_gpu=nv_map,
    )


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
    amd_vals: List[str] = []
    nvidia_by_kind: Dict[str, int] = {}
    amd_by_kind: Dict[str, int] = {}

    for n in nodes:
        m = _get_field_map(n, field)
        labels = (n.metadata.labels or {}) if n.metadata else {}
        nvidia_c = _node_nvidia_gpu_contrib(labels, m)
        if nvidia_c is not None:
            cnt, nk = nvidia_c
            nvidia_by_kind[nk] = nvidia_by_kind.get(nk, 0) + cnt
        if not m:
            continue
        if "cpu" in m:
            cpu_vals.append(m["cpu"])
        if "memory" in m:
            mem_vals.append(m["memory"])
        if "ephemeral-storage" in m:
            eph_vals.append(m["ephemeral-storage"])
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
    amd_total = _try_sum(_sum_int_quantity, amd_vals)

    return TotalsAcc(
        cpu_cores=cpu_total,
        memory_bytes=int(mem_total) if mem_total is not None else None,
        ephemeral_bytes=int(eph_total) if eph_total is not None else None,
        nvidia_by_kind=nvidia_by_kind if nvidia_by_kind else None,
        amd_by_kind=amd_by_kind if amd_total is not None else None,
    )


def _totals_acc_to_node_type_resources(acc: TotalsAcc, node_count: int) -> NodeTypeResources:
    """Build one NodeTypeResources from aggregated totals."""
    return NodeTypeResources(
        count=node_count,
        cpu=(
            ResourceItem(
                value=_format_decimal_report(acc.cpu_cores),
                unit="cores",
            )
            if acc.cpu_cores is not None
            else None
        ),
        memory=(
            _gib_resource_item(acc.memory_bytes)
            if acc.memory_bytes is not None
            else None
        ),
        ephemeral_storage=(
            _gib_resource_item(acc.ephemeral_bytes)
            if acc.ephemeral_bytes is not None
            else None
        ),
        nvidia_gpu=_gpu_kind_totals_to_list(acc.nvidia_by_kind),
        amd_gpu=_gpu_kind_totals_to_list(acc.amd_by_kind),
        weights=_compute_resource_weights(acc),
    )


# =========================
# Public API
# =========================


def total(
    patterns: Optional[List[str]] = None,
    field: str = "capacity",
    *,
    node_label_key: str,
) -> Dict[str, Any]:
    """
    Calculate total cluster resources across nodes matching regex patterns.

    Args:
        patterns: Regex strings for node names. If None or empty, includes all nodes.
        field: Which field to sum: "capacity" (default) or "allocatable".
        node_label_key: Kubernetes node label key used to group results (callers
            such as the CLI supply the default; this function does not default it).

    Returns:
        A dict with ``node_label_key``, ``by_label_value`` (each key is a label
        value, or ``\"\"`` if unset), and per-group ``count`` plus resource maps.
    """
    label_key = node_label_key.strip()
    if not label_key:
        raise ValueError("node_label_key must be a non-empty string")

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
    by_nt: Dict[str, List[V1Node]] = {}
    for n in nodes:
        labels = (n.metadata.labels or {}) if n.metadata else {}
        raw_nt = labels.get(label_key)
        nt_key = "" if raw_nt is None else str(raw_nt)
        by_nt.setdefault(nt_key, []).append(n)

    groups: Dict[str, NodeTypeResources] = {}
    for nt_key in sorted(by_nt.keys(), key=lambda s: (s == "", s)):
        bucket = by_nt[nt_key]
        acc = _sum_resources(bucket, cfg.field)
        groups[nt_key] = _totals_acc_to_node_type_resources(acc, len(bucket))

    return ClusterResourcesResult(
        node_label_key=label_key,
        by_label_value=groups,
    ).model_dump(
        by_alias=True,
        exclude_none=True,
    )


def _scale_resource_item_inplace(item: Dict[str, Any], scale: Decimal) -> None:
    """Apply ``--scale`` to one resource dict with ``value`` and ``unit``."""
    unit = str(item.get("unit", ""))
    v = Decimal(str(item["value"]))
    if unit == "cores":
        item["value"] = _format_decimal_report(v * scale)
    elif unit == "GiB":
        scaled_bytes = _gib_display_to_bytes(v) * scale
        int_bytes = max(0, int(scaled_bytes.to_integral_value(rounding=ROUND_HALF_UP)))
        out = _gib_resource_item(int_bytes)
        item["value"] = out.value
        item["unit"] = out.unit
    elif unit == "count":
        item["value"] = _format_decimal_report(v * scale)
    else:
        item["value"] = _format_decimal_report(v * scale)


def _scale_cluster_resources_payload(result: Dict[str, Any], scale: Decimal) -> None:
    """Multiply numeric ``value`` fields in-place (CLI ``--scale``). Leaves ``weights`` unchanged."""
    inner = result.get("by_label_value")
    if not isinstance(inner, dict):
        return
    for block in inner.values():
        if not isinstance(block, dict):
            continue
        for res_key in ("cpu", "memory", "ephemeral-storage"):
            item = block.get(res_key)
            if isinstance(item, dict) and "value" in item and "unit" in item:
                _scale_resource_item_inplace(item, scale)
        for gpu_key in ("nvidia.com/gpu", "amd.com/gpu"):
            lst = block.get(gpu_key)
            if isinstance(lst, list):
                for g in lst:
                    if isinstance(g, dict) and "value" in g and "unit" in g:
                        _scale_resource_item_inplace(g, scale)


def list_resource_quotas(namespace: str) -> Dict[str, Any]:
    """List ResourceQuota objects in a namespace via the Kubernetes Python client."""
    k8s = get_k8s_config()
    quota_list = k8s.core_v1.list_namespaced_resource_quota(namespace=namespace)
    payload = k8s.api_client.sanitize_for_serialization(quota_list)
    if isinstance(payload, dict):
        return payload
    return {"items": payload or []}


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
    node_label_key: Annotated[
        str,
        typer.Option(
            "--node-label-key",
            help=(
                "Node label key used to group totals by label value "
                '(default only applies to this CLI, not to total()).'
            ),
        ),
    ] = "skaha.opencadc.org/node-type",
):
    """
    Sum resources across nodes matching any of the provided regex patterns.
    """
    assert field in ["capacity", "allocatable"]
    assert scale > 0.0 and scale <= 1.0, "Percentage must be in (0, 1]"
    try:
        result = total(
            patterns or None,
            field=field,
            node_label_key=node_label_key,
        )
        console.print(result, width=120)
        if scale != 1.0:
            console.print(f"Scaling by {scale * 100}%...")
            _scale_cluster_resources_payload(result, Decimal(str(scale)))
            console.print(result, width=120)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)


@app.command("resourcequota")
def resourcequota(
    namespace: Annotated[
        str,
        typer.Option(
            "-n",
            "--namespace",
            help="Namespace to query for ResourceQuota objects.",
        ),
    ],
):
    """List namespace ResourceQuota objects using the Kubernetes Python client."""
    try:
        response = list_resource_quotas(namespace)
        console.print({"response": response, "resource_quotas": response.get("items", [])})
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    app()
