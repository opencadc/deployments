import inspect
from pathlib import Path

from typer.models import OptionInfo

from kueuer.lifecycle import commands


def _artifacts_default(fn):
    default = inspect.signature(fn).parameters["artifacts_dir"].default
    if isinstance(default, OptionInfo):
        return default.default
    return default


def test_lifecycle_commands_default_artifacts_dir() -> None:
    assert _artifacts_default(commands.preflight) == "artifacts"
    assert _artifacts_default(commands.validate_kueue) == "artifacts"
    assert _artifacts_default(commands.ensure_queues) == "artifacts"
    assert _artifacts_default(commands.run_suite) == "artifacts"
    assert _artifacts_default(commands.collect) == "artifacts"
    assert _artifacts_default(commands.teardown) == "artifacts"
    assert _artifacts_default(commands.e2e) == "artifacts"


def test_manifest_path_prefers_canonical_name(tmp_path: Path) -> None:
    path = commands._manifest_path(tmp_path.as_posix(), "run-a")
    assert path == tmp_path / "run-a" / "manifest.json"


def test_manifest_path_falls_back_to_legacy_name(tmp_path: Path) -> None:
    legacy = tmp_path / "run-a" / "run_manifest.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("{}\n", encoding="utf-8")

    path = commands._manifest_path(tmp_path.as_posix(), "run-a")
    assert path == legacy


def test_collect_uses_legacy_performance_filename_when_needed(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "run-a"
    suite_dir = run_root / "suite"
    suite_dir.mkdir(parents=True, exist_ok=True)
    legacy_perf = suite_dir / "performance_results.csv"
    legacy_perf.write_text("job_count,use_kueue\n2,False\n", encoding="utf-8")
    evictions = suite_dir / "evictions.yaml"
    evictions.write_text("{}\n", encoding="utf-8")

    captured = {}

    def fake_collect_outputs(**kwargs):
        captured.update(kwargs)
        return {}

    monkeypatch.setattr(commands, "collect_outputs", fake_collect_outputs)

    commands.collect(
        artifacts_dir=tmp_path.as_posix(),
        run_id="run-a",
        performance_csv="",
        evictions_yaml="",
    )

    assert captured["performance_csv"] == legacy_perf.as_posix()
    assert captured["evictions_yaml"] == evictions.as_posix()
    assert (run_root / "manifest.json").exists()
