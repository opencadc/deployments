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
    assert out["startup_latency"].iloc[0] == 3.0
    assert out["completion_latency"].iloc[0] == 5.0


def test_plot_completion_times_uses_boolean_filters(monkeypatch) -> None:
    df = pd.DataFrame(
        {
            "first_creation_time": pd.to_datetime(
                ["2026-03-05T00:00:00Z", "2026-03-05T00:00:00Z"]
            ),
            "last_completion_time": pd.to_datetime(
                ["2026-03-05T00:00:04Z", "2026-03-05T00:00:05Z"]
            ),
            "job_count": [2, 2],
            "use_kueue": [False, True],
        }
    )

    calls = []

    monkeypatch.setattr(plot_module.sns, "scatterplot", lambda *a, **k: None)

    def _capture_regplot(*_args, **kwargs):
        calls.append(kwargs["data"].copy())
        return None

    monkeypatch.setattr(plot_module.sns, "regplot", _capture_regplot)
    monkeypatch.setattr(plot_module.plt, "show", lambda: None)

    plot_module.plot_completion_times(df)

    assert len(calls) == 2
    assert calls[0]["use_kueue"].eq(False).all()
    assert calls[1]["use_kueue"].eq(True).all()


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
        "throughput_comparison.png",
        "first_job_turnaround_comparison.png",
        "tail_job_turnaround_comparison.png",
        "cv_of_job_durations.png",
        "job_duration_distribution.png",
        "job_completion_times.png",
        "scaling_efficiency.png",
        "scheduling_overhead.png",
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
  preemptors: []
job-b:
  name: job-b
  priority: 100000
  admitted_at: "2026-03-05T00:00:00Z"
  finished_at: "2026-03-05T00:00:04Z"
  requeues: 1
  preemptors: []
        """.strip()
    )

    monkeypatch.setattr(plot_module.plt, "show", lambda: (_ for _ in ()).throw(AssertionError("show should not be called")))
    plot_module.evictions(yaml_path.as_posix(), output_dir=tmp_path.as_posix(), show=False)

    expected = [
        "evictions_by_priority.png",
        "job_start_end_timeline.png",
        "requeues_by_priority.png",
    ]
    for name in expected:
        assert (tmp_path / name).exists()


def test_plot_duration_distribution_handles_constant_values(tmp_path) -> None:
    df = pd.DataFrame(
        {
            "avg_time_from_creation_completion": [9.0, 9.0, 9.0, 9.0],
            "use_kueue": [False, True, False, True],
        }
    )
    plot_module.plot_duration_distribution(
        df, output_dir=tmp_path.as_posix(), show=False
    )
    assert (tmp_path / "job_duration_distribution.png").exists()
