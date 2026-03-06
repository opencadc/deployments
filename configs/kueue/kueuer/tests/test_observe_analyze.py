from kueuer.observe.analyze import evaluate_policy, summarize_observations
from kueuer.observe.models import ObservationPolicyResult, ObservationSample


def test_summarize_observations_computes_p95_and_max() -> None:
    samples = [
        ObservationSample(
            timestamp="2026-03-05T00:00:00Z",
            source="kueue-controller",
            available=True,
            values={
                "kueue_controller_memory_working_set_bytes": 1024.0,
                "apiserver_non_watch_request_p95_seconds": 0.10,
            },
            labels={},
        ),
        ObservationSample(
            timestamp="2026-03-05T00:00:05Z",
            source="kueue-controller",
            available=True,
            values={
                "kueue_controller_memory_working_set_bytes": 2048.0,
                "apiserver_non_watch_request_p95_seconds": 0.30,
            },
            labels={},
        ),
    ]

    summary = summarize_observations(samples, capabilities={"apiserver": True})
    assert summary.aggregate_metrics["kueue_controller_memory_working_set_bytes_max"] == 2048.0
    assert summary.aggregate_metrics["apiserver_non_watch_request_p95_seconds_p95"] == 0.30


def test_evaluate_policy_detects_threshold_violations() -> None:
    summary_metrics = {
        "kueue_controller_memory_working_set_bytes_max": 3 * 1024**3,
        "kueue_controller_restart_count_delta_max": 1.0,
        "benchmark_oomkilled_pods_max": 0.0,
        "apiserver_non_watch_request_p95_seconds_p95": 0.25,
    }
    baseline_metrics = {
        "apiserver_non_watch_request_p95_seconds_p95": 0.10,
    }

    result = evaluate_policy(
        summary_metrics=summary_metrics,
        baseline_metrics=baseline_metrics,
    )

    assert isinstance(result, ObservationPolicyResult)
    assert result.status == "fail"
    assert any("memory" in item for item in result.violations)
    assert any("apiserver" in item for item in result.violations)


def test_evaluate_policy_pass_when_within_thresholds() -> None:
    result = evaluate_policy(
        summary_metrics={
            "kueue_controller_memory_working_set_bytes_max": float(1 * 1024**3),
            "kueue_controller_restart_count_delta_max": 0.0,
            "benchmark_oomkilled_pods_max": 0.0,
            "apiserver_non_watch_request_p95_seconds_p95": 0.12,
        },
        baseline_metrics={"apiserver_non_watch_request_p95_seconds_p95": 0.11},
    )
    assert result.status == "pass"
    assert result.violations == []


def test_evaluate_policy_uses_restart_delta_metric_name() -> None:
    result = evaluate_policy(
        summary_metrics={
            "kueue_controller_memory_working_set_bytes_max": float(1 * 1024**3),
            "kueue_controller_restart_count_delta": 1.0,
            "benchmark_oomkilled_pods_max": 0.0,
            "apiserver_non_watch_request_p95_seconds_p95": 0.12,
        },
        baseline_metrics={"apiserver_non_watch_request_p95_seconds_p95": 0.11},
    )
    assert result.status == "fail"
    assert result.checks["kueue_controller_restart_count_delta"] == "fail"


def test_evaluate_policy_fails_when_oom_metric_is_missing() -> None:
    result = evaluate_policy(
        summary_metrics={
            "kueue_controller_memory_working_set_bytes_max": float(1 * 1024**3),
            "kueue_controller_restart_count_delta": 0.0,
            "apiserver_non_watch_request_p95_seconds_p95": 0.12,
        },
        baseline_metrics={"apiserver_non_watch_request_p95_seconds_p95": 0.11},
    )
    assert result.status == "fail"
    assert result.checks["benchmark_oomkilled_pods_max"] == "fail"
    assert any("OOM metric unavailable" in item for item in result.violations)


def test_unavailable_samples_do_not_produce_passing_policy() -> None:
    samples = [
        ObservationSample(
            timestamp="2026-03-05T00:00:00Z",
            source="kueue-controller",
            available=False,
            values={
                "kueue_controller_memory_working_set_bytes": 0.0,
                "kueue_controller_restart_count_delta": 0.0,
            },
            labels={"error": "missing"},
        ),
        ObservationSample(
            timestamp="2026-03-05T00:00:05Z",
            source="apiserver",
            available=False,
            values={"apiserver_non_watch_request_p95_seconds": 0.0},
            labels={"error": "missing"},
        ),
        ObservationSample(
            timestamp="2026-03-05T00:00:10Z",
            source="queues",
            available=False,
            values={"benchmark_oomkilled_pods": 0.0},
            labels={"error": "missing"},
        ),
    ]

    summary = summarize_observations(
        samples,
        capabilities={
            "kueue-controller": False,
            "apiserver": False,
            "queues": False,
        },
    )
    result = evaluate_policy(summary.aggregate_metrics)
    assert result.status == "fail"
