from pathlib import Path

import pytest

from kueuer.lifecycle import suite


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


class FakeCollector:
    def __init__(self, namespace: str, interval_seconds: float):
        self.namespace = namespace
        self.interval_seconds = interval_seconds
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def write_series(self, output_dir: str):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        csv = Path(output_dir) / "timeseries.csv"
        csv.write_text("metric,value\n", encoding="utf-8")
        return {
            "timeseries_csv": csv.as_posix(),
        }


def test_run_benchmark_suite_observe_writes_artifacts(tmp_path: Path) -> None:
    def perf_runner(**kwargs):
        Path(kwargs["output_dir"]).mkdir(parents=True, exist_ok=True)
        Path(kwargs["output_dir"], "performance.csv").write_text("ok", encoding="utf-8")

    def evict_runner(**kwargs):
        Path(kwargs["output_dir"]).mkdir(parents=True, exist_ok=True)
        Path(kwargs["output_dir"], "evictions.yaml").write_text("ok", encoding="utf-8")

    report = suite.run_benchmark_suite(
        artifacts_dir=tmp_path.as_posix(),
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        priority="high",
        performance_options=_performance_options(),
        eviction_options=_eviction_options(),
        observe=True,
        observe_interval_seconds=1.0,
        collector_factory=FakeCollector,
        performance_runner=perf_runner,
        eviction_runner=evict_runner,
    )

    assert "observe" in report
    assert Path(report["observe"]["timeseries_csv"]).exists()


def test_run_benchmark_suite_observe_stops_collector_on_failure(tmp_path: Path) -> None:
    collector_ref = {"instance": None}

    def collector_factory(namespace: str, interval_seconds: float):
        instance = FakeCollector(namespace=namespace, interval_seconds=interval_seconds)
        collector_ref["instance"] = instance
        return instance

    def perf_runner(**kwargs):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        suite.run_benchmark_suite(
            artifacts_dir=tmp_path.as_posix(),
            namespace="skaha-workload",
            localqueue="skaha-local-queue",
            priority="high",
            performance_options=_performance_options(),
            eviction_options=_eviction_options(),
            observe=True,
            collector_factory=collector_factory,
            performance_runner=perf_runner,
            eviction_runner=lambda **kwargs: None,
        )

    assert collector_ref["instance"] is not None
    assert collector_ref["instance"].stopped is True
