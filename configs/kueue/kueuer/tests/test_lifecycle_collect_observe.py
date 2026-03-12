from pathlib import Path

from kueuer.lifecycle import collect


def test_collect_outputs_includes_observe_artifacts_when_present(tmp_path: Path) -> None:
    perf_csv = tmp_path / "perf.csv"
    perf_csv.write_text(
        (
            "timestamp,first_creation_time,last_creation_time,first_completion_time,last_completion_time,"
            "job_count,use_kueue,total_execution_time,avg_time_from_creation_completion,"
            "median_time_from_creation_completion,std_dev_time_from_creation_completion,job_duration\n"
            "2026-03-05T00:00:00Z,2026-03-05T00:00:00Z,2026-03-05T00:00:01Z,2026-03-05T00:00:03Z,2026-03-05T00:00:06Z,2,False,6,3,3,0.2,1\n"
            "2026-03-05T00:00:00Z,2026-03-05T00:00:00Z,2026-03-05T00:00:01Z,2026-03-05T00:00:03Z,2026-03-05T00:00:06Z,2,True,5,2.5,2.5,0.3,1\n"
        ),
        encoding="utf-8",
    )
    evict_yaml = tmp_path / "evict.yaml"
    evict_yaml.write_text("job-a: {name: job-a, priority: 10000, requeues: 0, preemptors: []}\n", encoding="utf-8")

    output_dir = tmp_path / "out"
    observe_dir = output_dir / "observe"
    observe_dir.mkdir(parents=True, exist_ok=True)
    (observe_dir / "timeseries.csv").write_text(
        "timestamp,source,available,metric,value,labels_json\n"
        "2026-03-05T00:00:00Z,queues,true,pending_workloads,3,{}\n",
        encoding="utf-8",
    )

    def perf_plotter(filepath: str, output_dir: str, show: bool):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir, "perf.png").write_text(filepath, encoding="utf-8")
        return None

    def evict_plotter(filepath: str, output_dir: str, show: bool):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir, "evict.png").write_text(filepath, encoding="utf-8")
        return None

    def observe_plotter(timeseries_csv: str, output_dir: str, show: bool):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        marker = Path(output_dir, "queue_depth.png")
        marker.write_text(timeseries_csv, encoding="utf-8")
        return {"queue_depth_plot": marker.as_posix()}

    def observe_analyzer(observe_dir: str, baseline_summary_path: str = ""):
        del baseline_summary_path
        report = Path(observe_dir, "report.json")
        report.write_text("{}", encoding="utf-8")
        return {"report_json": report.as_posix()}

    report = collect.collect_outputs(
        performance_csv=perf_csv.as_posix(),
        evictions_yaml=evict_yaml.as_posix(),
        output_dir=output_dir.as_posix(),
        performance_plotter=perf_plotter,
        evictions_plotter=evict_plotter,
        observe_plotter=observe_plotter,
        observe_analyzer=observe_analyzer,
    )

    assert "observe_plot_dir" in report
    assert Path(report["observe_plot_dir"]).exists()
    assert Path(report["observe_report_json"]).exists()
    assert Path(report["report_json"]).exists()
