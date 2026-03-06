import json
import time
from pathlib import Path

from kueuer.observe.collector import ObservationCollector
from kueuer.observe.models import ObservationSample


def test_collector_periodically_samples() -> None:
    calls = {"n": 0}

    def snapshot_fn(namespace: str):
        calls["n"] += 1
        return {
            "samples": [
                ObservationSample(
                    timestamp="2026-03-05T00:00:00Z",
                    source="apiserver",
                    available=True,
                    values={"apiserver_non_watch_request_p95_seconds": 0.1},
                    labels={},
                )
            ],
            "capabilities": {"apiserver": True},
        }

    collector = ObservationCollector(
        namespace="skaha-workload",
        interval_seconds=0.01,
        snapshot_fn=snapshot_fn,
    )
    collector.start()
    time.sleep(0.06)
    collector.stop()

    assert calls["n"] >= 2
    assert len(collector.samples) >= 2


def test_collector_writes_jsonl_and_csv(tmp_path: Path) -> None:
    def snapshot_fn(namespace: str):
        return {
            "samples": [
                ObservationSample(
                    timestamp="2026-03-05T00:00:00Z",
                    source="queues",
                    available=True,
                    values={"pending_workloads": 3.0},
                    labels={},
                )
            ],
            "capabilities": {"queues": True},
        }

    collector = ObservationCollector(
        namespace="skaha-workload",
        interval_seconds=1.0,
        snapshot_fn=snapshot_fn,
    )
    collector.collect_once()
    outputs = collector.write_series(tmp_path.as_posix())

    raw_jsonl = Path(outputs["raw_samples_jsonl"])
    timeseries_csv = Path(outputs["timeseries_csv"])
    assert raw_jsonl.exists()
    assert timeseries_csv.exists()

    lines = raw_jsonl.read_text(encoding="utf-8").strip().splitlines()
    payload = json.loads(lines[0])
    assert payload["source"] == "queues"


def test_collector_handles_snapshot_errors_gracefully() -> None:
    def snapshot_fn(namespace: str):
        raise RuntimeError("metrics unavailable")

    collector = ObservationCollector(
        namespace="skaha-workload",
        interval_seconds=1.0,
        snapshot_fn=snapshot_fn,
    )
    collector.collect_once()

    assert len(collector.samples) == 1
    assert collector.samples[0].available is False
    assert collector.samples[0].source == "collector"
