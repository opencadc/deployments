from datetime import datetime, timezone

from kueuer.benchmarks.track import _apply_workload_conditions


def _sample_workload() -> dict:
    return {
        "metadata": {"uid": "uid-1", "name": "job-kueue-eviction-low-job-0"},
        "spec": {"priority": 10000},
        "status": {
            "conditions": [
                {
                    "type": "Admitted",
                    "status": "True",
                    "lastTransitionTime": "2026-03-05T00:00:00Z",
                    "reason": "Admitted",
                    "message": "Admitted",
                },
                {
                    "type": "Evicted",
                    "status": "True",
                    "lastTransitionTime": "2026-03-05T00:01:00Z",
                    "reason": "Preempted",
                    "message": "Preempted by workload (UID: 11111111-2222-3333-4444-555555555555, JobUID: job-1)",
                },
                {
                    "type": "Requeued",
                    "status": "True",
                    "lastTransitionTime": "2026-03-05T00:01:01Z",
                    "reason": "Backoff",
                    "message": "Requeued",
                },
                {
                    "type": "Finished",
                    "status": "True",
                    "lastTransitionTime": "2026-03-05T00:02:00Z",
                    "reason": "JobFinished",
                    "message": "Done",
                },
            ]
        },
    }


def test_apply_workload_conditions_deduplicates_replayed_events() -> None:
    workloads: dict = {}
    seen: dict = {}
    data = _sample_workload()

    first_finished = _apply_workload_conditions(workloads, seen, data)
    second_finished = _apply_workload_conditions(workloads, seen, data)

    record = workloads["uid-1"]
    assert first_finished is True
    assert second_finished is False
    assert record["requeues"] == 1
    assert len(record["preemptors"]) == 1
    assert record["preemptors"][0][0] == "11111111-2222-3333-4444-555555555555"
    assert record["admitted_at"] == datetime(2026, 3, 5, 0, 0, tzinfo=timezone.utc)
    assert record["finished_at"] == datetime(2026, 3, 5, 0, 2, tzinfo=timezone.utc)
