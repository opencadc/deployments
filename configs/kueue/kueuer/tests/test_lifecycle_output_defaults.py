import inspect
from pathlib import Path

from typer.models import OptionInfo
from typer.testing import CliRunner

from kueuer.cli import app
from kueuer.lifecycle import commands

runner = CliRunner()


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


def test_collect_uses_legacy_suite_filenames_when_needed(tmp_path: Path, monkeypatch) -> None:
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


def test_collect_prefers_canonical_domain_directories(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "run-a"
    perf_dir = run_root / "performance"
    evict_dir = run_root / "evictions"
    perf_dir.mkdir(parents=True, exist_ok=True)
    evict_dir.mkdir(parents=True, exist_ok=True)
    performance = perf_dir / "performance.csv"
    evictions = evict_dir / "evictions.yaml"
    performance.write_text("job_count,use_kueue\n2,False\n", encoding="utf-8")
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

    assert captured["performance_csv"] == performance.as_posix()
    assert captured["evictions_yaml"] == evictions.as_posix()


def test_e2e_observe_defaults_to_true() -> None:
    default = inspect.signature(commands.e2e).parameters["observe"].default
    if isinstance(default, OptionInfo):
        default = default.default
    assert default is True


def test_collect_prints_plot_and_report_locations(tmp_path: Path, monkeypatch) -> None:
    run_root = tmp_path / "run-a"
    perf_dir = run_root / "performance"
    evict_dir = run_root / "evictions"
    perf_dir.mkdir(parents=True, exist_ok=True)
    evict_dir.mkdir(parents=True, exist_ok=True)
    (perf_dir / "performance.csv").write_text("job_count,use_kueue\n2,False\n", encoding="utf-8")
    (evict_dir / "evictions.yaml").write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(
        commands,
        "collect_outputs",
        lambda **kwargs: {
            "ok": True,
            "performance_plot_dir": (run_root / "plots" / "performance").as_posix(),
            "evictions_plot_dir": (run_root / "plots" / "evictions").as_posix(),
            "observe_plot_dir": (run_root / "plots" / "observe").as_posix(),
            "observe_report_json": (run_root / "observe" / "report.json").as_posix(),
            "report_md": (run_root / "report.md").as_posix(),
        },
    )

    result = runner.invoke(
        app,
        [
            "lifecycle",
            "collect",
            "--artifacts-dir",
            tmp_path.as_posix(),
            "--run-id",
            "run-a",
        ],
    )

    assert result.exit_code == 0
    assert "Performance plots:" in result.stdout
    assert "Eviction plots:" in result.stdout
    assert "Observation plots:" in result.stdout
    assert "Observation report:" in result.stdout
    assert "Run report:" in result.stdout
    assert "uv run kr plot performance" in result.stdout
    assert "uv run kr plot evictions" in result.stdout
