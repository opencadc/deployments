from pathlib import Path

from kueuer.lifecycle import suite


def _performance_options() -> dict[str, object]:
    return {
        "profile": "local-safe",
        "counts_csv": "2,4",
        "duration": 7,
        "cores": 0.2,
        "ram": 0.5,
        "storage": 0.75,
        "wait": 3,
    }


def _eviction_options() -> dict[str, object]:
    return {
        "profile": "local-safe",
        "jobs": 8,
        "duration": 7,
        "cores": 1.5,
        "ram": 1.75,
        "storage": 2.25,
    }


def test_run_benchmark_suite_builds_expected_outputs(tmp_path: Path) -> None:
    called = {"performance": None, "evictions": None}

    def perf_runner(**kwargs):
        called["performance"] = kwargs
        perf_dir = Path(kwargs["output_dir"]) / "performance"
        perf_dir.mkdir(parents=True, exist_ok=True)
        Path(perf_dir, "performance.csv").write_text("ok", encoding="utf-8")

    def evict_runner(**kwargs):
        called["evictions"] = kwargs
        evict_dir = Path(kwargs["output_dir"]) / "evictions"
        evict_dir.mkdir(parents=True, exist_ok=True)
        Path(evict_dir, "evictions.yaml").write_text("ok", encoding="utf-8")

    report = suite.run_benchmark_suite(
        artifacts_dir=tmp_path.as_posix(),
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        priority="high",
        performance_options=_performance_options(),
        eviction_options=_eviction_options(),
        performance_runner=perf_runner,
        eviction_runner=evict_runner,
    )

    assert Path(report["performance_output"]).exists()
    assert Path(report["evictions_output"]).exists()
    assert report["performance_output"].endswith("/performance/performance.csv")
    assert report["evictions_output"].endswith("/evictions/evictions.yaml")
    assert "kr benchmark performance" in report["commands"][0]
    assert "kr benchmark evictions" in report["commands"][1]
    assert "kr lifecycle" not in "\n".join(report["commands"])
    assert called["performance"] is not None
    assert called["evictions"] is not None
    assert called["performance"]["output_dir"] == tmp_path.as_posix()
    assert called["evictions"]["output_dir"] == tmp_path.as_posix()
    assert called["performance"]["duration"] == 7
    assert called["performance"]["wait"] == 3
    assert called["evictions"]["jobs"] == 8
    assert called["evictions"]["duration"] == 7


def test_run_benchmark_suite_fails_fast_when_scenario_apply_reports_errors(tmp_path: Path) -> None:
    called = {"performance": 0, "evictions": 0}

    def perf_runner(**kwargs):
        called["performance"] += 1

    def evict_runner(**kwargs):
        called["evictions"] += 1

    report = suite.run_benchmark_suite(
        artifacts_dir=tmp_path.as_posix(),
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        priority="high",
        performance_options=_performance_options(),
        eviction_options=_eviction_options(),
        scenario_apply_fn=lambda **kwargs: {
            "scenario": "unknown",
            "applied": False,
            "queue_before": "",
            "queue_after": "",
            "errors": ["unsupported scenario"],
        },
        performance_runner=perf_runner,
        eviction_runner=evict_runner,
    )

    assert report["ok"] is False
    assert report["errors"] == ["unsupported scenario"]
    assert called["performance"] == 0
    assert called["evictions"] == 0
