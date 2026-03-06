import inspect
from pathlib import Path

from typer.models import OptionInfo
from typer.testing import CliRunner

from kueuer.benchmarks import benchmark, plot
from kueuer.cli import app


runner = CliRunner()


def _option_default(fn, name: str):
    default = inspect.signature(fn).parameters[name].default
    if isinstance(default, OptionInfo):
        return default.default
    return default


def test_benchmark_command_defaults_expose_local_safe_values() -> None:
    assert _option_default(benchmark.performance, "duration") == 5
    assert _option_default(benchmark.performance, "cores") == 0.1
    assert _option_default(benchmark.performance, "ram") == 0.25
    assert _option_default(benchmark.performance, "storage") == 0.25
    assert _option_default(benchmark.performance, "wait") == 5
    assert _option_default(benchmark.eviction, "jobs") == 8
    assert _option_default(benchmark.eviction, "cores") == 2.0
    assert _option_default(benchmark.eviction, "ram") == 2.0
    assert _option_default(benchmark.eviction, "storage") == 2.0
    assert _option_default(benchmark.eviction, "duration") == 60


def test_benchmark_command_defaults_use_artifacts_dir_and_blank_run_id() -> None:
    assert _option_default(benchmark.performance, "output_dir") == "artifacts"
    assert _option_default(benchmark.performance, "run_id") == ""
    assert _option_default(benchmark.eviction, "output_dir") == "artifacts"
    assert _option_default(benchmark.eviction, "run_id") == ""


def test_plot_performance_requires_output_dir(tmp_path: Path) -> None:
    csv_path = tmp_path / "results.csv"
    csv_path.write_text("timestamp,first_creation_time,last_creation_time,first_completion_time,last_completion_time,job_count,use_kueue,total_execution_time,avg_time_from_creation_completion,median_time_from_creation_completion,std_dev_time_from_creation_completion,job_duration\n", encoding="utf-8")

    result = runner.invoke(app, ["plot", "performance", csv_path.as_posix()])

    assert result.exit_code != 0
    assert "--output-dir" in result.stdout


def test_benchmark_performance_uses_run_scoped_default_output_and_prints_plot_command(
    monkeypatch,
) -> None:
    captured = {}

    monkeypatch.setattr(benchmark, "_default_run_id", lambda: "20260306-153000")
    monkeypatch.setattr(benchmark.k8s, "check", lambda namespace, kueue, priority: True)

    def fake_benchmark(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(benchmark, "benchmark", fake_benchmark)

    result = runner.invoke(
        app,
        [
            "benchmark",
            "performance",
            "--counts",
            "2,4",
        ],
    )

    assert result.exit_code == 0
    assert captured["resultsfile"].endswith("artifacts/20260306-153000/performance.csv")
    assert (
        "uv run kr plot performance artifacts/20260306-153000/performance.csv --output-dir artifacts/20260306-153000/plots/performance --show"
        in result.stdout
    )


def test_plot_module_has_no_default_output_dir() -> None:
    assert _option_default(plot.performance, "output_dir") is ...
    assert _option_default(plot.evictions, "output_dir") is ...
