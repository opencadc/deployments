import matplotlib
import pandas as pd

matplotlib.use("Agg")

from kueuer.benchmarks import plot as plot_module


def test_compute_latency_adds_turnaround_columns() -> None:
    df = pd.DataFrame(
        {
            "first_creation_time": [pd.Timestamp("2026-03-05T00:00:00Z")],
            "first_completion_time": [pd.Timestamp("2026-03-05T00:00:03Z")],
            "last_creation_time": [pd.Timestamp("2026-03-05T00:00:01Z")],
            "last_completion_time": [pd.Timestamp("2026-03-05T00:00:06Z")],
        }
    )

    out = plot_module.compute_latency(df)
    assert out["first_job_turnaround_s"].iloc[0] == 3.0
    assert out["tail_job_turnaround_s"].iloc[0] == 5.0
    assert out["run_makespan_s"].iloc[0] == 6.0
    assert out["startup_latency"].iloc[0] == 3.0
    assert out["completion_latency"].iloc[0] == 5.0


def test_compute_completion_ratio_defaults_to_one_without_tracking_columns() -> None:
    df = pd.DataFrame(
        {
            "job_count": [2, 4],
            "use_kueue": [False, True],
        }
    )

    out = plot_module.compute_completion_ratio(df)
    assert out["completion_ratio"].tolist() == [1.0, 1.0]


def test_performance_command_writes_plot_files(tmp_path, monkeypatch) -> None:
    csv_path = tmp_path / "results.csv"
    pd.DataFrame(
        {
            "timestamp": ["2026-03-05T00:00:00Z", "2026-03-05T00:00:00Z"],
            "first_creation_time": ["2026-03-05T00:00:00Z", "2026-03-05T00:00:00Z"],
            "last_creation_time": ["2026-03-05T00:00:01Z", "2026-03-05T00:00:01Z"],
            "first_completion_time": ["2026-03-05T00:00:03Z", "2026-03-05T00:00:03Z"],
            "last_completion_time": ["2026-03-05T00:00:06Z", "2026-03-05T00:00:06Z"],
            "job_count": [2, 2],
            "use_kueue": [False, True],
            "total_execution_time": [6.0, 5.0],
            "avg_time_from_creation_completion": [3.0, 2.5],
            "median_time_from_creation_completion": [3.0, 2.5],
            "std_dev_time_from_creation_completion": [0.2, 0.3],
            "job_duration": [1, 1],
        }
    ).to_csv(csv_path, index=False)

    monkeypatch.setattr(plot_module.plt, "show", lambda: (_ for _ in ()).throw(AssertionError("show should not be called")))
    plot_module.performance(csv_path.as_posix(), output_dir=tmp_path.as_posix(), show=False)

    expected = [
        "performance_overview.png",
        "throughput_by_job_count.png",
        "completion_ratio_by_job_count.png",
        "tail_turnaround_by_job_count.png",
        "turnaround_overhead_by_job_count.png",
    ]
    for name in expected:
        assert (tmp_path / name).exists()


def test_evictions_command_writes_plot_files(tmp_path, monkeypatch) -> None:
    yaml_path = tmp_path / "evictions.yaml"
    yaml_path.write_text(
        """
job-a:
  name: job-a
  priority: 10000
  admitted_at: "2026-03-05T00:00:00Z"
  finished_at: "2026-03-05T00:00:05Z"
  requeues: 0
  preemptors:
    - ["job-c", "2026-03-05T00:00:02Z"]
job-b:
  name: job-b
  priority: 100000
  admitted_at: "2026-03-05T00:00:00Z"
  finished_at: "2026-03-05T00:00:04Z"
  requeues: 1
  preemptors: []
job-c:
  name: job-c
  priority: 1000000
  admitted_at: "2026-03-05T00:00:01Z"
  finished_at: "2026-03-05T00:00:03Z"
  requeues: 0
  preemptors: []
        """.strip()
    )

    monkeypatch.setattr(plot_module.plt, "show", lambda: (_ for _ in ()).throw(AssertionError("show should not be called")))
    plot_module.evictions(yaml_path.as_posix(), output_dir=tmp_path.as_posix(), show=False)

    expected = [
        "eviction_pressure_by_priority.png",
        "workload_runtime_timeline.png",
        "eviction_heatmap.png",
    ]
    for name in expected:
        assert (tmp_path / name).exists()


def test_compute_scheduling_overhead_prefers_average_turnaround() -> None:
    df = pd.DataFrame(
        {
            "avg_time_from_creation_completion": [9.0],
            "job_duration": [5.0],
            "first_creation_time": [pd.Timestamp("2026-03-05T00:00:00Z")],
            "first_completion_time": [pd.Timestamp("2026-03-05T00:00:20Z")],
        }
    )
    out = plot_module.compute_scheduling_overhead(df)
    assert out["turnaround_overhead_s"].iloc[0] == 4.0
