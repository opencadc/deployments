import pytest
import typer

from kueuer.lifecycle import commands


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


def test_e2e_exits_when_run_suite_reports_failure(
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

    with pytest.raises(typer.Exit) as excinfo:
        commands.e2e(
            artifacts_dir=tmp_path.as_posix(),
            run_id="run-a",
            skip_teardown=True,
        )

    assert excinfo.value.exit_code == 1
    assert calls["collect"] == 0
