import inspect

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


def test_plot_command_requires_explicit_output_directory() -> None:
    perf_output_dir = _option_default(plot.performance, "output_dir")
    evict_output_dir = _option_default(plot.evictions, "output_dir")

    assert perf_output_dir is ...
    assert evict_output_dir is ...
