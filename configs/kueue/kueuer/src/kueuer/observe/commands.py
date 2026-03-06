"""CLI commands for observation collection and analysis."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from kueuer.observe.analyze import evaluate_policy, summarize_observations
from kueuer.observe.collector import ObservationCollector
from kueuer.observe.models import ObservationSample
from kueuer.observe import plot as observe_plot
from kueuer.utils.artifacts import default_run_id

observe_cli = typer.Typer(help="Observation and scale-attribution commands.")


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


def analyze_observations(
    observe_dir: str,
    baseline_summary_path: str = "",
) -> Dict[str, str]:
    root = Path(observe_dir)
    raw_samples_path = root / "raw_samples.jsonl"
    capabilities_path = root / "capabilities.json"

    samples = _load_samples(raw_samples_path)
    capabilities: Dict[str, bool] = {}
    if capabilities_path.exists():
        capabilities = {
            str(key): bool(value)
            for key, value in json.loads(capabilities_path.read_text(encoding="utf-8"))
            .get("capabilities", {})
            .items()
        }

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

    summary_path = root / "summary.json"
    policy_path = root / "policy.json"
    summary_path.write_text(json.dumps(summary.to_dict(), indent=2) + "\n", encoding="utf-8")
    policy_path.write_text(json.dumps(policy.to_dict(), indent=2) + "\n", encoding="utf-8")

    return {
        "summary_json": summary_path.as_posix(),
        "policy_json": policy_path.as_posix(),
    }


def render_observation_report(observe_dir: str) -> str:
    root = Path(observe_dir)
    summary_path = root / "summary.json"
    policy_path = root / "policy.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    policy = json.loads(policy_path.read_text(encoding="utf-8")) if policy_path.exists() else {}

    lines = [
        "# Observation report",
        "",
        f"- status: `{policy.get('status', 'unknown')}`",
        f"- generated_at: `{summary.get('generated_at', '')}`",
        "",
        "## checks",
        "",
    ]
    checks = policy.get("checks", {})
    if checks:
        for key, value in checks.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")

    lines.extend(["", "## violations", ""])
    violations = policy.get("violations", [])
    if violations:
        for item in violations:
            lines.append(f"- {item}")
    else:
        lines.append("- none")

    report_path = root / "report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
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


@observe_cli.command("collect")
def collect(
    artifacts_dir: str = typer.Option("artifacts", "--artifacts-dir"),
    run_id: str = typer.Option("", "--run-id"),
    namespace: str = typer.Option("skaha-workload", "--namespace"),
    interval_seconds: float = typer.Option(5.0, "--interval-seconds"),
    duration_seconds: float = typer.Option(0.0, "--duration-seconds"),
) -> None:
    effective = run_id or _run_id()
    observe_dir = Path(artifacts_dir) / effective / "observe"
    report = collect_observations(
        output_dir=observe_dir.as_posix(),
        namespace=namespace,
        interval_seconds=interval_seconds,
        duration_seconds=duration_seconds,
    )
    typer.echo(f"collect completed for run {effective}: {report['timeseries_csv']}")
    typer.echo(
        f"uv run kr observe plot --run-id {effective} --output-dir artifacts/{effective}/plots/observe --show"
    )
    typer.echo(f"uv run kr observe analyze --run-id {effective}")


@observe_cli.command("analyze")
def analyze(
    artifacts_dir: str = typer.Option("artifacts", "--artifacts-dir"),
    run_id: str = typer.Option("", "--run-id"),
    baseline_summary_path: str = typer.Option("", "--baseline-summary"),
) -> None:
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
    typer.echo(f"analyze completed for run {effective}: {report['policy_json']}")
    typer.echo(f"uv run kr observe report --run-id {effective}")


@observe_cli.command("plot")
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


@observe_cli.command("report")
def report(
    artifacts_dir: str = typer.Option("artifacts", "--artifacts-dir"),
    run_id: str = typer.Option("", "--run-id"),
) -> None:
    effective = run_id or _latest_run_id(Path(artifacts_dir))
    if not effective:
        raise typer.BadParameter(
            "No run directory found under artifacts. Pass --run-id.",
            param_hint="--run-id",
        )
    observe_dir = Path(artifacts_dir) / effective / "observe"
    report_path = render_observation_report(observe_dir.as_posix())
    typer.echo(f"report completed for run {effective}: {report_path}")
