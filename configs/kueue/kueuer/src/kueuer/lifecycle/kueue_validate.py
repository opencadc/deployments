"""Validation checks for Kueue installation and health."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from kueuer.lifecycle.shell import run_command


def validate_kueue_health(
    namespace: str = "kueue-system",
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    errors: List[str] = []
    remediation: List[str] = []

    namespace_cmd = ["kubectl", "get", "namespace", namespace]
    namespace_result = run_cmd(namespace_cmd)
    if namespace_result.returncode != 0:
        errors.append(f"Namespace {namespace} not found.")
        remediation.append("Install Kueue and ensure namespace kueue-system exists.")
        remediation.append("kubectl get namespace kueue-system")
        return {"ok": False, "errors": errors, "remediation": remediation}

    deploy_cmd = [
        "kubectl",
        "get",
        "deploy",
        "-n",
        namespace,
        "kueue-controller-manager",
        "-o",
        "jsonpath={.status.availableReplicas}",
    ]
    deploy_result = run_cmd(deploy_cmd)
    available = (deploy_result.stdout or "").strip()
    try:
        available_count = int(available) if available else 0
    except ValueError:
        available_count = 0
    if deploy_result.returncode != 0 or available_count < 1:
        errors.append("Kueue controller deployment is not available.")
        remediation.append("kubectl get deploy -n kueue-system")

    pods_cmd = ["kubectl", "get", "pods", "-n", namespace, "--no-headers"]
    pods_result = run_cmd(pods_cmd)
    pods_stdout = (pods_result.stdout or "").strip()
    pod_lines = [line for line in pods_stdout.splitlines() if line.strip()]
    has_running = False
    for line in pod_lines:
        if "kueue-controller-manager" not in line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        ready = parts[1]
        phase = parts[2]
        if "/" not in ready:
            continue
        ready_count, total_count = ready.split("/", maxsplit=1)
        if phase == "Running" and ready_count == total_count:
            has_running = True
            break
    if pods_result.returncode != 0 or not has_running:
        errors.append("Kueue controller pods are not healthy.")
        remediation.append("kubectl get pods -n kueue-system")
        remediation.append("kubectl describe pods -n kueue-system")

    return {
        "ok": not errors,
        "errors": errors,
        "remediation": remediation,
        "namespace": namespace,
        "available_replicas": available_count,
        "pods": pod_lines,
    }
