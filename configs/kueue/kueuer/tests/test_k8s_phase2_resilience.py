from types import SimpleNamespace

import pytest

from kueuer.benchmarks import k8s


def test_chunk_ranges_even_and_tail() -> None:
    assert k8s.chunk_ranges(6, 3) == [(0, 3), (3, 6)]
    assert k8s.chunk_ranges(7, 3) == [(0, 3), (3, 6), (6, 7)]


def test_stress_cpu_workers_respects_fractional_requests() -> None:
    assert k8s.stress_cpu_workers(0.1) == 1
    assert k8s.stress_cpu_workers(1.0) == 1
    assert k8s.stress_cpu_workers(2.2) == 3


def test_pod_outcomes_counts_oomkilled() -> None:
    running = SimpleNamespace(
        status=SimpleNamespace(phase="Running", container_statuses=None)
    )
    succeeded = SimpleNamespace(
        status=SimpleNamespace(phase="Succeeded", container_statuses=None)
    )
    failed_oom = SimpleNamespace(
        status=SimpleNamespace(
            phase="Failed",
            container_statuses=[
                SimpleNamespace(
                    state=SimpleNamespace(
                        terminated=SimpleNamespace(reason="OOMKilled")
                    )
                )
            ],
        )
    )

    summary = k8s.summarize_pod_statuses([running, succeeded, failed_oom])
    assert summary["pods_total"] == 3
    assert summary["pods_running"] == 1
    assert summary["pods_succeeded"] == 1
    assert summary["pods_failed"] == 1
    assert summary["pods_oomkilled"] == 1


def test_kueue_controller_restarts_handles_api_errors(monkeypatch) -> None:
    monkeypatch.setattr(k8s.config, "load_kube_config", lambda: None)

    class FakeCoreV1Api:
        def list_namespaced_pod(self, namespace):
            raise RuntimeError("forbidden")

    monkeypatch.setattr(k8s.client, "CoreV1Api", FakeCoreV1Api)

    assert k8s.kueue_controller_restarts() == 0


def test_stress_vm_bytes_mb_uses_safer_default_fraction() -> None:
    assert k8s.DEFAULT_STRESS_VM_MEMORY_FRACTION == 0.4
    assert k8s.stress_vm_bytes_mb(
        ram_gb=1.0,
        vm_memory_fraction=k8s.DEFAULT_STRESS_VM_MEMORY_FRACTION,
    ) == pytest.approx(409.6)


def test_stress_vm_bytes_mb_validates_fraction_bounds() -> None:
    with pytest.raises(ValueError):
        k8s.stress_vm_bytes_mb(ram_gb=1.0, vm_memory_fraction=0.0)
    with pytest.raises(ValueError):
        k8s.stress_vm_bytes_mb(ram_gb=1.0, vm_memory_fraction=1.0)


def test_is_high_oom_risk_flags_tight_memory_headroom() -> None:
    assert k8s.is_high_oom_risk(ram_gb=1.0, vm_memory_fraction=0.8) is True
    assert k8s.is_high_oom_risk(ram_gb=1.0, vm_memory_fraction=0.55) is False
