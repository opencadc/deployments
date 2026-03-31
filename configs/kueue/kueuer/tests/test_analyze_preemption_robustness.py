from kueuer.benchmarks.analyze import evictions


def test_evictions_handles_missing_preemptor_metadata() -> None:
    workloads = {
        "victim-1": {
            "name": "victim",
            "priority": 100000,
            "requeues": 1,
            "preemptors": [("missing-uid", None)],
        }
    }

    assert evictions(workloads) is False


def test_evictions_detects_priority_violation_when_known() -> None:
    workloads = {
        "victim-1": {
            "name": "victim",
            "priority": 100000,
            "requeues": 1,
            "preemptors": [("preemptor-1", None)],
        },
        "preemptor-1": {"name": "preemptor", "priority": 10000, "requeues": 0},
    }

    assert evictions(workloads) is True
