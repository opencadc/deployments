"""Internal observation collection and analysis functions.

These functions are used by the lifecycle module when the --observe flag is enabled.
They are not exposed as CLI commands - observation functionality is accessed through
the lifecycle e2e command with --observe, and plots are generated via 'kr plot observations'.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from kueuer.observe import plot as observe_plot
from kueuer.observe.analyze import evaluate_policy, summarize_observations
from kueuer.observe.collector import ObservationCollector
from kueuer.observe.models import ObservationSample
from kueuer.utils.constants import DEFAULT_OBSERVATION_INTERVAL_SECONDS


def collect_observations(
    output_dir: str,
    namespace: str,
    interval_seconds: float = DEFAULT_OBSERVATION_INTERVAL_SECONDS,
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
