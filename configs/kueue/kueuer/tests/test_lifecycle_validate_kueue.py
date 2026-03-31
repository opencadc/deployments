from dataclasses import dataclass
from typing import Callable, Dict, List

from kueuer.lifecycle import kueue_validate


@dataclass
class FakeResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def _runner(responses: Dict[str, FakeResult]) -> Callable[[List[str]], FakeResult]:
    def _run(command: List[str]) -> FakeResult:
        return responses.get(" ".join(command), FakeResult(returncode=1, stderr="missing"))

    return _run


def test_validate_kueue_healthy() -> None:
    run = _runner(
        {
            "kubectl get namespace kueue-system": FakeResult(0, "kueue-system"),
            "kubectl get deploy -n kueue-system kueue-controller-manager -o jsonpath={.status.availableReplicas}": FakeResult(0, "1"),
            "kubectl get pods -n kueue-system --no-headers": FakeResult(
                0, "kueue-controller-manager-abc 1/1 Running 0 1m"
            ),
        }
    )
    report = kueue_validate.validate_kueue_health(run_cmd=run)
    assert report["ok"] is True


def test_validate_kueue_accepts_multi_container_running_pods() -> None:
    run = _runner(
        {
            "kubectl get namespace kueue-system": FakeResult(0, "kueue-system"),
            "kubectl get deploy -n kueue-system kueue-controller-manager -o jsonpath={.status.availableReplicas}": FakeResult(0, "1"),
            "kubectl get pods -n kueue-system --no-headers": FakeResult(
                0, "kueue-controller-manager-abc 2/2 Running 0 1m"
            ),
        }
    )
    report = kueue_validate.validate_kueue_health(run_cmd=run)
    assert report["ok"] is True


def test_validate_kueue_missing_namespace() -> None:
    run = _runner(
        {
            "kubectl get namespace kueue-system": FakeResult(1, "", "NotFound"),
        }
    )
    report = kueue_validate.validate_kueue_health(run_cmd=run)
    assert report["ok"] is False
    assert "kueue-system" in " ".join(report["errors"])
    assert report["remediation"]


def test_validate_kueue_unhealthy_controller() -> None:
    run = _runner(
        {
            "kubectl get namespace kueue-system": FakeResult(0, "kueue-system"),
            "kubectl get deploy -n kueue-system kueue-controller-manager -o jsonpath={.status.availableReplicas}": FakeResult(0, "0"),
            "kubectl get pods -n kueue-system --no-headers": FakeResult(0, "kueue-controller-manager-abc 0/1 CrashLoopBackOff 5 1m"),
        }
    )
    report = kueue_validate.validate_kueue_health(run_cmd=run)
    assert report["ok"] is False
    assert "controller" in " ".join(report["errors"]).lower()
