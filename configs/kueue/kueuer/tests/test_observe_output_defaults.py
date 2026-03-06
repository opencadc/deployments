import inspect
from pathlib import Path

from typer.models import OptionInfo

from kueuer.observe import commands


def _option_default(fn, name: str):
    default = inspect.signature(fn).parameters[name].default
    if isinstance(default, OptionInfo):
        return default.default
    return default


def test_observe_command_defaults_use_artifacts_root() -> None:
    collect_artifacts = _option_default(commands.collect, "artifacts_dir")
    analyze_artifacts = _option_default(commands.analyze, "artifacts_dir")
    report_artifacts = _option_default(commands.report, "artifacts_dir")

    assert collect_artifacts == "artifacts"
    assert analyze_artifacts == "artifacts"
    assert report_artifacts == "artifacts"


def test_observe_collect_run_id_default_is_blank() -> None:
    run_id = _option_default(commands.collect, "run_id")
    assert run_id == ""


def test_latest_run_id_detects_latest_observe_directory(tmp_path: Path) -> None:
    (tmp_path / "20260305-000001" / "observe").mkdir(parents=True, exist_ok=True)
    (tmp_path / "20260305-000010" / "observe").mkdir(parents=True, exist_ok=True)

    latest = commands._latest_run_id(tmp_path)

    assert latest == "20260305-000010"


def test_analyze_without_run_id_uses_latest_run(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "20260305-000001" / "observe").mkdir(parents=True, exist_ok=True)
    (tmp_path / "20260305-000010" / "observe").mkdir(parents=True, exist_ok=True)

    captured = {}

    def fake_analyze_observations(observe_dir: str, baseline_summary_path: str = ""):
        captured["observe_dir"] = observe_dir
        captured["baseline_summary_path"] = baseline_summary_path
        return {"policy_json": str(Path(observe_dir) / "policy.json")}

    monkeypatch.setattr(commands, "analyze_observations", fake_analyze_observations)

    commands.analyze(artifacts_dir=tmp_path.as_posix(), run_id="")

    assert captured["observe_dir"].endswith("20260305-000010/observe")
