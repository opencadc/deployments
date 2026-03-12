"""Queue readiness checks and conditional apply logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from kueuer.lifecycle.shell import run_command

CLUSTER_CONFIG = "dev/clusterQueue.config.yaml"
LOCAL_CONFIG = "dev/localQueue.config.yaml"


def default_config_paths() -> Tuple[str, str]:
    root = Path(__file__).resolve().parents[4]
    return (
        (root / CLUSTER_CONFIG).as_posix(),
        (root / LOCAL_CONFIG).as_posix(),
    )


def _check_objects(
    namespace: str,
    localqueue: str,
    clusterqueue: str,
    run_cmd: Callable[[List[str]], Any],
) -> Tuple[List[str], List[str]]:
    checks = [
        (
            "clusterqueue",
            ["kubectl", "get", "clusterqueue", clusterqueue],
        ),
        (
            "localqueue",
            ["kubectl", "get", "localqueue", "-n", namespace, localqueue],
        ),
        ("priority-low", ["kubectl", "get", "workloadpriorityclass", "low"]),
        ("priority-medium", ["kubectl", "get", "workloadpriorityclass", "medium"]),
        ("priority-high", ["kubectl", "get", "workloadpriorityclass", "high"]),
    ]
    missing: List[str] = []
    errors: List[str] = []
    for name, cmd in checks:
        result = run_cmd(cmd)
        if result.returncode != 0:
            missing.append(name)
            errors.append(f"Missing or invalid {name}: {' '.join(cmd)}")
    return missing, errors


def ensure_queues(
    namespace: str,
    localqueue: str,
    clusterqueue: str,
    apply_if_missing: bool = True,
    cluster_config: str = CLUSTER_CONFIG,
    local_config: str = LOCAL_CONFIG,
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    missing, errors = _check_objects(namespace, localqueue, clusterqueue, run_cmd)
    manual_commands = [
        f"kubectl apply -f {cluster_config}",
        f"kubectl apply -f {local_config}",
        f"kubectl get clusterqueue {clusterqueue}",
        f"kubectl get localqueue -n {namespace} {localqueue}",
    ]
    if not missing:
        return {
            "ok": True,
            "missing": [],
            "errors": [],
            "manual_commands": [],
            "applied": False,
        }

    applied = False
    if apply_if_missing:
        apply_cluster = run_cmd(["kubectl", "apply", "-f", cluster_config])
        apply_local = run_cmd(["kubectl", "apply", "-f", local_config])
        applied = apply_cluster.returncode == 0 and apply_local.returncode == 0
        missing, retry_errors = _check_objects(namespace, localqueue, clusterqueue, run_cmd)
        errors.extend(retry_errors)

    ok = len(missing) == 0
    return {
        "ok": ok,
        "missing": missing,
        "errors": errors,
        "manual_commands": [] if ok else manual_commands,
        "applied": applied,
    }
