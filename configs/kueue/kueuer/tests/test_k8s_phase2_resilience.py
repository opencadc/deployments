from types import SimpleNamespace

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
