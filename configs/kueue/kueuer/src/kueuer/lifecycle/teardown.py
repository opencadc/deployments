"""Teardown helpers for lifecycle workflows."""

from __future__ import annotations

from time import sleep
from typing import Any, Callable, Dict, List

from kubernetes import client, config

from kueuer.benchmarks import k8s
from kueuer.lifecycle.queues import default_config_paths
from kueuer.lifecycle.shell import run_command


def list_job_names(namespace: str) -> List[str]:
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    jobs = batch_v1.list_namespaced_job(namespace=namespace).items
    return [job.metadata.name for job in jobs if job.metadata and job.metadata.name]


def cleanup_benchmark_jobs(
    namespace: str,
    prefixes: List[str],
    delete_fn: Callable[[str, str], int] = k8s.delete_jobs,
    list_jobs_fn: Callable[[str], List[str]] = list_job_names,
    verify_wait_seconds: int = 10,
) -> Dict[str, Any]:
    deleted_counts: Dict[str, int] = {}
    total_deleted = 0
    for prefix in prefixes:
        count = int(delete_fn(namespace, prefix))
        deleted_counts[prefix] = count
        total_deleted += count

    remaining: List[str] = []
    for _ in range(max(verify_wait_seconds, 0) + 1):
        current = list_jobs_fn(namespace)
        remaining = [name for name in current if any(name.startswith(p) for p in prefixes)]
        if not remaining:
            break
        sleep(1)
    return {
        "ok": len(remaining) == 0,
        "deleted_counts": deleted_counts,
        "total_deleted": total_deleted,
        "remaining": remaining,
    }


def cleanup_queues(run_cmd: Callable[[List[str]], Any] = run_command) -> Dict[str, Any]:
    cluster_config, local_config = default_config_paths()
    commands = [
        ["kubectl", "delete", "-f", local_config, "--ignore-not-found=true"],
        ["kubectl", "delete", "-f", cluster_config, "--ignore-not-found=true"],
    ]
    results = []
    for command in commands:
        res = run_cmd(command)
        results.append({"command": " ".join(command), "returncode": res.returncode})
    return {"ok": all(item["returncode"] == 0 for item in results), "results": results}
