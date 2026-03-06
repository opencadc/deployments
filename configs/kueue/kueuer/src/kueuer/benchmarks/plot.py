from pathlib import Path
from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib import ticker
import pandas as pd
import seaborn as sns
import typer

from kueuer.utils import io


sns.set_theme(
    style="whitegrid",
    context="talk",
    rc={
        "axes.facecolor": "#fbfaf7",
        "figure.facecolor": "#f4f1ea",
        "grid.color": "#d9d2c6",
        "axes.edgecolor": "#cfc6b8",
        "axes.titleweight": "bold",
    },
)

PALETTE = {
    False: "#4c6a92",
    True: "#d2693c",
}
MODE_LABELS = {
    False: "Direct Kubernetes",
    True: "Kueue-managed",
}
PRIORITY_LABELS = {
    10000: "Low",
    100000: "Medium",
    1000000: "High",
}
PRIORITY_COLORS = {
    "Low": "#8c6d5a",
    "Medium": "#d1a24c",
    "High": "#487c6e",
}

app = typer.Typer(help="Plot Kueue benchmark results.")


def _finalize_plot(
    fig: plt.Figure,
    filename: str,
    output_dir: Optional[str],
    show: bool,
) -> None:
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / filename, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    if show:
        plt.show()
    plt.close(fig)


def _annotate_empty(ax: plt.Axes, message: str) -> None:
    ax.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        fontsize=12,
        color="#5b5146",
        transform=ax.transAxes,
    )
    ax.set_axis_off()


def _style_axis(ax: plt.Axes, title: str, ylabel: str) -> None:
    ax.set_title(title, loc="left", pad=14)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.55)
    ax.grid(axis="x", alpha=0.10)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _job_count_ticks(ax: plt.Axes, values: pd.Series) -> None:
    unique = sorted({int(value) for value in values.dropna().tolist()})
    if not unique:
        return
    if len(unique) >= 4 and max(unique) / min(unique) >= 4:
        ax.set_xscale("log")
    ax.set_xticks(unique)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))


def _summary_by_count(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    summary = (
        df.groupby(["use_kueue", "job_count"])[metric]
        .agg(
            median="median",
            p25=lambda values: values.quantile(0.25),
            p75=lambda values: values.quantile(0.75),
        )
        .reset_index()
        .sort_values(["use_kueue", "job_count"])
    )
    return summary


def _plot_metric_trend(
    df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    filename: str,
    output_dir: Optional[str],
    show: bool,
    y_limits: tuple[float, float] | None = None,
    formatter: ticker.Formatter | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    summary = _summary_by_count(df, metric)

    for use_kueue in (False, True):
        subset = df[df["use_kueue"] == use_kueue].sort_values("job_count")
        series = summary[summary["use_kueue"] == use_kueue]
        color = PALETTE[use_kueue]
        ax.scatter(
            subset["job_count"],
            subset[metric],
            s=45,
            alpha=0.35,
            color=color,
            edgecolors="white",
            linewidths=0.6,
            zorder=3,
        )
        ax.fill_between(
            series["job_count"],
            series["p25"],
            series["p75"],
            color=color,
            alpha=0.14,
            zorder=1,
        )
        ax.plot(
            series["job_count"],
            series["median"],
            color=color,
            linewidth=2.8,
            marker="o",
            markersize=6,
            label=MODE_LABELS[use_kueue],
            zorder=4,
        )

    ax.set_xlabel("Requested jobs")
    _style_axis(ax, title=title, ylabel=ylabel)
    _job_count_ticks(ax, df["job_count"])
    if y_limits is not None:
        ax.set_ylim(*y_limits)
    if formatter is not None:
        ax.yaxis.set_major_formatter(formatter)
    ax.legend(frameon=False, loc="best")
    fig.tight_layout()
    _finalize_plot(fig, filename, output_dir, show)


def _overview_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    metric: str,
    title: str,
    ylabel: str,
    formatter: ticker.Formatter | None = None,
    y_limits: tuple[float, float] | None = None,
) -> None:
    summary = _summary_by_count(df, metric)
    for use_kueue in (False, True):
        series = summary[summary["use_kueue"] == use_kueue]
        color = PALETTE[use_kueue]
        raw = df[df["use_kueue"] == use_kueue]
        ax.scatter(
            raw["job_count"],
            raw[metric],
            s=28,
            alpha=0.25,
            color=color,
            edgecolors="none",
            zorder=2,
        )
        ax.fill_between(
            series["job_count"],
            series["p25"],
            series["p75"],
            color=color,
            alpha=0.12,
            zorder=1,
        )
        ax.plot(
            series["job_count"],
            series["median"],
            color=color,
            linewidth=2.2,
            marker="o",
            markersize=4.5,
            label=MODE_LABELS[use_kueue],
            zorder=3,
        )

    ax.set_xlabel("Requested jobs")
    _style_axis(ax, title=title, ylabel=ylabel)
    _job_count_ticks(ax, df["job_count"])
    if formatter is not None:
        ax.yaxis.set_major_formatter(formatter)
    if y_limits is not None:
        ax.set_ylim(*y_limits)


def _plot_performance_overview(
    df: pd.DataFrame,
    output_dir: Optional[str],
    show: bool,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=False)
    _overview_panel(
        axes[0, 0],
        df,
        "throughput",
        "Scale throughput",
        "Completed jobs per second",
    )
    _overview_panel(
        axes[0, 1],
        df,
        "completion_ratio",
        "Completion ratio",
        "Completed/requested",
        formatter=ticker.PercentFormatter(xmax=1.0),
        y_limits=(0.0, 1.05),
    )
    _overview_panel(
        axes[1, 0],
        df,
        "tail_job_turnaround_s",
        "Tail turnaround",
        "Seconds",
    )
    _overview_panel(
        axes[1, 1],
        df,
        "turnaround_overhead_s",
        "Non-runtime overhead",
        "Seconds above job runtime",
    )
    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    for ax in axes.flat:
        if ax.legend_ is not None:
            ax.legend_.remove()
    fig.suptitle(
        "Kueue benchmark performance overview",
        x=0.06,
        y=1.02,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.tight_layout()
    _finalize_plot(fig, "performance_overview.png", output_dir, show)


def _plot_eviction_pressure(
    df: pd.DataFrame,
    output_dir: Optional[str],
    show: bool,
) -> None:
    summary = (
        df.groupby("priority_label")
        .agg(total_evictions=("num_evictions", "sum"), median_requeues=("requeues", "median"))
        .reindex(["Low", "Medium", "High"])
        .fillna(0.0)
        .reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2))
    axes[0].bar(
        summary["priority_label"],
        summary["total_evictions"],
        color=[PRIORITY_COLORS[label] for label in summary["priority_label"]],
        width=0.65,
    )
    _style_axis(axes[0], "Total evictions by priority", "Eviction count")
    axes[0].set_xlabel("Priority tier")

    sns.stripplot(
        data=df,
        x="priority_label",
        y="requeues",
        hue="priority_label",
        order=["Low", "Medium", "High"],
        palette=PRIORITY_COLORS,
        size=7,
        jitter=0.18,
        alpha=0.75,
        ax=axes[1],
        legend=False,
    )
    sns.pointplot(
        data=df,
        x="priority_label",
        y="requeues",
        order=["Low", "Medium", "High"],
        estimator="median",
        errorbar=None,
        color="#2f4858",
        markers="D",
        linestyles="",
        ax=axes[1],
    )
    _style_axis(axes[1], "Requeue pressure by priority", "Requeues per workload")
    axes[1].set_xlabel("Priority tier")
    fig.suptitle(
        "Eviction pressure overview",
        x=0.06,
        y=1.02,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.tight_layout()
    _finalize_plot(fig, "eviction_pressure_by_priority.png", output_dir, show)


def _plot_workload_timeline(
    df: pd.DataFrame,
    output_dir: Optional[str],
    show: bool,
) -> None:
    timeline = df.sort_values(["priority", "admitted_at", "name"]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(13.5, max(4.5, len(timeline) * 0.5)))
    y_positions = list(range(len(timeline)))

    for idx, row in timeline.iterrows():
        label = row["priority_label"]
        color = PRIORITY_COLORS.get(label, "#6c757d")
        admitted_at = row["admitted_at"]
        finished_at = row["finished_at"] if pd.notna(row["finished_at"]) else admitted_at
        ax.hlines(
            y=idx,
            xmin=admitted_at,
            xmax=finished_at,
            color=color,
            linewidth=4.0,
            alpha=0.9,
        )
        ax.scatter(admitted_at, idx, color=color, s=45, edgecolors="white", linewidths=0.6)
        ax.scatter(finished_at, idx, color="#202124", s=40, marker="s")
        for _preemptor_uid, event_time in row["preemptors"]:
            ax.scatter(
                pd.to_datetime(event_time),
                idx,
                color="#b83232",
                s=70,
                marker="X",
                linewidths=0.8,
            )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        [f"{row['name']} ({row['priority_label']})" for _, row in timeline.iterrows()]
    )
    ax.set_xlabel("Benchmark time")
    _style_axis(ax, "Workload runtime timeline", "Workload")
    fig.autofmt_xdate()
    fig.tight_layout()
    _finalize_plot(fig, "workload_runtime_timeline.png", output_dir, show)


def _plot_eviction_heatmap(
    evict_df: pd.DataFrame,
    output_dir: Optional[str],
    show: bool,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 4.8))
    if evict_df.empty:
        _annotate_empty(ax, "No eviction events were recorded for this run.")
    else:
        evict_df = evict_df.copy()
        evict_df["time_bin"] = evict_df["time"].dt.floor("1s")
        evict_df["priority_label"] = evict_df["priority"].map(PRIORITY_LABELS)
        heat = (
            evict_df.groupby(["priority_label", "time_bin"])
            .size()
            .reset_index(name="count")
            .pivot(index="priority_label", columns="time_bin", values="count")
            .reindex(["Low", "Medium", "High"])
            .fillna(0.0)
        )
        sns.heatmap(
            heat,
            cmap=sns.color_palette("flare", as_cmap=True),
            linewidths=0.5,
            linecolor="#f4f1ea",
            cbar_kws={"label": "Evictions per second"},
            ax=ax,
        )
        _style_axis(ax, "Eviction heatmap", "Priority tier")
        ax.set_xlabel("Benchmark time")
    fig.tight_layout()
    _finalize_plot(fig, "eviction_heatmap.png", output_dir, show)


def load_results(filepath: str) -> pd.DataFrame:
    return pd.read_csv(
        filepath,
        parse_dates=[
            "timestamp",
            "first_creation_time",
            "last_creation_time",
            "first_completion_time",
            "last_completion_time",
        ],
    )


def compute_throughput(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    completed = df.get("completed_jobs_tracked", df["job_count"]).fillna(df["job_count"])
    df["throughput"] = completed / df["total_execution_time"].replace(0, pd.NA)
    df["throughput"] = df["throughput"].fillna(0.0)
    return df


def compute_latency(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["first_job_turnaround_s"] = (
        df["first_completion_time"] - df["first_creation_time"]
    ).dt.total_seconds()
    df["tail_job_turnaround_s"] = (
        df["last_completion_time"] - df["last_creation_time"]
    ).dt.total_seconds()
    df["run_makespan_s"] = (
        df["last_completion_time"] - df["first_creation_time"]
    ).dt.total_seconds()
    df["startup_latency"] = df["first_job_turnaround_s"]
    df["completion_latency"] = df["tail_job_turnaround_s"]
    return df


def compute_completion_ratio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "completion_ratio" in df.columns:
        df["completion_ratio"] = pd.to_numeric(df["completion_ratio"], errors="coerce").fillna(0.0)
        return df
    if "completed_jobs_tracked" in df.columns:
        ratio = pd.to_numeric(df["completed_jobs_tracked"], errors="coerce").fillna(0.0)
        df["completion_ratio"] = ratio / df["job_count"].replace(0, pd.NA)
        df["completion_ratio"] = df["completion_ratio"].fillna(0.0)
        return df
    df["completion_ratio"] = 1.0
    return df


def compute_cv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    denominator = df["avg_time_from_creation_completion"].replace(0, pd.NA)
    df["cv"] = (
        df["std_dev_time_from_creation_completion"] / denominator
    ).fillna(0.0)
    return df


def compute_scheduling_overhead(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "avg_time_from_creation_completion" in df.columns:
        df["turnaround_overhead_s"] = (
            df["avg_time_from_creation_completion"] - df["job_duration"]
        ).clip(lower=0.0)
    else:
        df["turnaround_overhead_s"] = (
            (df["first_completion_time"] - df["first_creation_time"]).dt.total_seconds()
            - df["job_duration"]
        ).clip(lower=0.0)
    return df


def compute_comparative_metrics(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("use_kueue").median(numeric_only=True)
    if not {False, True}.issubset(set(grouped.index.tolist())):
        return pd.DataFrame()
    baseline = grouped.loc[False]
    kueue = grouped.loc[True]
    return pd.DataFrame(
        {
            "throughput_delta_pct": [
                ((kueue["throughput"] - baseline["throughput"]) / baseline["throughput"]) * 100.0
                if baseline["throughput"]
                else 0.0
            ],
            "completion_ratio_delta_pct": [
                (kueue["completion_ratio"] - baseline["completion_ratio"]) * 100.0
            ],
            "tail_turnaround_delta_pct": [
                ((kueue["tail_job_turnaround_s"] - baseline["tail_job_turnaround_s"])
                / baseline["tail_job_turnaround_s"]) * 100.0
                if baseline["tail_job_turnaround_s"]
                else 0.0
            ],
            "turnaround_overhead_delta_pct": [
                ((kueue["turnaround_overhead_s"] - baseline["turnaround_overhead_s"])
                / baseline["turnaround_overhead_s"]) * 100.0
                if baseline["turnaround_overhead_s"]
                else 0.0
            ],
        }
    )


@app.command("performance")
def performance(
    filepath: str,
    output_dir: str = typer.Option(
        ...,
        "-o",
        "--output-dir",
        help="Directory where plots are written.",
    ),
    show: bool = typer.Option(
        False, "--show/--no-show", help="Display plots interactively."
    ),
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = load_results(filepath)
    df = compute_throughput(df)
    df = compute_latency(df)
    df = compute_completion_ratio(df)
    df = compute_cv(df)
    df = compute_scheduling_overhead(df)
    comparative_df = compute_comparative_metrics(df)

    _plot_performance_overview(df, output_dir, show)
    _plot_metric_trend(
        df,
        "throughput",
        "Throughput by requested job count",
        "Completed jobs per second",
        "throughput_by_job_count.png",
        output_dir,
        show,
    )
    _plot_metric_trend(
        df,
        "completion_ratio",
        "Completion ratio by requested job count",
        "Completed/requested",
        "completion_ratio_by_job_count.png",
        output_dir,
        show,
        y_limits=(0.0, 1.05),
        formatter=ticker.PercentFormatter(xmax=1.0),
    )
    _plot_metric_trend(
        df,
        "tail_job_turnaround_s",
        "Tail turnaround by requested job count",
        "Seconds",
        "tail_turnaround_by_job_count.png",
        output_dir,
        show,
    )
    _plot_metric_trend(
        df,
        "turnaround_overhead_s",
        "Non-runtime overhead by requested job count",
        "Seconds above requested runtime",
        "turnaround_overhead_by_job_count.png",
        output_dir,
        show,
    )

    return df, comparative_df


@app.command("evictions")
def evictions(
    filepath: str,
    output_dir: str = typer.Option(
        ...,
        "-o",
        "--output-dir",
        help="Directory where plots are written.",
    ),
    show: bool = typer.Option(
        False, "--show/--no-show", help="Display plots interactively."
    ),
) -> None:
    data = io.read_yaml(filepath)
    df = pd.DataFrame.from_dict(data, orient="index")
    if df.empty:
        df = pd.DataFrame(
            columns=["name", "priority", "admitted_at", "finished_at", "requeues", "preemptors"]
        )
    df["admitted_at"] = pd.to_datetime(df.get("admitted_at"), errors="coerce")
    df["finished_at"] = pd.to_datetime(df.get("finished_at"), errors="coerce")
    df["priority"] = pd.to_numeric(df.get("priority"), errors="coerce").fillna(0).astype(int)
    df["requeues"] = pd.to_numeric(df.get("requeues"), errors="coerce").fillna(0).astype(int)
    df["preemptors"] = df.get("preemptors", pd.Series([[]] * len(df))).apply(
        lambda value: value if isinstance(value, list) else []
    )
    df["num_evictions"] = df["preemptors"].apply(len)
    df["priority_label"] = df["priority"].map(PRIORITY_LABELS).fillna("Unknown")

    eviction_events = []
    for _, row in df.iterrows():
        for _preemptor_id, evict_time in row["preemptors"]:
            eviction_events.append(
                {"time": pd.to_datetime(evict_time), "priority": row["priority"]}
            )
    evict_df = pd.DataFrame(eviction_events, columns=["time", "priority"])

    _plot_eviction_pressure(df, output_dir, show)
    _plot_workload_timeline(df, output_dir, show)
    _plot_eviction_heatmap(evict_df, output_dir, show)
