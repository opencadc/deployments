from pathlib import Path

from kueuer.observe import plot


def test_observations_plot_writes_expected_files(tmp_path: Path) -> None:
    timeseries = tmp_path / "timeseries.csv"
    timeseries.write_text(
        "timestamp,source,available,metric,value,labels_json\n"
        "2026-03-05T00:00:00Z,kueue-controller,true,kueue_controller_memory_working_set_bytes,100,{}\n"
        "2026-03-05T00:00:05Z,kueue-controller,true,kueue_controller_memory_working_set_bytes,120,{}\n"
        "2026-03-05T00:00:00Z,kueue-controller,true,kueue_controller_cpu_cores,0.2,{}\n"
        "2026-03-05T00:00:05Z,kueue-controller,true,kueue_controller_cpu_cores,0.3,{}\n"
        "2026-03-05T00:00:00Z,apiserver,true,apiserver_non_watch_request_p95_seconds,0.1,{}\n"
        "2026-03-05T00:00:05Z,apiserver,true,apiserver_non_watch_request_p95_seconds,0.2,{}\n"
        "2026-03-05T00:00:00Z,queues,true,pending_workloads,5,{}\n"
        "2026-03-05T00:00:05Z,queues,true,pending_workloads,2,{}\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "plots"
    report = plot.observations(
        timeseries_csv=timeseries.as_posix(),
        output_dir=output_dir.as_posix(),
        show=False,
    )

    assert Path(report["kueue_controller_memory_plot"]).exists()
    assert Path(report["kueue_controller_cpu_plot"]).exists()
    assert Path(report["apiserver_latency_plot"]).exists()
    assert Path(report["queue_depth_plot"]).exists()
