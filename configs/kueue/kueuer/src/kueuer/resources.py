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
Totals cluster resources across Kubernetes nodes.

- Deduplicates nodes by UID when listing.
- By default totals from node .status.capacity; use --field allocatable to sum
  .status.allocatable instead.
- Results are grouped by a configurable node label (see CLI ``--node-label``;
  ``total()`` requires ``node_label`` with no default in code). Nodes without
  the label are grouped under ``""``. Each group has ``count`` (nodes in group),
  ``cpu``, ``memory``, ``ephemeral-storage`` (binary units per ``--units``;
  values up to 3 decimal places), per-bucket **weights** (IEEE-754 binary64,
  shortest round-trip decimal strings; normalized to ``--baseline`` (``-b``),
  computed in the same byte scale as ``--units``—see ``ResourceWeights``), and
  GPU lists.
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
  uv run resources.py --field allocatable
  uv run resources.py --units Mi --baseline cpu
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, getcontext, localcontext
from typing import Annotated, Any, Dict, Iterable, List, Optional, cast

import typer
from kubernetes.client import CoreV1Api, V1Node
from kubernetes.utils.quantity import parse_quantity
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from rich.console import Console
from typing_extensions import Literal

from kueuer.utils.constants import DECIMAL_PRECISION
from kueuer.utils.k8s_config import get_k8s_config

# High precision for CPU arithmetic (Decimal) and for stringifying without loss
# Rationale: See DECIMAL_PRECISION in utils/constants.py
getcontext().prec = DECIMAL_PRECISION

# Reported fractional precision for CPU, GiB display quantities, and weight ratios.
REPORT_MAX_DECIMAL_PLACES = 3

# Intermediate precision for weight ratio division before rounding to
# ``REPORT_MAX_DECIMAL_PLACES``.
_WEIGHT_RATIO_DIV_PREC = max(80, DECIMAL_PRECISION)

# Baseline weight ``1`` as a binary64 round-trip string (matches computed weights).
_WEIGHT_BASELINE_ONE_STR = repr(1.0)

# ``total()`` / ``--baseline`` accepted resource names.
_ALLOWED_BASELINES: frozenset[str] = frozenset(
    ("cpu", "memory", "ephemeral-storage", "nvidia.com/gpu")
)

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
        description=(
            "Binary unit (B, Ki, Mi, …) for memory/ephemeral, 'cores', or 'count'."
        ),
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
    """Pool composition weights vs ``--baseline``; see module docstring."""

    model_config = ConfigDict(populate_by_name=True)

    cpu: Optional[str] = Field(
        None,
        description="IEEE-754 binary64 string; baseline CPU weight is ``1.0``.",
    )
    memory: Optional[str] = Field(
        None,
        description="IEEE-754 binary64 string vs baseline in ``--units``.",
    )
    ephemeral_storage: Optional[str] = Field(
        None,
        serialization_alias="ephemeral-storage",
        description="IEEE-754 binary64 string vs baseline in ``--units``.",
    )
    nvidia_gpu: Optional[Dict[str, str]] = Field(
        None,
        serialization_alias="nvidia.com/gpu",
        description="Per GPU product: IEEE-754 binary64 weight vs baseline.",
    )


class NodeTypeResources(BaseModel):
    """Resource totals for one value of the grouping node label."""

    model_config = ConfigDict(populate_by_name=True)

    count: int = Field(
        ...,
        ge=0,
        description="Number of nodes in this group (unique nodes).",
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
            "Pool composition weights (IEEE-754 binary64, shortest round-trip "
            "strings). Omitted when the baseline resource total is missing or "
            "non-positive."
        ),
    )


class ClusterResourcesResult(BaseModel):
    """Cluster resources grouped by ``node_label`` label values."""

    node_label: str = Field(
        ...,
        description="Kubernetes node label key used to form each group.",
    )
    by_label_value: Dict[str, NodeTypeResources]


class Settings(BaseModel):
    field: Literal["capacity", "allocatable"] = "capacity"
    pretty: bool = False


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


def _collect_nodes(v1: CoreV1Api) -> List[V1Node]:
    all_nodes = v1.list_node().items
    dedup: Dict[str, V1Node] = {}
    for n in all_nodes:
        name = n.metadata.name or ""
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


def _gpu_kind_totals_to_list(
    by_kind: Optional[Dict[str, int]],
) -> Optional[List[GpuResourceItem]]:
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
    """Stringify a non-negative Decimal with at most ``REPORT_MAX_DECIMAL_PLACES``."""
    if value < 0:
        raise ValueError("value must be non-negative")
    q = Decimal("1").scaleb(-REPORT_MAX_DECIMAL_PLACES)
    rounded = value.quantize(q, rounding=ROUND_HALF_UP)
    s = format(rounded, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


# Binary IEC factors: unit string -> bytes per one unit (B, Ki, Mi, Gi, Ti, Pi).
_BINARY_UNIT_BYTES: Dict[str, int] = {
    "B": 1,
    "Ki": 1024,
    "Mi": 1024**2,
    "Gi": 1024**3,
    "Ti": 1024**4,
    "Pi": 1024**5,
}


def normalize_binary_unit(units: str) -> str:
    """Return canonical binary unit key or raise ``ValueError``."""
    u = units.strip()
    if u not in _BINARY_UNIT_BYTES:
        allowed = ", ".join(sorted(_BINARY_UNIT_BYTES))
        raise ValueError(f'units must be one of: {allowed} (got "{units}")')
    return u


def _bytes_to_qty_decimal(total_bytes: int, unit: str) -> Decimal:
    """Convert byte totals to the selected binary unit (full ``Decimal``, unrounded)."""
    if total_bytes < 0:
        raise ValueError("byte total must be non-negative")
    factor = Decimal(_BINARY_UNIT_BYTES[unit])
    return Decimal(total_bytes) / factor


def _bytes_to_resource_item(total_bytes: int, unit: str) -> ResourceItem:
    """Memory / ephemeral totals in ``unit`` with limited display precision."""
    if total_bytes == 0:
        return ResourceItem(value="0", unit=unit)
    v = _bytes_to_qty_decimal(total_bytes, unit)
    return ResourceItem(value=_format_decimal_report(v), unit=unit)


def _display_qty_to_bytes(value: Decimal, unit: str) -> Decimal:
    """Interpret a displayed quantity in ``unit`` as bytes."""
    return value * Decimal(_BINARY_UNIT_BYTES[unit])


def _decimal_ratio_string(numerator: Decimal, denominator: Decimal) -> str:
    """Weight ratio as IEEE-754 binary64 (``float``), shortest round-trip ``repr``."""
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    with localcontext() as ctx:
        ctx.prec = _WEIGHT_RATIO_DIV_PREC
        ratio = numerator / denominator
    return repr(float(ratio))


def _nvidia_weights_from_numerator(
    by_kind: Optional[Dict[str, int]],
    numer: Decimal,
) -> Optional[Dict[str, str]]:
    if not by_kind:
        return None
    entries: Dict[str, str] = {}
    for kind, cnt in sorted(by_kind.items(), key=lambda kv: (kv[0] == "", kv[0])):
        if cnt <= 0:
            continue
        entries[kind] = _decimal_ratio_string(numer, Decimal(cnt))
    return entries or None


def _nvidia_pool_total(by_kind: Optional[Dict[str, int]]) -> Optional[Decimal]:
    """Sum of NVIDIA GPU counts across kinds (pool-wide GPU total)."""
    if not by_kind:
        return None
    t = sum(c for c in by_kind.values() if c > 0)
    return Decimal(t) if t > 0 else None


def _weight_quantities(
    acc: TotalsAcc,
    units: str,
) -> tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal]]:
    mem_b = acc.memory_bytes
    eph_b = acc.ephemeral_bytes
    qty_mem = (
        _bytes_to_qty_decimal(mem_b, units) if mem_b is not None and mem_b > 0 else None
    )
    qty_eph = (
        _bytes_to_qty_decimal(eph_b, units) if eph_b is not None and eph_b > 0 else None
    )
    return (acc.cpu_cores, qty_mem, qty_eph)


def _weights_baseline_cpu(
    acc: TotalsAcc,
    qty_cpu: Decimal,
    qty_mem: Optional[Decimal],
    qty_eph: Optional[Decimal],
) -> Optional[ResourceWeights]:
    w_mem = _decimal_ratio_string(qty_cpu, qty_mem) if qty_mem is not None else None
    w_eph = _decimal_ratio_string(qty_cpu, qty_eph) if qty_eph is not None else None
    w_nv = _nvidia_weights_from_numerator(acc.nvidia_by_kind, qty_cpu)
    return ResourceWeights(
        cpu=_WEIGHT_BASELINE_ONE_STR,
        memory=w_mem,
        ephemeral_storage=w_eph,
        nvidia_gpu=w_nv,
    )


def _weights_baseline_memory(
    acc: TotalsAcc,
    qty_cpu: Optional[Decimal],
    qty_mem: Decimal,
    qty_eph: Optional[Decimal],
) -> Optional[ResourceWeights]:
    w_cpu = (
        _decimal_ratio_string(qty_mem, qty_cpu)
        if qty_cpu is not None and qty_cpu > 0
        else None
    )
    w_eph = _decimal_ratio_string(qty_mem, qty_eph) if qty_eph is not None else None
    w_nv = _nvidia_weights_from_numerator(acc.nvidia_by_kind, qty_mem)
    return ResourceWeights(
        cpu=w_cpu,
        memory=_WEIGHT_BASELINE_ONE_STR,
        ephemeral_storage=w_eph,
        nvidia_gpu=w_nv,
    )


def _weights_baseline_ephemeral(
    acc: TotalsAcc,
    qty_cpu: Optional[Decimal],
    qty_mem: Optional[Decimal],
    qty_eph: Decimal,
) -> Optional[ResourceWeights]:
    w_cpu = (
        _decimal_ratio_string(qty_eph, qty_cpu)
        if qty_cpu is not None and qty_cpu > 0
        else None
    )
    w_mem = _decimal_ratio_string(qty_eph, qty_mem) if qty_mem is not None else None
    w_nv = _nvidia_weights_from_numerator(acc.nvidia_by_kind, qty_eph)
    return ResourceWeights(
        cpu=w_cpu,
        memory=w_mem,
        ephemeral_storage=_WEIGHT_BASELINE_ONE_STR,
        nvidia_gpu=w_nv,
    )


def _weights_baseline_nvidia(
    acc: TotalsAcc,
    qty_nv_total: Decimal,
    qty_cpu: Optional[Decimal],
    qty_mem: Optional[Decimal],
    qty_eph: Optional[Decimal],
) -> ResourceWeights:
    """Baseline is total NVIDIA GPU count; per-kind GPU weights use ``qty_nv_total``."""
    w_cpu = (
        _decimal_ratio_string(qty_nv_total, qty_cpu)
        if qty_cpu is not None and qty_cpu > 0
        else None
    )
    w_mem = (
        _decimal_ratio_string(qty_nv_total, qty_mem) if qty_mem is not None else None
    )
    w_eph = (
        _decimal_ratio_string(qty_nv_total, qty_eph) if qty_eph is not None else None
    )
    w_nv = _nvidia_weights_from_numerator(acc.nvidia_by_kind, qty_nv_total)
    return ResourceWeights(
        cpu=w_cpu,
        memory=w_mem,
        ephemeral_storage=w_eph,
        nvidia_gpu=w_nv,
    )


def _compute_resource_weights(
    acc: TotalsAcc,
    *,
    baseline: str,
    units: str,
) -> Optional[ResourceWeights]:
    """
    Weights normalize pool totals to ``baseline``: that resource is ``1``; other
    fields are ratios in the same byte scale as ``units`` (for memory and
    ephemeral) or in GPU counts (for NVIDIA). For ``nvidia.com/gpu``, the
    baseline quantity is the **sum** of all NVIDIA GPU counts in the group.

    **Interpretation (heuristic):** comparative normalization, not schedulability.
    """
    qty_cpu, qty_mem, qty_eph = _weight_quantities(acc, units)

    if baseline == "cpu":
        if qty_cpu is None or qty_cpu <= 0:
            return None
        return _weights_baseline_cpu(acc, qty_cpu, qty_mem, qty_eph)

    if baseline == "memory":
        if qty_mem is None or qty_mem <= 0:
            return None
        return _weights_baseline_memory(acc, qty_cpu, qty_mem, qty_eph)

    if baseline == "ephemeral-storage":
        if qty_eph is None or qty_eph <= 0:
            return None
        return _weights_baseline_ephemeral(acc, qty_cpu, qty_mem, qty_eph)

    if baseline == "nvidia.com/gpu":
        qty_nv = _nvidia_pool_total(acc.nvidia_by_kind)
        if qty_nv is None or qty_nv <= 0:
            return None
        return _weights_baseline_nvidia(acc, qty_nv, qty_cpu, qty_mem, qty_eph)

    raise ValueError(f'unknown baseline: "{baseline}"')


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


def _totals_acc_to_node_type_resources(
    acc: TotalsAcc,
    node_count: int,
    *,
    units: str,
    baseline: str,
) -> NodeTypeResources:
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
            _bytes_to_resource_item(acc.memory_bytes, units)
            if acc.memory_bytes is not None
            else None
        ),
        ephemeral_storage=(
            _bytes_to_resource_item(acc.ephemeral_bytes, units)
            if acc.ephemeral_bytes is not None
            else None
        ),
        nvidia_gpu=_gpu_kind_totals_to_list(acc.nvidia_by_kind),
        amd_gpu=_gpu_kind_totals_to_list(acc.amd_by_kind),
        weights=_compute_resource_weights(
            acc,
            baseline=baseline,
            units=units,
        ),
    )


# =========================
# Public API
# =========================


def total(
    field: str = "capacity",
    *,
    node_label: str,
    units: str = "Gi",
    baseline: str = "cpu",
) -> Dict[str, Any]:
    """
    Calculate total cluster resources across all nodes.

    Args:
        field: Which field to sum: "capacity" (default) or "allocatable".
        node_label: Kubernetes node label key used to group results (callers
            such as the CLI supply the default; this function does not default it).
        units: Binary byte unit for memory and ephemeral totals (``B``, ``Ki``,
            ``Mi``, ``Gi``, ``Ti``, ``Pi``).
        baseline: Resource with weight ``1``; others are expressed per this
            baseline in ``units`` for memory/ephemeral. One of ``cpu``,
            ``memory``, ``ephemeral-storage``, or ``nvidia.com/gpu`` (total
            NVIDIA GPU count).

    Returns:
        A dict with ``node_label``, ``by_label_value`` (each key is a label
        value, or ``\"\"`` if unset), and per-group ``count`` plus resource maps.
    """
    label_key = node_label.strip()
    if not label_key:
        raise ValueError("node_label must be a non-empty string")

    unit_key = normalize_binary_unit(units)
    br = baseline.strip()
    if br not in _ALLOWED_BASELINES:
        allowed = ", ".join(sorted(_ALLOWED_BASELINES))
        raise ValueError(f'baseline must be one of: {allowed} (got "{baseline}")')

    # Validate inputs with Pydantic
    if field not in ("capacity", "allocatable"):
        raise ValueError('field must be "capacity" or "allocatable"')
    try:
        cfg = Settings(field=cast(Literal["capacity", "allocatable"], field))
    except ValidationError as e:
        raise ValueError(str(e)) from e

    v1 = _load_kube()
    nodes = _collect_nodes(v1)
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
        groups[nt_key] = _totals_acc_to_node_type_resources(
            acc,
            len(bucket),
            units=unit_key,
            baseline=br,
        )

    return ClusterResourcesResult(
        node_label=label_key,
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
    elif unit in _BINARY_UNIT_BYTES:
        scaled_bytes = _display_qty_to_bytes(v, unit) * scale
        int_bytes = max(0, int(scaled_bytes.to_integral_value(rounding=ROUND_HALF_UP)))
        out = _bytes_to_resource_item(int_bytes, unit)
        item["value"] = out.value
        item["unit"] = out.unit
    elif unit == "count":
        item["value"] = _format_decimal_report(v * scale)
    else:
        item["value"] = _format_decimal_report(v * scale)


def _scale_cluster_resources_payload(result: Dict[str, Any], scale: Decimal) -> None:
    """Multiply numeric ``value`` fields in-place (CLI ``--scale``).

    Leaves ``weights`` unchanged.
    """
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
    units: Annotated[
        str,
        typer.Option(
            "-u",
            "--units",
            help=(
                "Binary byte unit for memory and ephemeral totals: "
                '"B", "Ki", "Mi", "Gi", "Ti", "Pi".'
            ),
        ),
    ] = "Gi",
    baseline: Annotated[
        str,
        typer.Option(
            "-b",
            "--baseline",
            help=(
                "Resource with weight 1 for pool weights: "
                '"cpu", "memory", "ephemeral-storage", or "nvidia.com/gpu".'
            ),
        ),
    ] = "cpu",
    node_label: Annotated[
        str,
        typer.Option(
            "-n",
            "--node-label",
            help=(
                "Node label key used to group totals by label value "
                "(default only applies to this CLI, not to total())."
            ),
        ),
    ] = "skaha.opencadc.org/node-type",
):
    """
    Sum resources across all nodes, grouped by a node label.
    """
    assert field in ["capacity", "allocatable"]
    assert scale > 0.0 and scale <= 1.0, "Percentage must be in (0, 1]"
    try:
        result = total(
            field=field,
            node_label=node_label,
            units=units,
            baseline=baseline,
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
        console.print(
            {"response": response, "resource_quotas": response.get("items", [])}
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    app()
