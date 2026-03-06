from pathlib import Path

from kueuer.lifecycle import collect


def test_collect_outputs_generates_comparison_files(tmp_path: Path) -> None:
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

    def perf_plotter(filepath: str, output_dir: str, show: bool):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir, "perf.png").write_text(filepath, encoding="utf-8")
        return None

    def evict_plotter(filepath: str, output_dir: str, show: bool):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir, "evict.png").write_text(filepath, encoding="utf-8")
        return None

    report = collect.collect_outputs(
        performance_csv=perf_csv.as_posix(),
        evictions_yaml=evict_yaml.as_posix(),
        output_dir=(tmp_path / "out").as_posix(),
        performance_plotter=perf_plotter,
        evictions_plotter=evict_plotter,
    )

    assert Path(report["performance_plot_dir"], "perf.png").exists()
    assert Path(report["evictions_plot_dir"], "evict.png").exists()
    assert Path(report["comparison_summary"]).exists()
    assert Path(report["comparison_report"]).exists()
    assert report["comparison_summary"].endswith("/comparison/summary.json")
    assert report["comparison_report"].endswith("/comparison/report.md")
