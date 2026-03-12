"""Typed data models for observation artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ObservationSample:
    timestamp: str
    source: str
    available: bool
    values: Dict[str, float]
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "available": self.available,
            "values": self.values,
            "labels": self.labels,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ObservationSample":
        return cls(
            timestamp=str(payload.get("timestamp", "")),
            source=str(payload.get("source", "")),
            available=bool(payload.get("available", False)),
            values={
                str(key): float(value)
                for key, value in dict(payload.get("values", {})).items()
            },
            labels={
                str(key): str(value)
                for key, value in dict(payload.get("labels", {})).items()
            },
        )


@dataclass
class ObservationSeries:
    samples: List[ObservationSample] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"samples": [sample.to_dict() for sample in self.samples]}

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ObservationSeries":
        raw = payload.get("samples", [])
        samples = [ObservationSample.from_dict(item) for item in raw]
        return cls(samples=samples)


@dataclass
class ObservationSummary:
    generated_at: str
    aggregate_metrics: Dict[str, float] = field(default_factory=dict)
    capabilities: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "aggregate_metrics": self.aggregate_metrics,
            "capabilities": self.capabilities,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ObservationSummary":
        return cls(
            generated_at=str(payload.get("generated_at", "")),
            aggregate_metrics={
                str(key): float(value)
                for key, value in dict(payload.get("aggregate_metrics", {})).items()
            },
            capabilities={
                str(key): bool(value)
                for key, value in dict(payload.get("capabilities", {})).items()
            },
        )


@dataclass
class ObservationPolicyResult:
    status: str
    checks: Dict[str, str] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "checks": self.checks,
            "violations": self.violations,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ObservationPolicyResult":
        return cls(
            status=str(payload.get("status", "unknown")),
            checks={
                str(key): str(value) for key, value in dict(payload.get("checks", {})).items()
            },
            violations=[str(item) for item in payload.get("violations", [])],
        )
