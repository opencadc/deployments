from pathlib import Path
from types import SimpleNamespace

import pytest

from kueuer.lifecycle import scenarios, suite


def _performance_options() -> dict[str, object]:
    return {
        "profile": "local-safe",
        "counts_csv": "2,4",
        "duration": 5,
        "cores": 0.1,
        "ram": 0.25,
        "storage": 0.25,
        "wait": 5,
    }


def _eviction_options() -> dict[str, object]:
    return {
        "profile": "local-safe",
        "jobs": 8,
        "duration": 60,
        "cores": 2.0,
        "ram": 2.0,
        "storage": 2.0,
    }


def test_apply_control_scenario_is_noop(tmp_path: Path) -> None:
    report = scenarios.apply_scenario(
        scenario="control",
        output_dir=tmp_path.as_posix(),
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        run_cmd=lambda command: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    assert report["applied"] is False
    assert report["scenario"] == "control"


def test_backlog_scenario_applies_and_writes_snapshots(tmp_path: Path) -> None:
    calls = []

    def run_cmd(command):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    report = scenarios.apply_scenario(
        scenario="backlog",
        output_dir=tmp_path.as_posix(),
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        run_cmd=run_cmd,
    )

    assert report["applied"] is True
    assert Path(report["queue_before"]).exists()
    assert Path(report["queue_after"]).exists()
    assert report["localqueue"] == "skaha-local-queue-backlog"
    assert report["clusterqueue"] == "skaha-cluster-queue-backlog"
    assert any(command[:3] == ["kubectl", "apply", "-f"] for command in calls)
    before_text = Path(report["queue_before"]).read_text(encoding="utf-8")
    after_text = Path(report["queue_after"]).read_text(encoding="utf-8")
    assert "skaha-local-queue-backlog" in after_text
    assert "skaha-cluster-queue-backlog" in after_text


def test_backlog_scenario_aborts_before_apply_when_snapshot_fails(tmp_path: Path) -> None:
    calls = []

    def run_cmd(command):
        calls.append(command)
        return SimpleNamespace(returncode=1, stdout="", stderr="apply failed")

    report = scenarios.apply_scenario(
        scenario="backlog",
        output_dir=tmp_path.as_posix(),
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        run_cmd=run_cmd,
    )

    assert report["applied"] is False
    assert report["errors"]
    assert any(command[:3] == ["kubectl", "apply", "-f"] for command in calls)


def test_run_benchmark_suite_restores_scenario_after_failure(tmp_path: Path) -> None:
    restore_calls = {"n": 0}

    def scenario_apply(**kwargs):
        return {
            "scenario": "backlog",
            "applied": True,
            "queue_before": "before.yaml",
            "queue_after": "after.yaml",
            "localqueue": "scenario-local",
        }

    def scenario_restore(context, run_cmd):
        restore_calls["n"] += 1

    def performance_runner(**kwargs):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        suite.run_benchmark_suite(
            artifacts_dir=tmp_path.as_posix(),
            namespace="skaha-workload",
            localqueue="skaha-local-queue",
            priority="high",
            performance_options=_performance_options(),
            eviction_options=_eviction_options(),
            scenario="backlog",
            scenario_apply_fn=scenario_apply,
            scenario_restore_fn=scenario_restore,
            performance_runner=performance_runner,
            eviction_runner=lambda **kwargs: None,
        )

    assert restore_calls["n"] == 1


def test_run_benchmark_suite_uses_scenario_queue_names(tmp_path: Path) -> None:
    captured = {}

    def scenario_apply(**kwargs):
        del kwargs
        return {
            "scenario": "backlog",
            "applied": True,
            "queue_before": "before.yaml",
            "queue_after": "after.yaml",
            "localqueue": "scenario-local",
            "clusterqueue": "scenario-cluster",
            "errors": [],
        }

    def perf_runner(**kwargs):
        captured["performance"] = kwargs

    def evict_runner(**kwargs):
        captured["evictions"] = kwargs

    suite.run_benchmark_suite(
        artifacts_dir=tmp_path.as_posix(),
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        priority="high",
        performance_options=_performance_options(),
        eviction_options=_eviction_options(),
        scenario="backlog",
        scenario_apply_fn=scenario_apply,
        scenario_restore_fn=lambda context, run_cmd: {"restored": True, "error": ""},
        performance_runner=perf_runner,
        eviction_runner=evict_runner,
    )

    assert captured["performance"]["kueue"] == "scenario-local"
    assert captured["evictions"]["kueue"] == "scenario-local"


def test_run_benchmark_suite_restores_scenario_when_observe_export_fails(tmp_path: Path) -> None:
    restore_calls = {"n": 0}

    class BrokenCollector:
        def __init__(self, namespace: str, interval_seconds: float):
            del namespace
            del interval_seconds

        def start(self) -> None:
            return None

        def stop(self) -> None:
            return None

        def write_series(self, output_dir: str):
            del output_dir
            raise RuntimeError("disk full")

    def scenario_apply(**kwargs):
        return {"scenario": "backlog", "applied": True, "queue_before": "before.yaml"}

    def scenario_restore(context, run_cmd):
        del context
        del run_cmd
        restore_calls["n"] += 1
        return {"restored": True, "error": ""}

    with pytest.raises(RuntimeError):
        suite.run_benchmark_suite(
            artifacts_dir=tmp_path.as_posix(),
            namespace="skaha-workload",
            localqueue="skaha-local-queue",
            priority="high",
            performance_options=_performance_options(),
            eviction_options=_eviction_options(),
            scenario="backlog",
            observe=True,
            collector_factory=BrokenCollector,
            scenario_apply_fn=scenario_apply,
            scenario_restore_fn=scenario_restore,
            performance_runner=lambda **kwargs: None,
            eviction_runner=lambda **kwargs: None,
        )

    assert restore_calls["n"] == 1
