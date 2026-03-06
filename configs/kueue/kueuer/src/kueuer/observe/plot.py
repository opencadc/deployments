"""Plot helpers for observation timeseries data."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd


METRICS = {
    "kueue_controller_memory_working_set_bytes": (
        "kueue_controller_memory.png",
        "Kueue controller memory",
    ),
    "kueue_controller_cpu_cores": (
        "kueue_controller_cpu.png",
        "Kueue controller CPU",
    ),
    "apiserver_non_watch_request_p95_seconds": (
        "apiserver_latency.png",
        "API server non-watch p95 latency",
    ),
    "pending_workloads": (
        "queue_depth.png",
        "Queue pending workloads",
    ),
}


def _render_metric_plot(df: pd.DataFrame, metric: str, output_path: Path, title: str) -> None:
    subset = df[df["metric"] == metric]
    fig, ax = plt.subplots(figsize=(8, 4))
    if subset.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        ax.set_axis_off()
    else:
        subset = subset.sort_values("timestamp")
        ax.plot(subset["timestamp"], subset["value"], marker="o")
        ax.set_ylabel(metric)
        ax.tick_params(axis="x", rotation=45)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(output_path.as_posix(), dpi=150)
    plt.close(fig)


def observations(timeseries_csv: str, output_dir: str, show: bool = False) -> Dict[str, str]:
    del show
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(timeseries_csv)
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    reports: Dict[str, str] = {}
    for metric, (filename, title) in METRICS.items():
        output_path = out / filename
        _render_metric_plot(df=df, metric=metric, output_path=output_path, title=title)
        key = filename.replace(".png", "") + "_plot"
        reports[key] = output_path.as_posix()

    return {
        "kueue_controller_memory_plot": reports["kueue_controller_memory_plot"],
        "kueue_controller_cpu_plot": reports["kueue_controller_cpu_plot"],
        "apiserver_latency_plot": reports["apiserver_latency_plot"],
        "queue_depth_plot": reports["queue_depth_plot"],
    }
