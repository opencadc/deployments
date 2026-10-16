"""Preflight checks for user-provided Kubernetes contexts."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from kueuer.lifecycle.shell import command_exists, run_command


def run_preflight(
    namespace: str,
    command_exists_fn: Callable[[str], bool] = command_exists,
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    """Verify kubectl, workload namespace, Job RBAC, and API connectivity.

    ``kubectl cluster-info`` is not namespace-scoped; we run
    ``kubectl -n <namespace> cluster-info`` so the workload namespace is set on
    the kubectl invocation. If that command fails but the namespace exists and
    ``can-i create jobs`` succeeds, preflight still passes with a warning so
    benchmarks can run when ``cluster-info`` flakes or is restricted.
    """
    errors: List[str] = []
    warnings: List[str] = []
    checks: Dict[str, bool] = {}

    for binary in ("kubectl",):
        ok = command_exists_fn(binary)
        checks[f"binary:{binary}"] = ok
        if not ok:
            errors.append(f"Required binary missing: {binary}")

    context = ""
    if errors:
        return {
            "ok": False,
            "context": context,
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
        }

    context_result = run_cmd(["kubectl", "config", "current-context"])
    checks["context"] = context_result.returncode == 0
    if context_result.returncode != 0:
        errors.append("kubectl config current-context failed")
    else:
        context = context_result.stdout.strip()

    if errors:
        return {
            "ok": False,
            "context": context,
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
        }

    ns_result = run_cmd(["kubectl", "get", "namespace", namespace])
    checks["namespace-exists"] = ns_result.returncode == 0
    if not checks["namespace-exists"]:
        errors.append(
            f"Workload namespace {namespace!r} not found or not accessible."
        )

    can_i_result = run_cmd(
        ["kubectl", "auth", "can-i", "create", "jobs", "-n", namespace]
    )
    checks["can-create-jobs"] = can_i_result.returncode == 0 and (
        "yes" in can_i_result.stdout.lower()
    )
    if not checks["can-create-jobs"]:
        errors.append("kubectl auth can-i create jobs failed")

    if errors:
        return {
            "ok": False,
            "context": context,
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
        }

    cluster_result = run_cmd(["kubectl", "-n", namespace, "cluster-info"])
    checks["cluster-info"] = cluster_result.returncode == 0
    if not checks["cluster-info"]:
        warnings.append(
            f"kubectl -n {namespace!r} cluster-info failed; continuing because "
            "the workload namespace exists and Job creation is allowed."
        )

    return {
        "ok": True,
        "context": context,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
