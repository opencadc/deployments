from types import SimpleNamespace
from typing import Dict, List

from kueuer.lifecycle import teardown
from kueuer.lifecycle.queues import default_config_paths


def test_cleanup_benchmark_jobs_reports_deleted_and_empty_remaining() -> None:
    deleted: Dict[str, int] = {}

    def delete_fn(namespace: str, prefix: str) -> int:
        deleted[prefix] = deleted.get(prefix, 0) + 1
        return 2

    report = teardown.cleanup_benchmark_jobs(
        namespace="skaha-workload",
        prefixes=["direct-", "kueue-"],
        delete_fn=delete_fn,
        list_jobs_fn=lambda namespace: [],
    )

    assert report["ok"] is True
    assert report["total_deleted"] == 4
    assert deleted["direct-"] == 1
    assert deleted["kueue-"] == 1


def test_cleanup_benchmark_jobs_detects_remaining_prefixes() -> None:
    remaining_jobs: List[str] = ["kueue-foo", "other-job"]
    report = teardown.cleanup_benchmark_jobs(
        namespace="skaha-workload",
        prefixes=["kueue-"],
        delete_fn=lambda namespace, prefix: 0,
        list_jobs_fn=lambda namespace: remaining_jobs,
    )
    assert report["ok"] is False
    assert report["remaining"] == ["kueue-foo"]


def test_cleanup_benchmark_jobs_waits_for_eventual_deletion() -> None:
    calls = {"n": 0}

    def list_fn(namespace: str):
        calls["n"] += 1
        return ["kueue-foo"] if calls["n"] == 1 else []

    report = teardown.cleanup_benchmark_jobs(
        namespace="skaha-workload",
        prefixes=["kueue-"],
        delete_fn=lambda namespace, prefix: 1,
        list_jobs_fn=list_fn,
        verify_wait_seconds=2,
    )
    assert report["ok"] is True


def test_cleanup_queues_uses_absolute_queue_config_paths() -> None:
    calls: List[List[str]] = []

    def run_cmd(command: List[str]):
        calls.append(command)
        return SimpleNamespace(returncode=0)

    report = teardown.cleanup_queues(run_cmd=run_cmd)
    cluster_config, local_config = default_config_paths()

    assert report["ok"] is True
    assert calls[0] == [
        "kubectl",
        "delete",
        "-f",
        local_config,
        "--ignore-not-found=true",
    ]
    assert calls[1] == [
        "kubectl",
        "delete",
        "-f",
        cluster_config,
        "--ignore-not-found=true",
    ]
