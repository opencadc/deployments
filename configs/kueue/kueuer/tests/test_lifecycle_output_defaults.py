import inspect
from pathlib import Path

from typer.models import OptionInfo

from kueuer.lifecycle import commands


def _option_default(fn, name: str):
    default = inspect.signature(fn).parameters[name].default
    if isinstance(default, OptionInfo):
        return default.default
    return default


def test_top_level_lifecycle_callables_default_artifacts_dir() -> None:
    assert _option_default(commands.preflight, "artifacts_dir") == "artifacts"
    assert _option_default(commands.teardown, "artifacts_dir") == "artifacts"


def test_manifest_path_prefers_canonical_name(tmp_path: Path) -> None:
    path = commands._manifest_path(tmp_path.as_posix(), "run-a")
    assert path == tmp_path / "run-a" / "manifest.json"


def test_manifest_path_falls_back_to_legacy_name(tmp_path: Path) -> None:
    legacy = tmp_path / "run-a" / "run_manifest.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("{}\n", encoding="utf-8")

    path = commands._manifest_path(tmp_path.as_posix(), "run-a")
    assert path == legacy


def test_resolve_suite_path_uses_legacy_suite_filenames_when_needed(tmp_path: Path) -> None:
    run_root = tmp_path / "run-a"
    suite_dir = run_root / "suite"
    suite_dir.mkdir(parents=True, exist_ok=True)
    legacy_perf = suite_dir / "performance_results.csv"
    legacy_perf.write_text("job_count,use_kueue\n2,False\n", encoding="utf-8")

    path = commands._resolve_suite_path(
        run_root,
        "performance",
        "performance.csv",
        "performance_results.csv",
    )

    assert path == legacy_perf


def test_resolve_suite_path_prefers_canonical_domain_directories(tmp_path: Path) -> None:
    run_root = tmp_path / "run-a"
    perf_dir = run_root / "performance"
    perf_dir.mkdir(parents=True, exist_ok=True)
    performance = perf_dir / "performance.csv"
    performance.write_text("job_count,use_kueue\n2,False\n", encoding="utf-8")

    path = commands._resolve_suite_path(
        run_root,
        "performance",
        "performance.csv",
        "performance_results.csv",
    )

    assert path == performance
