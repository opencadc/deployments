"""Plot helpers for observation timeseries data."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

import matplotlib.pyplot as plt
from matplotlib import dates as mdates
import pandas as pd
import seaborn as sns


sns.set_theme(
    style="whitegrid",
    context="talk",
    rc={
        "axes.facecolor": "#fbfaf7",
        "figure.facecolor": "#f4f1ea",
        "grid.color": "#d9d2c6",
        "axes.edgecolor": "#cfc6b8",
    },
)

COLORS = {
    "memory": "#506d94",
    "cpu": "#d26a3d",
    "latency": "#7f5539",
    "latency_alt": "#b08968",
    "pending": "#487c6e",
    "admitted": "#9cc9b5",
    "wait": "#8a5ea7",
    "wait_alt": "#bea3d4",
    "inflight_read": "#6b8e23",
    "inflight_write": "#bc4749",
}


def _style_axis(ax: plt.Axes, title: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", pad=12, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.55)
    ax.grid(axis="x", alpha=0.10)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))


def _save(fig: plt.Figure, output_path: Path, show: bool = False) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path.as_posix(), dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    if show:
        plt.show()
    plt.close(fig)
    return output_path.as_posix()


def _empty_axis(ax: plt.Axes, message: str) -> None:
    ax.text(0.5, 0.5, message, ha="center", va="center", color="#5b5146", transform=ax.transAxes)
    ax.set_axis_off()


def _metric_subset(df: pd.DataFrame, metrics: Iterable[str]) -> pd.DataFrame:
    subset = df[df["metric"].isin(list(metrics))].copy()
    if subset.empty:
        return subset
    subset["timestamp"] = pd.to_datetime(subset["timestamp"], errors="coerce")
    subset = subset.dropna(subset=["timestamp"]).sort_values("timestamp")
    subset["value"] = pd.to_numeric(subset["value"], errors="coerce")
    return subset.dropna(subset=["value"])


def _plot_series(ax: plt.Axes, subset: pd.DataFrame, metric: str, label: str, color: str) -> None:
    series = subset[subset["metric"] == metric]
    if series.empty:
        return
    ax.plot(
        series["timestamp"],
        series["value"],
        color=color,
        linewidth=2.5,
        marker="o",
        markersize=4,
        label=label,
    )


def _render_controller_resources(df: pd.DataFrame, output_path: Path, show: bool) -> str:
    subset = _metric_subset(
        df,
        [
            "kueue_controller_memory_working_set_bytes",
            "kueue_controller_cpu_cores",
        ],
    )
    fig, axes = plt.subplots(2, 1, figsize=(12, 7.4), sharex=True)
    memory = subset[subset["metric"] == "kueue_controller_memory_working_set_bytes"].copy()
    if not memory.empty:
        memory["value"] = memory["value"] / float(1024**3)
        axes[0].plot(
            memory["timestamp"],
            memory["value"],
            color=COLORS["memory"],
            linewidth=2.7,
            marker="o",
            markersize=4,
        )
        axes[0].axhline(2.0, color="#b83232", linestyle="--", linewidth=1.4, alpha=0.8)
        _style_axis(axes[0], "Controller memory working set", "GiB")
    else:
        _empty_axis(axes[0], "No controller memory samples")

    cpu = subset[subset["metric"] == "kueue_controller_cpu_cores"]
    if not cpu.empty:
        axes[1].plot(
            cpu["timestamp"],
            cpu["value"],
            color=COLORS["cpu"],
            linewidth=2.7,
            marker="o",
            markersize=4,
        )
        _style_axis(axes[1], "Controller CPU usage", "Cores")
        axes[1].set_xlabel("Observation time")
    else:
        _empty_axis(axes[1], "No controller CPU samples")

    fig.suptitle(
        "Kueue controller resource profile",
        x=0.06,
        y=1.01,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    return _save(fig, output_path, show=show)


def _render_apiserver_pressure(df: pd.DataFrame, output_path: Path, show: bool) -> str:
    subset = _metric_subset(
        df,
        [
            "apiserver_non_watch_request_p95_seconds",
            "apiserver_non_watch_request_p99_seconds",
            "apiserver_current_inflight_read_requests",
            "apiserver_current_inflight_write_requests",
        ],
    )
    fig, axes = plt.subplots(2, 1, figsize=(12, 7.4), sharex=True)

    latency = subset[
        subset["metric"].isin(
            [
                "apiserver_non_watch_request_p95_seconds",
                "apiserver_non_watch_request_p99_seconds",
            ]
        )
    ].copy()
    if not latency.empty:
        latency["value"] = latency["value"] * 1000.0
        _plot_series(
            axes[0],
            latency.replace(
                {
                    "metric": {
                        "apiserver_non_watch_request_p95_seconds": "p95_ms",
                        "apiserver_non_watch_request_p99_seconds": "p99_ms",
                    }
                }
            ),
            "p95_ms",
            "Non-watch p95",
            COLORS["latency"],
        )
        _plot_series(
            axes[0],
            latency.replace(
                {
                    "metric": {
                        "apiserver_non_watch_request_p95_seconds": "p95_ms",
                        "apiserver_non_watch_request_p99_seconds": "p99_ms",
                    }
                }
            ),
            "p99_ms",
            "Non-watch p99",
            COLORS["latency_alt"],
        )
        _style_axis(axes[0], "API server request latency", "Milliseconds")
        axes[0].legend(frameon=False, loc="best")
    else:
        _empty_axis(axes[0], "No API server latency samples")

    inflight = subset[
        subset["metric"].isin(
            [
                "apiserver_current_inflight_read_requests",
                "apiserver_current_inflight_write_requests",
            ]
        )
    ]
    if not inflight.empty:
        _plot_series(
            axes[1],
            inflight,
            "apiserver_current_inflight_read_requests",
            "Read inflight",
            COLORS["inflight_read"],
        )
        _plot_series(
            axes[1],
            inflight,
            "apiserver_current_inflight_write_requests",
            "Write inflight",
            COLORS["inflight_write"],
        )
        _style_axis(axes[1], "API server inflight request pressure", "Concurrent requests")
        axes[1].set_xlabel("Observation time")
        axes[1].legend(frameon=False, loc="best")
    else:
        _empty_axis(axes[1], "No inflight request samples")

    fig.suptitle(
        "Kubernetes API server pressure",
        x=0.06,
        y=1.01,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    return _save(fig, output_path, show=show)


def _render_queue_pressure(df: pd.DataFrame, output_path: Path, show: bool) -> str:
    subset = _metric_subset(
        df,
        [
            "pending_workloads",
            "admitted_workloads",
            "workload_queue_wait_p50_seconds",
            "workload_queue_wait_p95_seconds",
        ],
    )
    fig, axes = plt.subplots(2, 1, figsize=(12, 7.4), sharex=True)

    queue_depth = subset[
        subset["metric"].isin(["pending_workloads", "admitted_workloads"])
    ]
    if not queue_depth.empty:
        _plot_series(
            axes[0],
            queue_depth,
            "pending_workloads",
            "Pending workloads",
            COLORS["pending"],
        )
        _plot_series(
            axes[0],
            queue_depth,
            "admitted_workloads",
            "Admitted workloads",
            COLORS["admitted"],
        )
        _style_axis(axes[0], "Queue depth over time", "Workloads")
        axes[0].legend(frameon=False, loc="best")
    else:
        _empty_axis(axes[0], "No queue depth samples")

    waits = subset[
        subset["metric"].isin(
            ["workload_queue_wait_p50_seconds", "workload_queue_wait_p95_seconds"]
        )
    ]
    if not waits.empty:
        _plot_series(
            axes[1],
            waits,
            "workload_queue_wait_p50_seconds",
            "Queue wait p50",
            COLORS["wait_alt"],
        )
        _plot_series(
            axes[1],
            waits,
            "workload_queue_wait_p95_seconds",
            "Queue wait p95",
            COLORS["wait"],
        )
        _style_axis(axes[1], "Admission wait time", "Seconds")
        axes[1].set_xlabel("Observation time")
        axes[1].legend(frameon=False, loc="best")
    else:
        _empty_axis(axes[1], "No queue wait samples")

    fig.suptitle(
        "Queue pressure and admission wait",
        x=0.06,
        y=1.01,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    return _save(fig, output_path, show=show)


def _render_observation_overview(df: pd.DataFrame, output_path: Path, show: bool) -> str:
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)
    configs = [
        (
            "kueue_controller_memory_working_set_bytes",
            "Controller memory",
            "GiB",
            COLORS["memory"],
            lambda values: values / float(1024**3),
        ),
        (
            "kueue_controller_cpu_cores",
            "Controller CPU",
            "Cores",
            COLORS["cpu"],
            lambda values: values,
        ),
        (
            "apiserver_non_watch_request_p95_seconds",
            "API server non-watch p95",
            "Milliseconds",
            COLORS["latency"],
            lambda values: values * 1000.0,
        ),
        (
            "pending_workloads",
            "Pending workloads",
            "Workloads",
            COLORS["pending"],
            lambda values: values,
        ),
    ]

    for ax, (metric, title, ylabel, color, transform) in zip(axes.flat, configs):
        subset = _metric_subset(df, [metric])
        if subset.empty:
            _empty_axis(ax, f"No {title.lower()} samples")
            continue
        subset["value"] = transform(subset["value"])
        ax.plot(
            subset["timestamp"],
            subset["value"],
            color=color,
            linewidth=2.5,
            marker="o",
            markersize=4,
        )
        _style_axis(ax, title, ylabel)

    fig.suptitle(
        "Observation overview",
        x=0.06,
        y=1.01,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    return _save(fig, output_path, show=show)


def observations(timeseries_csv: str, output_dir: str, show: bool = False) -> Dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(timeseries_csv)

    report = {
        "observation_overview_plot": _render_observation_overview(
            df,
            out / "observation_overview.png",
            show=show,
        ),
        "controller_resource_plot": _render_controller_resources(
            df,
            out / "controller_resource_overview.png",
            show=show,
        ),
        "apiserver_pressure_plot": _render_apiserver_pressure(
            df,
            out / "apiserver_pressure.png",
            show=show,
        ),
        "queue_pressure_plot": _render_queue_pressure(
            df,
            out / "queue_pressure.png",
            show=show,
        ),
    }

    return report
