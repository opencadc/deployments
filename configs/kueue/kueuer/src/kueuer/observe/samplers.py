"""Sampling helpers for controller, API server, and queue state."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Tuple

from kueuer.lifecycle.shell import run_command
from kueuer.observe.models import ObservationSample

_CPU_PATTERN = re.compile(r"^(?P<value>[0-9]*\.?[0-9]+)(?P<suffix>m?)$")
_MEM_PATTERN = re.compile(r"^(?P<value>[0-9]*\.?[0-9]+)(?P<suffix>Ki|Mi|Gi|Ti|K|M|G|T)?$")
_BUCKET_PATTERN = re.compile(
    r'apiserver_request_duration_seconds_bucket\{([^}]*)le="(?P<le>[^"]+)"([^}]*)\}\s+(?P<count>[0-9]+(?:\.[0-9]+)?)'
)
_VERB_PATTERN = re.compile(r'verb="(?P<verb>[^"]+)"')


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def parse_top_values(cpu_raw: str, memory_raw: str) -> Tuple[float, float]:
    """Parse CPU and memory values from `kubectl top` output columns."""
    cpu_match = _CPU_PATTERN.match(cpu_raw.strip())
    if not cpu_match:
        raise ValueError(f"invalid cpu quantity: {cpu_raw}")
    cpu_value = float(cpu_match.group("value"))
    if cpu_match.group("suffix") == "m":
        cpu_value = cpu_value / 1000.0

    mem_match = _MEM_PATTERN.match(memory_raw.strip())
    if not mem_match:
        raise ValueError(f"invalid memory quantity: {memory_raw}")
    mem_value = float(mem_match.group("value"))
    mem_suffix = mem_match.group("suffix") or ""
    multipliers = {
        "": 1,
        "K": 1000,
        "M": 1000**2,
        "G": 1000**3,
        "T": 1000**4,
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "Ti": 1024**4,
    }
    mem_value = mem_value * multipliers[mem_suffix]
    return cpu_value, mem_value


def parse_apiserver_latency(metrics_text: str) -> Dict[str, float]:
    """Estimate API-server non-watch latency p95/p99 from histogram buckets."""
    buckets: Dict[float, float] = {}
    for line in metrics_text.splitlines():
        if "apiserver_request_duration_seconds_bucket" not in line:
            continue
        verb_match = _VERB_PATTERN.search(line)
        if verb_match and verb_match.group("verb").upper() == "WATCH":
            continue
        bucket_match = _BUCKET_PATTERN.search(line)
        if not bucket_match:
            continue
        le_raw = bucket_match.group("le")
        if le_raw == "+Inf":
            le = math.inf
        else:
            le = float(le_raw)
        count = float(bucket_match.group("count"))
        buckets[le] = buckets.get(le, 0.0) + count

    if not buckets:
        return {
            "apiserver_non_watch_request_p95_seconds": 0.0,
            "apiserver_non_watch_request_p99_seconds": 0.0,
        }

    ordered = sorted(buckets.items(), key=lambda item: item[0])
    total = max(item[1] for item in ordered)
    if total <= 0:
        return {
            "apiserver_non_watch_request_p95_seconds": 0.0,
            "apiserver_non_watch_request_p99_seconds": 0.0,
        }

    def _quantile(target: float) -> float:
        threshold = total * target
        for upper, cumulative in ordered:
            if cumulative >= threshold:
                if math.isinf(upper):
                    finite = [value for value, _ in ordered if not math.isinf(value)]
                    return max(finite) if finite else 0.0
                return float(upper)
        last = ordered[-1][0]
        return 0.0 if math.isinf(last) else float(last)

    return {
        "apiserver_non_watch_request_p95_seconds": _quantile(0.95),
        "apiserver_non_watch_request_p99_seconds": _quantile(0.99),
    }


def _sample_kueue_controller(
    run_cmd: Callable[[List[str]], Any],
    namespace: str = "kueue-system",
) -> ObservationSample:
    """Sample Kueue controller CPU, memory, and restart counters."""
    top_result = run_cmd(["kubectl", "top", "pod", "-n", namespace, "--no-headers"])
    values: Dict[str, float] = {
        "kueue_controller_cpu_cores": 0.0,
        "kueue_controller_memory_working_set_bytes": 0.0,
        "kueue_controller_restart_count": 0.0,
    }
    labels: Dict[str, str] = {}
    available = top_result.returncode == 0
    if top_result.returncode == 0:
        for line in top_result.stdout.splitlines():
            if "kueue-controller-manager" not in line:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            cpu, memory = parse_top_values(parts[1], parts[2])
            values["kueue_controller_cpu_cores"] = cpu
            values["kueue_controller_memory_working_set_bytes"] = memory
            labels["pod"] = parts[0]
            break
    else:
        labels["error"] = top_result.stderr.strip() or "kubectl top failed"

    restart_result = run_cmd(["kubectl", "get", "pods", "-n", namespace, "-o", "json"])
    if restart_result.returncode == 0:
        payload = json.loads(restart_result.stdout or "{}")
        restart_total = 0.0
        for item in payload.get("items", []):
            name = item.get("metadata", {}).get("name", "")
            if "kueue-controller-manager" not in name:
                continue
            for status in item.get("status", {}).get("containerStatuses", []) or []:
                restart_total += float(status.get("restartCount", 0) or 0)
        values["kueue_controller_restart_count"] = restart_total
    else:
        available = False

    return ObservationSample(
        timestamp=utc_now_iso(),
        source="kueue-controller",
        available=available,
        values=values,
        labels=labels,
    )


def _sample_apiserver(run_cmd: Callable[[List[str]], Any]) -> ObservationSample:
    """Sample API-server latency and inflight request counters."""
    result = run_cmd(["kubectl", "get", "--raw", "/metrics"])
    values = {
        "apiserver_non_watch_request_p95_seconds": 0.0,
        "apiserver_non_watch_request_p99_seconds": 0.0,
        "apiserver_current_inflight_read_requests": 0.0,
        "apiserver_current_inflight_write_requests": 0.0,
    }
    labels: Dict[str, str] = {}
    available = result.returncode == 0
    if result.returncode == 0:
        values.update(parse_apiserver_latency(result.stdout))

        for line in result.stdout.splitlines():
            if line.startswith("apiserver_current_inflight_requests"):
                if 'request_kind="readOnly"' in line:
                    values["apiserver_current_inflight_read_requests"] = float(
                        line.split()[-1]
                    )
                if 'request_kind="mutating"' in line:
                    values["apiserver_current_inflight_write_requests"] = float(
                        line.split()[-1]
                    )
    else:
        labels["error"] = result.stderr.strip() or "kubectl raw metrics failed"

    return ObservationSample(
        timestamp=utc_now_iso(),
        source="apiserver",
        available=available,
        values=values,
        labels=labels,
    )


def _sample_queues(namespace: str, run_cmd: Callable[[List[str]], Any]) -> ObservationSample:
    """Sample queue depth, wait time, and benchmark OOMKilled pod counters."""
    queue_result = run_cmd(["kubectl", "get", "localqueue", "-n", namespace, "-o", "json"])
    workload_result = run_cmd(["kubectl", "get", "workload", "-n", namespace, "-o", "json"])
    pod_result = run_cmd(["kubectl", "get", "pods", "-n", namespace, "-o", "json"])

    available = queue_result.returncode == 0 and workload_result.returncode == 0
    values = {
        "pending_workloads": 0.0,
        "admitted_workloads": 0.0,
        "workload_queue_wait_p50_seconds": 0.0,
        "workload_queue_wait_p95_seconds": 0.0,
    }
    labels: Dict[str, str] = {}

    if available:
        queue_payload = json.loads(queue_result.stdout or "{}")
        pending = 0.0
        admitted = 0.0
        for item in queue_payload.get("items", []):
            status = item.get("status", {})
            pending += float(status.get("pendingWorkloads", 0) or 0)
            admitted += float(status.get("admittedWorkloads", 0) or 0)
        values["pending_workloads"] = pending
        values["admitted_workloads"] = admitted

        workload_payload = json.loads(workload_result.stdout or "{}")
        waits: List[float] = []
        for item in workload_payload.get("items", []):
            created = item.get("metadata", {}).get("creationTimestamp")
            admitted_at = None
            for condition in item.get("status", {}).get("conditions", []) or []:
                if condition.get("type") == "Admitted" and condition.get("status") == "True":
                    admitted_at = condition.get("lastTransitionTime")
                    break
            if not created or not admitted_at:
                continue
            try:
                created_ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
                admitted_ts = datetime.fromisoformat(admitted_at.replace("Z", "+00:00"))
                waits.append(max((admitted_ts - created_ts).total_seconds(), 0.0))
            except ValueError:
                continue

        if waits:
            ordered = sorted(waits)
            midpoint = len(ordered) // 2
            if len(ordered) % 2 == 0:
                p50 = (ordered[midpoint - 1] + ordered[midpoint]) / 2.0
            else:
                p50 = ordered[midpoint]
            index95 = min(int(math.ceil(len(ordered) * 0.95)) - 1, len(ordered) - 1)
            values["workload_queue_wait_p50_seconds"] = float(p50)
            values["workload_queue_wait_p95_seconds"] = float(ordered[index95])

        if pod_result.returncode == 0:
            pods_payload = json.loads(pod_result.stdout or "{}")
            oomkilled = 0
            for item in pods_payload.get("items", []):
                name = item.get("metadata", {}).get("name", "")
                if not (name.startswith("direct-") or name.startswith("kueue-")):
                    continue
                for status in item.get("status", {}).get("containerStatuses", []) or []:
                    reason = (
                        status.get("state", {})
                        .get("terminated", {})
                        .get("reason", "")
                    )
                    if reason == "OOMKilled":
                        oomkilled += 1
                        break
            values["benchmark_oomkilled_pods"] = float(oomkilled)
        else:
            labels["oom_metric_error"] = (
                pod_result.stderr.strip() or "pod query failed for OOM metric"
            )
    else:
        labels["error"] = "queue or workload query failed"

    return ObservationSample(
        timestamp=utc_now_iso(),
        source="queues",
        available=available,
        values=values,
        labels=labels,
    )


def collect_sampler_snapshot(
    namespace: str,
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    """Collect one multi-source observation snapshot."""
    samples = [
        _sample_kueue_controller(run_cmd=run_cmd),
        _sample_apiserver(run_cmd=run_cmd),
        _sample_queues(namespace=namespace, run_cmd=run_cmd),
    ]
    capabilities = {sample.source: sample.available for sample in samples}
    return {"samples": samples, "capabilities": capabilities}
