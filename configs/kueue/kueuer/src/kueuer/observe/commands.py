"""CLI commands for observation collection and analysis."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

import typer

from kueuer.observe import plot as observe_plot
from kueuer.observe.analyze import evaluate_policy, summarize_observations
from kueuer.observe.collector import ObservationCollector
from kueuer.observe.models import ObservationSample
from kueuer.utils.artifacts import default_run_id

observe_cli = typer.Typer(
    help=(
        "Collect, summarize, and visualize control-plane observations for "
        "Kueue benchmark and lifecycle runs."
    )
)


def _run_id() -> str:
    return default_run_id()


def _latest_run_id(artifacts_dir: Path) -> Optional[str]:
    run_ids: List[str] = []
    for child in artifacts_dir.iterdir() if artifacts_dir.exists() else []:
        if not child.is_dir():
            continue
        if (child / "observe").exists():
            run_ids.append(child.name)
    if not run_ids:
        return None
    return sorted(run_ids)[-1]


def collect_observations(
    output_dir: str,
    namespace: str,
    interval_seconds: float = 5.0,
    duration_seconds: float = 0.0,
) -> Dict[str, str]:
    collector = ObservationCollector(
        namespace=namespace,
        interval_seconds=interval_seconds,
    )
    if duration_seconds > 0:
        collector.start()
        time.sleep(duration_seconds)
        collector.stop()
    else:
        collector.collect_once()
    return collector.write_series(output_dir)


def _load_samples(raw_samples_jsonl: Path) -> List[ObservationSample]:
    samples: List[ObservationSample] = []
    if not raw_samples_jsonl.exists():
        return samples
    for line in raw_samples_jsonl.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        payload = json.loads(text)
        samples.append(ObservationSample.from_dict(payload))
    return samples


def _load_samples_from_timeseries(timeseries_csv: Path) -> List[ObservationSample]:
    grouped: Dict[tuple[str, str, bool, str], ObservationSample] = {}
    if not timeseries_csv.exists():
        return []

    with timeseries_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            timestamp = str(row.get("timestamp", ""))
            source = str(row.get("source", ""))
            available = str(row.get("available", "")).strip().lower() == "true"
            labels_json = str(row.get("labels_json", "") or "{}")
            try:
                labels = json.loads(labels_json) if labels_json else {}
            except json.JSONDecodeError:
                labels = {}
            key = (timestamp, source, available, json.dumps(labels, sort_keys=True))
            sample = grouped.setdefault(
                key,
                ObservationSample(
                    timestamp=timestamp,
                    source=source,
                    available=available,
                    values={},
                    labels={str(k): str(v) for k, v in dict(labels).items()},
                ),
            )
            metric = str(row.get("metric", "") or "").strip()
            value = str(row.get("value", "") or "").strip()
            if metric and value:
                sample.values[metric] = float(value)

    return list(grouped.values())


def _derive_capabilities(samples: List[ObservationSample]) -> Dict[str, bool]:
    capabilities: Dict[str, bool] = {}
    for sample in samples:
        capabilities[sample.source] = capabilities.get(sample.source, False) or sample.available
    return capabilities


def analyze_observations(
    observe_dir: str,
    baseline_summary_path: str = "",
) -> Dict[str, str]:
    root = Path(observe_dir)
    timeseries_path = root / "timeseries.csv"

    samples = _load_samples_from_timeseries(timeseries_path)
    capabilities = _derive_capabilities(samples)

    summary = summarize_observations(samples, capabilities=capabilities)

    baseline_metrics: Dict[str, float] = {}
    if baseline_summary_path:
        baseline_payload = json.loads(Path(baseline_summary_path).read_text(encoding="utf-8"))
        baseline_metrics = {
            str(key): float(value)
            for key, value in baseline_payload.get("aggregate_metrics", {}).items()
        }

    policy = evaluate_policy(
        summary_metrics=summary.aggregate_metrics,
        baseline_metrics=baseline_metrics,
    )

    report_path = root / "report.json"
    report_payload = {
        "generated_at": summary.generated_at,
        "aggregate_metrics": summary.aggregate_metrics,
        "capabilities": summary.capabilities,
        "status": policy.status,
        "checks": policy.checks,
        "violations": policy.violations,
    }
    report_path.write_text(json.dumps(report_payload, indent=2) + "\n", encoding="utf-8")

    return {"report_json": report_path.as_posix()}


def render_observation_report(observe_dir: str) -> str:
    root = Path(observe_dir)
    report_path = root / "report.json"
    if not report_path.exists():
        report_path = Path(analyze_observations(observe_dir=observe_dir)["report_json"])
    return report_path.as_posix()


def render_observation_plots(
    observe_dir: str,
    output_dir: str,
    show: bool = False,
) -> Dict[str, str]:
    root = Path(observe_dir)
    timeseries_csv = root / "timeseries.csv"
    return observe_plot.observations(
        timeseries_csv=timeseries_csv.as_posix(),
        output_dir=output_dir,
        show=show,
    )


@observe_cli.command(
    "collect",
    help=(
        "Collect raw observation samples for controller, API server, and queue "
        "state under artifacts/<run-id>/observe/."
    ),
)
def collect(
    artifacts_dir: str = typer.Option("artifacts", "--artifacts-dir"),
    run_id: str = typer.Option("", "--run-id"),
    namespace: str = typer.Option("skaha-workload", "--namespace"),
    interval_seconds: float = typer.Option(5.0, "--interval-seconds"),
    duration_seconds: float = typer.Option(0.0, "--duration-seconds"),
) -> None:
    """Collect one-shot or time-bounded observation samples for a run."""
    effective = run_id or _run_id()
    observe_dir = Path(artifacts_dir) / effective / "observe"
    report = collect_observations(
        output_dir=observe_dir.as_posix(),
        namespace=namespace,
        interval_seconds=interval_seconds,
        duration_seconds=duration_seconds,
    )
    typer.echo(f"collect completed for run {effective}: {report['timeseries_csv']}")
    typer.echo(f"uv run kr plot observations artifacts/{effective}/observe/timeseries.csv --show")
    typer.echo(f"uv run kr observe analyze --run-id {effective}")


@observe_cli.command(
    "analyze",
    help=(
        "Summarize observation samples and evaluate the rollout policy for a "
        "run directory."
    ),
)
def analyze(
    artifacts_dir: str = typer.Option("artifacts", "--artifacts-dir"),
    run_id: str = typer.Option("", "--run-id"),
    baseline_summary_path: str = typer.Option("", "--baseline-summary"),
) -> None:
    """Summarize observation samples and write policy artifacts."""
    effective = run_id or _latest_run_id(Path(artifacts_dir))
    if not effective:
        raise typer.BadParameter(
            "No run directory found under artifacts. Pass --run-id.",
            param_hint="--run-id",
        )
    observe_dir = Path(artifacts_dir) / effective / "observe"
    report = analyze_observations(
        observe_dir=observe_dir.as_posix(),
        baseline_summary_path=baseline_summary_path,
    )
    typer.echo(f"analyze completed for run {effective}: {report['report_json']}")
    typer.echo(f"uv run kr observe report --run-id {effective}")


@observe_cli.command(
    "plot",
    help=(
        "Render observation plots from observe/timeseries.csv for an existing "
        "run directory."
    ),
)
def plot(
    artifacts_dir: str = typer.Option("artifacts", "--artifacts-dir"),
    run_id: str = typer.Option("", "--run-id"),
    output_dir: str = typer.Option(
        ...,
        "--output-dir",
        help="Directory where observation plots are written.",
    ),
    show: bool = typer.Option(
        False,
        "--show/--no-show",
        help="Display plots interactively.",
    ),
) -> None:
    """Render observation plots into an explicit output directory."""
    effective = run_id or _latest_run_id(Path(artifacts_dir))
    if not effective:
        raise typer.BadParameter(
            "No run directory found under artifacts. Pass --run-id.",
            param_hint="--run-id",
        )
    observe_dir = Path(artifacts_dir) / effective / "observe"
    report = render_observation_plots(
        observe_dir=observe_dir.as_posix(),
        output_dir=output_dir,
        show=show,
    )
    typer.echo(f"plot completed for run {effective}: {report['observation_overview_plot']}")


@observe_cli.command(
    "report",
    help=(
        "Return the consolidated observation report.json for a run directory."
        "for a run directory."
    ),
)
def report(
    artifacts_dir: str = typer.Option("artifacts", "--artifacts-dir"),
    run_id: str = typer.Option("", "--run-id"),
) -> None:
    """Render the Markdown observation report for a run."""
    effective = run_id or _latest_run_id(Path(artifacts_dir))
    if not effective:
        raise typer.BadParameter(
            "No run directory found under artifacts. Pass --run-id.",
            param_hint="--run-id",
        )
    observe_dir = Path(artifacts_dir) / effective / "observe"
    report_path = render_observation_report(observe_dir.as_posix())
    typer.echo(f"report completed for run {effective}: {report_path}")
