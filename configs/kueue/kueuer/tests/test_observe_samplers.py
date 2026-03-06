import json
from dataclasses import dataclass
from typing import Callable, Dict, List

from kueuer.observe import samplers


@dataclass
class FakeResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def _runner(responses: Dict[str, FakeResult]) -> Callable[[List[str]], FakeResult]:
    def _run(command: List[str]) -> FakeResult:
        key = " ".join(command)
        return responses.get(key, FakeResult(returncode=1, stderr="missing"))

    return _run


def test_parse_kubectl_top_values() -> None:
    cpu, memory = samplers.parse_top_values("250m", "1536Mi")
    assert cpu == 0.25
    assert memory == 1536 * 1024 * 1024


def test_parse_apiserver_non_watch_latency_quantiles() -> None:
    metrics = "\n".join(
        [
            'apiserver_request_duration_seconds_bucket{verb="LIST",le="0.1"} 5',
            'apiserver_request_duration_seconds_bucket{verb="LIST",le="0.5"} 40',
            'apiserver_request_duration_seconds_bucket{verb="LIST",le="1"} 98',
            'apiserver_request_duration_seconds_bucket{verb="LIST",le="2"} 100',
            'apiserver_request_duration_seconds_bucket{verb="WATCH",le="0.1"} 100',
        ]
    )
    parsed = samplers.parse_apiserver_latency(metrics)
    assert parsed["apiserver_non_watch_request_p95_seconds"] == 1.0
    assert parsed["apiserver_non_watch_request_p99_seconds"] == 2.0


def test_collect_sampler_snapshot_handles_partial_unavailable() -> None:
    localqueues = {
        "items": [
            {
                "status": {
                    "pendingWorkloads": 12,
                    "admittedWorkloads": 4,
                }
            }
        ]
    }
    run = _runner(
        {
            "kubectl top pod -n kueue-system --no-headers": FakeResult(
                returncode=1, stderr="metrics unavailable"
            ),
            "kubectl get --raw /metrics": FakeResult(
                returncode=0,
                stdout='apiserver_request_duration_seconds_bucket{verb="LIST",le="1"} 1\n',
            ),
            "kubectl get localqueue -n skaha-workload -o json": FakeResult(
                returncode=0,
                stdout=json.dumps(localqueues),
            ),
            "kubectl get workload -n skaha-workload -o json": FakeResult(
                returncode=0,
                stdout=json.dumps({"items": []}),
            ),
        }
    )

    snapshot = samplers.collect_sampler_snapshot(
        namespace="skaha-workload",
        run_cmd=run,
    )

    assert len(snapshot["samples"]) == 3
    by_source = {item.source: item for item in snapshot["samples"]}
    assert by_source["kueue-controller"].available is False
    assert by_source["apiserver"].available is True
    assert by_source["queues"].values["pending_workloads"] == 12.0
