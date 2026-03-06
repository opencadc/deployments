"""Preflight checks for user-provided Kubernetes contexts."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from kueuer.lifecycle.shell import command_exists, run_command


def run_preflight(
    namespace: str,
    command_exists_fn: Callable[[str], bool] = command_exists,
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    errors: List[str] = []
    checks: Dict[str, bool] = {}

    for binary in ("kubectl",):
        ok = command_exists_fn(binary)
        checks[f"binary:{binary}"] = ok
        if not ok:
            errors.append(f"Required binary missing: {binary}")

    context = ""
    if not errors:
        context_result = run_cmd(["kubectl", "config", "current-context"])
        checks["context"] = context_result.returncode == 0
        if context_result.returncode != 0:
            errors.append("kubectl config current-context failed")
        else:
            context = context_result.stdout.strip()

        cluster_result = run_cmd(["kubectl", "cluster-info"])
        checks["cluster-info"] = cluster_result.returncode == 0
        if cluster_result.returncode != 0:
            errors.append("kubectl cluster-info failed")

        can_i_result = run_cmd(
            ["kubectl", "auth", "can-i", "create", "jobs", "-n", namespace]
        )
        checks["can-create-jobs"] = can_i_result.returncode == 0 and (
            "yes" in can_i_result.stdout.lower()
        )
        if not checks["can-create-jobs"]:
            errors.append("kubectl auth can-i create jobs failed")

    return {
        "ok": not errors,
        "context": context,
        "checks": checks,
        "errors": errors,
    }
