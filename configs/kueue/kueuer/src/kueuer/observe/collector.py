"""Periodic collector for observation samples."""

from __future__ import annotations

import csv
import json
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List

from kueuer.observe.models import ObservationSample
from kueuer.observe.samplers import collect_sampler_snapshot, utc_now_iso
from kueuer.utils.constants import (
    DEFAULT_OBSERVATION_INTERVAL_SECONDS,
    MIN_OBSERVATION_INTERVAL_SECONDS,
)


class ObservationCollector:
    def __init__(
        self,
        namespace: str,
        interval_seconds: float = DEFAULT_OBSERVATION_INTERVAL_SECONDS,
        snapshot_fn: Callable[[str], Dict[str, Any]] = collect_sampler_snapshot,
    ) -> None:
        self.namespace = namespace
        self.interval_seconds = max(float(interval_seconds), MIN_OBSERVATION_INTERVAL_SECONDS)
        self.snapshot_fn = snapshot_fn
        self.samples: List[ObservationSample] = []
        self.capabilities: Dict[str, bool] = {}
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def collect_once(self) -> None:
        try:
            snapshot = self.snapshot_fn(self.namespace)
            for sample in snapshot.get("samples", []):
                if isinstance(sample, ObservationSample):
                    self.samples.append(sample)
            for key, value in snapshot.get("capabilities", {}).items():
                self.capabilities[str(key)] = bool(value)
        except Exception as error:  # noqa: BLE001
            self.samples.append(
                ObservationSample(
                    timestamp=utc_now_iso(),
                    source="collector",
                    available=False,
                    values={},
                    labels={"error": str(error)},
                )
            )

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self.collect_once()
            self._stop_event.wait(self.interval_seconds)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=max(self.interval_seconds * 2, 1.0))

    def write_series(self, output_dir: str) -> Dict[str, str]:
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)
        timeseries_csv = root / "timeseries.csv"

        with timeseries_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "timestamp",
                    "source",
                    "available",
                    "metric",
                    "value",
                    "labels_json",
                ],
            )
            writer.writeheader()
            for sample in self.samples:
                labels_json = json.dumps(sample.labels, sort_keys=True)
                if not sample.values:
                    writer.writerow(
                        {
                            "timestamp": sample.timestamp,
                            "source": sample.source,
                            "available": str(sample.available).lower(),
                            "metric": "",
                            "value": "",
                            "labels_json": labels_json,
                        }
                    )
                for metric, value in sample.values.items():
                    writer.writerow(
                        {
                            "timestamp": sample.timestamp,
                            "source": sample.source,
                            "available": str(sample.available).lower(),
                            "metric": metric,
                            "value": value,
                            "labels_json": labels_json,
                        }
                    )

        return {
            "timeseries_csv": timeseries_csv.as_posix(),
        }
