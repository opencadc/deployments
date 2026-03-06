from kueuer.observe.models import (
    ObservationPolicyResult,
    ObservationSample,
    ObservationSeries,
    ObservationSummary,
)


def test_observation_sample_roundtrip() -> None:
    sample = ObservationSample(
        timestamp="2026-03-05T00:00:00Z",
        source="kueue-controller",
        available=True,
        values={"kueue_controller_cpu_cores": 0.2},
        labels={"namespace": "kueue-system"},
    )
    payload = sample.to_dict()
    restored = ObservationSample.from_dict(payload)
    assert restored.timestamp == sample.timestamp
    assert restored.source == sample.source
    assert restored.available is True
    assert restored.values["kueue_controller_cpu_cores"] == 0.2


def test_observation_series_serializes_multiple_samples() -> None:
    series = ObservationSeries(samples=[])
    series.samples.append(
        ObservationSample(
            timestamp="2026-03-05T00:00:00Z",
            source="apiserver",
            available=True,
            values={"apiserver_non_watch_request_p95_seconds": 0.11},
            labels={},
        )
    )
    series.samples.append(
        ObservationSample(
            timestamp="2026-03-05T00:00:05Z",
            source="apiserver",
            available=False,
            values={},
            labels={"reason": "forbidden"},
        )
    )
    payload = series.to_dict()
    restored = ObservationSeries.from_dict(payload)
    assert len(restored.samples) == 2
    assert restored.samples[1].available is False


def test_observation_summary_and_policy_result_roundtrip() -> None:
    summary = ObservationSummary(
        generated_at="2026-03-05T00:10:00Z",
        aggregate_metrics={"kueue_controller_memory_working_set_bytes_max": 1_000_000},
        capabilities={"apiserver": True, "kueue-controller": True},
    )
    policy = ObservationPolicyResult(
        status="pass",
        checks={"kueue_controller_restart_count_delta": "pass"},
        violations=[],
    )

    assert ObservationSummary.from_dict(summary.to_dict()).aggregate_metrics[
        "kueue_controller_memory_working_set_bytes_max"
    ] == 1_000_000
    assert ObservationPolicyResult.from_dict(policy.to_dict()).status == "pass"
