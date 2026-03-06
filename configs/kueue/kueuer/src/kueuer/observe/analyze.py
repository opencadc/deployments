"""Observation aggregation and policy evaluation."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Sequence, Tuple

from kueuer.observe.models import ObservationPolicyResult, ObservationSample, ObservationSummary


def _p95(values: List[float]) -> float:
    """Return the p95 value from a numeric sample list."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(math.ceil(len(ordered) * 0.95)) - 1, len(ordered) - 1)
    return float(ordered[index])


def _resolve_metric(
    summary_metrics: Dict[str, float],
    keys: Sequence[str],
) -> Tuple[float | None, str | None]:
    """Return the first available metric value and its key."""
    for key in keys:
        if key in summary_metrics:
            return float(summary_metrics[key]), key
    return None, None


def summarize_observations(
    samples: Iterable[ObservationSample],
    capabilities: Dict[str, bool],
) -> ObservationSummary:
    """Aggregate raw observation samples into summary metrics."""
    bucket: Dict[str, List[float]] = {}
    for sample in samples:
        if not sample.available:
            continue
        for metric, value in sample.values.items():
            bucket.setdefault(metric, []).append(float(value))

    aggregate: Dict[str, float] = {}
    for metric, values in bucket.items():
        metric_max = float(max(values))
        metric_min = float(min(values))
        aggregate[f"{metric}_max"] = metric_max
        aggregate[f"{metric}_min"] = metric_min
        aggregate[f"{metric}_delta"] = metric_max - metric_min
        aggregate[f"{metric}_p95"] = _p95(values)

    return ObservationSummary(
        generated_at=datetime.now(timezone.utc).isoformat(),
        aggregate_metrics=aggregate,
        capabilities=capabilities,
    )


def evaluate_policy(
    summary_metrics: Dict[str, float],
    baseline_metrics: Dict[str, float] | None = None,
) -> ObservationPolicyResult:
    """Evaluate rollout policy checks from summarized observation metrics."""
    baseline_metrics = baseline_metrics or {}

    checks: Dict[str, str] = {}
    violations: List[str] = []

    memory_max, _ = _resolve_metric(
        summary_metrics,
        ("kueue_controller_memory_working_set_bytes_max",),
    )
    if memory_max is None:
        checks["kueue_controller_memory_working_set_bytes_max"] = "fail"
        violations.append("kueue-controller memory metric unavailable")
    elif memory_max <= float(2 * 1024**3):
        checks["kueue_controller_memory_working_set_bytes_max"] = "pass"
    else:
        checks["kueue_controller_memory_working_set_bytes_max"] = "fail"
        violations.append("kueue-controller memory exceeded 2GiB")

    restart_delta, _ = _resolve_metric(
        summary_metrics,
        (
            "kueue_controller_restart_count_delta",
            "kueue_controller_restart_count_delta_max",
        ),
    )
    restart_check_key = "kueue_controller_restart_count_delta"
    if restart_delta is None:
        checks[restart_check_key] = "fail"
        violations.append("restart delta metric unavailable")
    elif restart_delta == 0.0:
        checks[restart_check_key] = "pass"
    else:
        checks[restart_check_key] = "fail"
        violations.append("kueue-controller restart delta is non-zero")

    oom_max, _ = _resolve_metric(
        summary_metrics,
        (
            "benchmark_oomkilled_pods_max",
            "pods_oomkilled_max",
        ),
    )
    oom_check_key = "benchmark_oomkilled_pods_max"
    if oom_max is None:
        checks[oom_check_key] = "fail"
        violations.append("OOM metric unavailable for policy evaluation")
    elif oom_max == 0.0:
        checks[oom_check_key] = "pass"
    else:
        checks[oom_check_key] = "fail"
        violations.append("OOMKilled pods observed during benchmark")

    apiserver_check_key = "apiserver_non_watch_request_p95_seconds_delta_pct"
    current_p95, _ = _resolve_metric(
        summary_metrics,
        ("apiserver_non_watch_request_p95_seconds_p95",),
    )
    if current_p95 is None:
        checks[apiserver_check_key] = "fail"
        violations.append("apiserver p95 metric unavailable")
        status = "pass" if not violations else "fail"
        return ObservationPolicyResult(status=status, checks=checks, violations=violations)

    baseline_p95 = float(baseline_metrics.get("apiserver_non_watch_request_p95_seconds_p95", 0.0))
    if baseline_p95 > 0:
        delta_pct = ((current_p95 - baseline_p95) / baseline_p95) * 100.0
    else:
        delta_pct = 0.0
    checks[apiserver_check_key] = (
        "pass" if delta_pct <= 20.0 else "fail"
    )
    if delta_pct > 20.0:
        violations.append("apiserver p95 non-watch latency increased by more than 20%")

    status = "pass" if not violations else "fail"
    return ObservationPolicyResult(status=status, checks=checks, violations=violations)
