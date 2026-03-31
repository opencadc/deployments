import pytest
from typer.testing import CliRunner

from kueuer.cli import app
from kueuer.lifecycle import commands

runner = CliRunner()


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


def test_execute_e2e_pipeline_runs_steps_in_order() -> None:
    called = []

    def _step(name: str, ok: bool = True):
        def _inner():
            called.append(name)
            return {"ok": ok, "name": name}

        return _inner

    report = commands.execute_e2e_pipeline(
        preflight_fn=_step("preflight"),
        validate_kueue_fn=_step("validate-kueue"),
        ensure_queues_fn=_step("ensure-queues"),
        run_suite_fn=_step("run-suite"),
        collect_fn=_step("collect"),
        teardown_fn=_step("teardown"),
    )
    assert report["ok"] is True
    assert called == [
        "preflight",
        "validate-kueue",
        "ensure-queues",
        "run-suite",
        "collect",
        "teardown",
    ]


def test_execute_e2e_pipeline_short_circuits_on_failure() -> None:
    called = []

    def _step(name: str, ok: bool = True):
        def _inner():
            called.append(name)
            return {"ok": ok, "name": name}

        return _inner

    report = commands.execute_e2e_pipeline(
        preflight_fn=_step("preflight", ok=False),
        validate_kueue_fn=_step("validate-kueue"),
        ensure_queues_fn=_step("ensure-queues"),
        run_suite_fn=_step("run-suite"),
        collect_fn=_step("collect"),
        teardown_fn=_step("teardown"),
    )
    assert report["ok"] is False
    assert report["failed_step"] == "preflight"
    assert called == ["preflight"]


def test_run_benchmark_e2e_returns_failure_when_suite_reports_failure(
    tmp_path, monkeypatch
) -> None:
    calls = {"collect": 0}

    monkeypatch.setattr(commands, "run_preflight", lambda namespace: {"ok": True})
    monkeypatch.setattr(commands, "validate_kueue_health", lambda: {"ok": True})
    monkeypatch.setattr(commands, "ensure_queues_state", lambda **kwargs: {"ok": True})
    monkeypatch.setattr(
        commands,
        "run_benchmark_suite",
        lambda **kwargs: {"ok": False, "errors": ["suite failed"]},
    )

    def fake_collect_outputs(**kwargs):
        calls["collect"] += 1
        return {"ok": True}

    monkeypatch.setattr(commands, "collect_outputs", fake_collect_outputs)
    monkeypatch.setattr(
        commands,
        "cleanup_benchmark_jobs",
        lambda namespace, prefixes: {"ok": True},
    )

    report = commands.run_benchmark_e2e(
        artifacts_dir=tmp_path.as_posix(),
        run_id="run-a",
        namespace="skaha-workload",
        localqueue="skaha-local-queue",
        clusterqueue="skaha-cluster-queue",
        priority="high",
        scenario="control",
        performance_options=_performance_options(),
        eviction_options=_eviction_options(),
        skip_teardown=True,
    )

    assert report["ok"] is False
    assert report["failed_step"] == "run-suite"
    assert calls["collect"] == 0


def test_public_benchmark_e2e_passes_resolved_shared_and_eviction_overrides(
    tmp_path, monkeypatch
) -> None:
    captured = {}

    def fake_run_benchmark_e2e(**kwargs):
        captured.update(kwargs)
        return {
            "ok": True,
            "run_id": "run-a",
            "run_root": (tmp_path / "run-a").as_posix(),
            "performance_csv": (tmp_path / "run-a" / "performance.csv").as_posix(),
            "evictions_yaml": (tmp_path / "run-a" / "evictions.yaml").as_posix(),
        }

    monkeypatch.setattr(commands, "run_benchmark_e2e", fake_run_benchmark_e2e)

    result = runner.invoke(
        app,
        [
            "benchmark",
            "e2e",
            "--output-dir",
            tmp_path.as_posix(),
            "--run-id",
            "run-a",
            "--profile",
            "local-safe",
            "--counts",
            "4,2,4",
            "--duration",
            "30",
            "--cores",
            "0.4",
            "--ram",
            "1.5",
            "--storage",
            "3.0",
            "--eviction-jobs",
            "12",
            "--eviction-ram",
            "10.0",
            "--no-observe",
        ],
    )

    assert result.exit_code == 0
    assert captured["observe"] is False
    assert captured["performance_options"] == {
        "profile": "local-safe",
        "counts_csv": "2,4",
        "duration": 30,
        "cores": 0.4,
        "ram": 1.5,
        "storage": 3.0,
        "wait": 5,
    }
    assert captured["eviction_options"] == {
        "profile": "local-safe",
        "jobs": 12,
        "cores": 0.4,
        "ram": 10.0,
        "storage": 3.0,
        "duration": 30,
    }
