from dataclasses import dataclass
from typing import Callable, Dict, List

from typer.testing import CliRunner

from kueuer.cli import app
from kueuer.lifecycle import preflight
from kueuer.lifecycle import commands


@dataclass
class FakeResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def _runner(responses: Dict[str, FakeResult]) -> Callable[[List[str]], FakeResult]:
    def _run(command: List[str]) -> FakeResult:
        key = " ".join(command)
        return responses.get(key, FakeResult(returncode=0, stdout="ok"))

    return _run


runner = CliRunner()


def test_run_preflight_success() -> None:
    run = _runner(
        {
            "kubectl config current-context": FakeResult(0, "minikube\n"),
            "kubectl cluster-info": FakeResult(0, "ok\n"),
            "kubectl auth can-i create jobs -n skaha-workload": FakeResult(0, "yes\n"),
        }
    )
    report = preflight.run_preflight(
        namespace="skaha-workload",
        command_exists_fn=lambda cmd: True,
        run_cmd=run,
    )
    assert report["ok"] is True
    assert report["context"] == "minikube"


def test_run_preflight_success_without_helm() -> None:
    run = _runner(
        {
            "kubectl config current-context": FakeResult(0, "minikube\n"),
            "kubectl cluster-info": FakeResult(0, "ok\n"),
            "kubectl auth can-i create jobs -n skaha-workload": FakeResult(0, "yes\n"),
        }
    )
    report = preflight.run_preflight(
        namespace="skaha-workload",
        command_exists_fn=lambda cmd: cmd == "kubectl",
        run_cmd=run,
    )
    assert report["ok"] is True


def test_run_preflight_fails_when_kubectl_missing() -> None:
    report = preflight.run_preflight(
        namespace="skaha-workload",
        command_exists_fn=lambda cmd: cmd != "kubectl",
        run_cmd=lambda _cmd: FakeResult(0, "ok"),
    )
    assert report["ok"] is False
    assert "kubectl" in " ".join(report["errors"]).lower()


def test_run_preflight_fails_on_cluster_unreachable() -> None:
    run = _runner(
        {
            "kubectl config current-context": FakeResult(0, "minikube\n"),
            "kubectl cluster-info": FakeResult(1, "", "connection refused"),
        }
    )
    report = preflight.run_preflight(
        namespace="skaha-workload",
        command_exists_fn=lambda cmd: True,
        run_cmd=run,
    )
    assert report["ok"] is False
    assert "cluster-info" in " ".join(report["errors"]).lower()


def test_preflight_command_prints_verbose_inventory(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        commands,
        "run_cluster_preflight",
        lambda **kwargs: {
            "ok": True,
            "errors": [],
            "remediation": [],
            "context": "production-a",
            "checks": {
                "access": {
                    "binary:kubectl": True,
                    "context": True,
                    "cluster-info": True,
                    "can-create-jobs": True,
                },
                "kueue": {
                    "ok": True,
                    "errors": [],
                    "remediation": [],
                    "available_replicas": 1,
                    "pods": [
                        "kueue-controller-manager-abc 2/2 Running 0 1m",
                    ],
                },
                "queues": {
                    "ok": True,
                    "missing": [],
                    "errors": [],
                    "manual_commands": [],
                    "applied": False,
                    "inventory": {
                        "clusterqueues": ["clusterqueue/skaha-cluster-queue"],
                        "localqueues": [
                            "localqueue.kueue.x-k8s.io/skaha-local-queue",
                            "localqueue.kueue.x-k8s.io/canfar-b-local-queue",
                        ],
                        "workloadpriorityclasses": [
                            "workloadpriorityclass.kueue.x-k8s.io/low",
                            "workloadpriorityclass.kueue.x-k8s.io/medium",
                            "workloadpriorityclass.kueue.x-k8s.io/high",
                        ],
                    },
                },
            },
        },
    )

    result = runner.invoke(
        app,
        [
            "lifecycle",
            "preflight",
            "--artifacts-dir",
            tmp_path.as_posix(),
            "--run-id",
            "run-a",
        ],
    )

    assert result.exit_code == 0
    assert "preflight ok for run run-a" in result.stdout
    assert "Context: production-a" in result.stdout
    assert "Access checks:" in result.stdout
    assert "Kueue health:" in result.stdout
    assert "ClusterQueues:" in result.stdout
    assert "skaha-cluster-queue" in result.stdout
    assert "LocalQueues:" in result.stdout
    assert "canfar-b-local-queue" in result.stdout
    assert "PriorityClasses:" in result.stdout


def test_run_cluster_preflight_collects_queue_inventory(monkeypatch) -> None:
    monkeypatch.setattr(
        commands,
        "run_preflight",
        lambda namespace: {
            "ok": True,
            "context": "ctx-a",
            "checks": {},
            "errors": [],
        },
    )
    monkeypatch.setattr(
        commands,
        "validate_kueue_health",
        lambda: {
            "ok": True,
            "errors": [],
            "remediation": [],
            "available_replicas": 1,
            "pods": ["kueue-controller-manager-abc 1/1 Running 0 1m"],
        },
    )
    monkeypatch.setattr(
        commands,
        "ensure_queues_state",
        lambda **kwargs: {
            "ok": True,
            "missing": [],
            "errors": [],
            "manual_commands": [],
            "applied": False,
        },
    )

    def fake_run_cmd(command: List[str]) -> FakeResult:
        key = " ".join(command)
        mapping = {
            "kubectl get clusterqueue -o name": FakeResult(
                0, "clusterqueue/skaha-cluster-queue\n"
            ),
            "kubectl get localqueue -A -o name": FakeResult(
                0,
                "localqueue.kueue.x-k8s.io/skaha-local-queue\n"
                "localqueue.kueue.x-k8s.io/canfar-b-local-queue\n",
            ),
            "kubectl get workloadpriorityclass -o name": FakeResult(
                0,
                "workloadpriorityclass.kueue.x-k8s.io/low\n"
                "workloadpriorityclass.kueue.x-k8s.io/medium\n"
                "workloadpriorityclass.kueue.x-k8s.io/high\n",
            ),
        }
        return mapping.get(key, FakeResult(1, "", "missing"))

    report = commands.run_cluster_preflight(
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        apply_if_missing=True,
        run_cmd=fake_run_cmd,
    )

    inventory = report["checks"]["queues"]["inventory"]
    assert inventory["clusterqueues"] == ["clusterqueue/skaha-cluster-queue"]
    assert len(inventory["localqueues"]) == 2
    assert inventory["workloadpriorityclasses"][-1].endswith("/high")
