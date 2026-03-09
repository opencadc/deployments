import inspect
from pathlib import Path

from typer.models import OptionInfo

from kueuer.benchmarks import benchmark, plot


def _option_default(fn, name: str):
    default = inspect.signature(fn).parameters[name].default
    if isinstance(default, OptionInfo):
        return default.default
    return default


def test_benchmark_command_defaults_use_artifacts_paths() -> None:
    performance_output = _option_default(benchmark.performance, "output_dir")
    evictions_output = _option_default(benchmark.eviction, "output_dir")
    performance_run_id = _option_default(benchmark.performance, "run_id")
    evictions_run_id = _option_default(benchmark.eviction, "run_id")

    assert performance_output == "artifacts"
    assert evictions_output == "artifacts"
    assert performance_run_id == ""
    assert evictions_run_id == ""


def test_plot_command_derives_output_directory_from_input_path() -> None:
    assert "output_dir" not in inspect.signature(plot.performance).parameters
    assert "output_dir" not in inspect.signature(plot.evictions).parameters
    assert "output_dir" not in inspect.signature(plot.observations).parameters


def test_plot_observations_writes_into_run_plot_directory(
    tmp_path: Path, monkeypatch
) -> None:
    run_root = tmp_path / "artifacts" / "20260307-001222"
    observe_dir = run_root / "observe"
    observe_dir.mkdir(parents=True, exist_ok=True)
    timeseries = observe_dir / "timeseries.csv"
    timeseries.write_text("timestamp,source,available,metric,value,labels_json\n", encoding="utf-8")

    captured = {}

    def fake_plotter(timeseries_csv: str, output_dir: str, show: bool):
        captured["timeseries_csv"] = timeseries_csv
        captured["output_dir"] = output_dir
        captured["show"] = show
        return {"observation_overview_plot": str(Path(output_dir) / "observation_overview.png")}

    monkeypatch.setattr(plot.observe_plot, "observations", fake_plotter)

    plot.observations(timeseries.as_posix(), show=False)

    assert captured["timeseries_csv"] == timeseries.as_posix()
    assert captured["output_dir"] == (run_root / "plots" / "observe").as_posix()
    assert captured["show"] is False
