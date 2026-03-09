"""Collect plots and comparison summaries for lifecycle runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict

import pandas as pd
import yaml

from kueuer.benchmarks import plot
from kueuer.observe import plot as observe_plot
from kueuer.observe.commands import analyze_observations


def collect_outputs(
    performance_csv: str,
    evictions_yaml: str,
    output_dir: str,
    performance_plotter: Callable[..., Any] = plot.render_performance_plots,
    evictions_plotter: Callable[..., Any] = plot.render_eviction_plots,
    observe_plotter: Callable[..., Any] = observe_plot.observations,
    observe_analyzer: Callable[..., Any] = analyze_observations,
) -> Dict[str, Any]:
    """Generate plots and summary artifacts for a lifecycle run output directory."""
    root = Path(output_dir)
    perf_plot_dir = root / "plots" / "performance"
    evict_plot_dir = root / "plots" / "evictions"
    observe_dir = root / "observe"
    observe_plot_dir = root / "plots" / "observe"
    perf_plot_dir.mkdir(parents=True, exist_ok=True)
    evict_plot_dir.mkdir(parents=True, exist_ok=True)

    performance_plotter(
        filepath=performance_csv,
        output_dir=perf_plot_dir.as_posix(),
        show=False,
    )
    evictions_plotter(
        filepath=evictions_yaml,
        output_dir=evict_plot_dir.as_posix(),
        show=False,
    )
    observe_artifacts: Dict[str, str] = {}
    observe_analysis: Dict[str, str] = {}
    observe_timeseries = observe_dir / "timeseries.csv"
    if observe_timeseries.exists():
        observe_plot_dir.mkdir(parents=True, exist_ok=True)
        observe_artifacts = observe_plotter(
            timeseries_csv=observe_timeseries.as_posix(),
            output_dir=observe_plot_dir.as_posix(),
            show=False,
        )
        observe_analysis = observe_analyzer(observe_dir=observe_dir.as_posix())

    perf_df = pd.read_csv(performance_csv)
    with open(evictions_yaml, encoding="utf-8") as f:
        evict_data = yaml.safe_load(f) or {}

    summary = {
        "performance_rows": int(len(perf_df)),
        "performance_columns": list(perf_df.columns),
        "tracked_evictions_workloads": int(len(evict_data)),
        "observation_plots_generated": bool(observe_artifacts),
        "performance_plot_dir": perf_plot_dir.as_posix(),
        "evictions_plot_dir": evict_plot_dir.as_posix(),
        "observe_plot_dir": observe_plot_dir.as_posix() if observe_artifacts else "",
        "observe_report_json": observe_analysis.get("report_json", ""),
    }

    report_json_path = root / "report.json"
    report_md_path = root / "report.md"
    report_json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    report_md_path.write_text(
        "\n".join(
            [
                "# Run report",
                "",
                f"- performance rows: `{summary['performance_rows']}`",
                f"- tracked eviction workloads: `{summary['tracked_evictions_workloads']}`",
                f"- performance plots: `{summary['performance_plot_dir']}`",
                f"- eviction plots: `{summary['evictions_plot_dir']}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "ok": True,
        "performance_plot_dir": perf_plot_dir.as_posix(),
        "evictions_plot_dir": evict_plot_dir.as_posix(),
        "observe_plot_dir": observe_plot_dir.as_posix() if observe_artifacts else "",
        "observe_report_json": observe_analysis.get("report_json", ""),
        "report_json": report_json_path.as_posix(),
        "report_md": report_md_path.as_posix(),
        "comparison_summary": report_json_path.as_posix(),
        "comparison_report": report_md_path.as_posix(),
        "observe_summary_json": "",
        "observe_policy_json": "",
        "observe_report_md": "",
        **observe_artifacts,
    }
