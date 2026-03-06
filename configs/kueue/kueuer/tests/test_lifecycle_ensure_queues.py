from dataclasses import dataclass
from typing import Callable, Dict, List

from kueuer.lifecycle import queues


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


def test_ensure_queues_valid_when_objects_exist() -> None:
    run = _runner(
        {
            "kubectl get clusterqueue skaha-cluster-queue": FakeResult(0),
            "kubectl get localqueue -n skaha-workload skaha-local-queue": FakeResult(0),
            "kubectl get workloadpriorityclass low": FakeResult(0),
            "kubectl get workloadpriorityclass medium": FakeResult(0),
            "kubectl get workloadpriorityclass high": FakeResult(0),
        }
    )
    report = queues.ensure_queues(
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        apply_if_missing=False,
        run_cmd=run,
    )
    assert report["ok"] is True
    assert report["missing"] == []


def test_ensure_queues_missing_without_apply_emits_manual_commands() -> None:
    run = _runner({})
    report = queues.ensure_queues(
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        apply_if_missing=False,
        run_cmd=run,
    )
    assert report["ok"] is False
    assert report["missing"]
    assert report["manual_commands"]


def test_ensure_queues_apply_failure_emits_manual_commands() -> None:
    run = _runner(
        {
            "kubectl apply -f dev/clusterQueue.config.yaml": FakeResult(1, stderr="forbidden"),
            "kubectl apply -f dev/localQueue.config.yaml": FakeResult(1, stderr="forbidden"),
        }
    )
    report = queues.ensure_queues(
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        apply_if_missing=True,
        run_cmd=run,
    )
    assert report["ok"] is False
    assert report["manual_commands"]
