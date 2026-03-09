import inspect
from pathlib import Path

from kueuer.observe import commands
from kueuer.utils.constants import DEFAULT_OBSERVATION_INTERVAL_SECONDS


def test_collect_observations_defaults_use_observation_interval_constant() -> None:
    interval = inspect.signature(commands.collect_observations).parameters[
        "interval_seconds"
    ].default
    duration = inspect.signature(commands.collect_observations).parameters[
        "duration_seconds"
    ].default

    assert interval == DEFAULT_OBSERVATION_INTERVAL_SECONDS
    assert duration == 0.0


def test_analyze_observations_writes_report_into_observe_directory(tmp_path: Path) -> None:
    observe_dir = tmp_path / "observe"
    observe_dir.mkdir(parents=True, exist_ok=True)
    (observe_dir / "timeseries.csv").write_text(
        "timestamp,source,available,metric,value,labels_json\n"
        "2026-03-05T00:00:00Z,queues,true,pending_workloads,3,{}\n",
        encoding="utf-8",
    )

    report = commands.analyze_observations(observe_dir=observe_dir.as_posix())

    assert report["report_json"] == (observe_dir / "report.json").as_posix()
    assert Path(report["report_json"]).exists()


def test_render_observation_report_reuses_existing_report(tmp_path: Path, monkeypatch) -> None:
    observe_dir = tmp_path / "observe"
    observe_dir.mkdir(parents=True, exist_ok=True)
    report_path = observe_dir / "report.json"
    report_path.write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(
        commands,
        "analyze_observations",
        lambda observe_dir: (_ for _ in ()).throw(AssertionError("should not analyze")),
    )

    assert commands.render_observation_report(observe_dir.as_posix()) == report_path.as_posix()


def test_render_observation_plots_uses_timeseries_in_observe_dir(
    tmp_path: Path, monkeypatch
) -> None:
    observe_dir = tmp_path / "observe"
    observe_dir.mkdir(parents=True, exist_ok=True)
    output_dir = tmp_path / "plots" / "observe"
    captured = {}

    def fake_plotter(timeseries_csv: str, output_dir: str, show: bool):
        captured["timeseries_csv"] = timeseries_csv
        captured["output_dir"] = output_dir
        captured["show"] = show
        return {"plot": str(Path(output_dir) / "queue_depth.png")}

    monkeypatch.setattr(commands.observe_plot, "observations", fake_plotter)

    report = commands.render_observation_plots(
        observe_dir=observe_dir.as_posix(),
        output_dir=output_dir.as_posix(),
        show=False,
    )

    assert report["plot"] == str(output_dir / "queue_depth.png")
    assert captured["timeseries_csv"] == (observe_dir / "timeseries.csv").as_posix()
    assert captured["output_dir"] == output_dir.as_posix()
    assert captured["show"] is False
