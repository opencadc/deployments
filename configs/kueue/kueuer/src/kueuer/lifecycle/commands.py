"""Internal workflow helpers and reusable CLI callables for benchmark runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List

import typer

from kueuer.lifecycle.collect import collect_outputs
from kueuer.lifecycle.kueue_validate import validate_kueue_health
from kueuer.lifecycle.models import append_step, load_or_init_manifest, save_manifest
from kueuer.lifecycle.preflight import run_preflight
from kueuer.lifecycle.queues import (
    default_config_paths,
    ensure_queues as ensure_queues_state,
)
from kueuer.lifecycle.shell import run_command
from kueuer.lifecycle.suite import run_benchmark_suite
from kueuer.lifecycle.teardown import cleanup_benchmark_jobs, cleanup_queues
from kueuer.utils.artifacts import default_run_id, resolve_run_input_path
from kueuer.utils.constants import (
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_CLUSTER_QUEUE,
    DEFAULT_LOCAL_QUEUE,
    DEFAULT_OBSERVATION_INTERVAL_SECONDS,
    DEFAULT_OBSERVATION_SUBDIR,
    DEFAULT_PRIORITY_CLASS,
    DEFAULT_WORKLOAD_NAMESPACE,
)

def _manifest_path(artifacts_dir: str, run_id: str) -> Path:
    """Resolve canonical manifest path and preserve legacy fallback behavior."""
    root = Path(artifacts_dir) / run_id
    canonical = root / "manifest.json"
    legacy = root / "run_manifest.json"
    if canonical.exists() or not legacy.exists():
        return canonical
    return legacy


def _resolve_suite_path(
    run_root: Path,
    domain: str,
    canonical_name: str,
    legacy_name: str,
) -> Path:
    """Resolve canonical lifecycle input path with legacy fallbacks."""
    legacy_candidates = [
        run_root / canonical_name,
        run_root / "suite" / canonical_name,
        run_root / "suite" / legacy_name,
    ]
    return resolve_run_input_path(
        run_root=run_root,
        domain=domain,
        filename=canonical_name,
        legacy_paths=legacy_candidates,
    )


def _write_manifest_step(
    artifacts_dir: str,
    run_id: str,
    step: str,
    ok: bool,
    details: Dict[str, Any],
) -> None:
    """Append one lifecycle step record to the run manifest."""
    path = _manifest_path(artifacts_dir, run_id)
    manifest = load_or_init_manifest(path, run_id)
    append_step(manifest, step, "ok" if ok else "failed", details)
    save_manifest(path, manifest)


def execute_e2e_pipeline(
    preflight_fn: Callable[[], Dict[str, Any]],
    validate_kueue_fn: Callable[[], Dict[str, Any]],
    ensure_queues_fn: Callable[[], Dict[str, Any]],
    run_suite_fn: Callable[[], Dict[str, Any]],
    collect_fn: Callable[[], Dict[str, Any]],
    teardown_fn: Callable[[], Dict[str, Any]],
) -> Dict[str, Any]:
    """Execute lifecycle steps in order and short-circuit on first failure."""
    ordered = [
        ("preflight", preflight_fn),
        ("validate-kueue", validate_kueue_fn),
        ("ensure-queues", ensure_queues_fn),
        ("run-suite", run_suite_fn),
        ("collect", collect_fn),
        ("teardown", teardown_fn),
    ]
    results: List[Dict[str, Any]] = []
    for name, fn in ordered:
        result = fn()
        results.append({"step": name, "result": result})
        if not result.get("ok", False):
            return {"ok": False, "failed_step": name, "steps": results}
    return {"ok": True, "steps": results}


def run_cluster_preflight(
    namespace: str,
    localqueue: str,
    clusterqueue: str,
    apply_if_missing: bool,
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    """Run access, Kueue, and queue checks as one preflight report."""
    access_report = run_preflight(namespace=namespace)
    kueue_report = validate_kueue_health()
    cluster_config, local_config = default_config_paths()
    queue_report = ensure_queues_state(
        namespace=namespace,
        localqueue=localqueue,
        clusterqueue=clusterqueue,
        apply_if_missing=apply_if_missing,
        cluster_config=cluster_config,
        local_config=local_config,
    )
    inventory = collect_kueue_inventory(run_cmd=run_cmd)
    queue_report["inventory"] = inventory
    queue_report["target_namespace"] = namespace
    queue_report["target_localqueue"] = localqueue
    queue_report["target_clusterqueue"] = clusterqueue
    errors = [
        *access_report.get("errors", []),
        *kueue_report.get("errors", []),
        *queue_report.get("errors", []),
    ]
    remediation = [
        *kueue_report.get("remediation", []),
        *queue_report.get("manual_commands", []),
    ]
    return {
        "ok": access_report["ok"] and kueue_report["ok"] and queue_report["ok"],
        "errors": errors,
        "remediation": remediation,
        "checks": {
            "access": access_report.get("checks", {}),
            "kueue": kueue_report,
            "queues": queue_report,
        },
        "context": access_report.get("context", ""),
    }


def _read_name_lines(command: List[str], run_cmd: Callable[[List[str]], Any]) -> List[str]:
    """Return stripped `kubectl get -o name` lines or an empty list on failure."""
    result = run_cmd(command)
    if result.returncode != 0:
        return []
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def collect_kueue_inventory(
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, List[str]]:
    """Collect a lightweight inventory of Kueue queue objects."""
    return {
        "clusterqueues": _read_name_lines(
            ["kubectl", "get", "clusterqueue", "-o", "name"],
            run_cmd=run_cmd,
        ),
        "localqueues": _read_name_lines(
            ["kubectl", "get", "localqueue", "-A", "-o", "name"],
            run_cmd=run_cmd,
        ),
        "workloadpriorityclasses": _read_name_lines(
            ["kubectl", "get", "workloadpriorityclass", "-o", "name"],
            run_cmd=run_cmd,
        ),
    }


def _echo_list(title: str, items: List[str]) -> None:
    typer.echo(f"{title}:")
    if not items:
        typer.echo("  - none found")
        return
    for item in items:
        typer.echo(f"  - {item}")


def print_preflight_report(report: Dict[str, Any]) -> None:
    """Render a verbose preflight report for humans."""
    typer.echo(f"Context: {report.get('context', '') or 'unknown'}")

    access = report.get("checks", {}).get("access", {})
    typer.echo("Access checks:")
    typer.echo(f"  - kubectl installed: {'yes' if access.get('binary:kubectl') else 'no'}")
    typer.echo(f"  - current context readable: {'yes' if access.get('context') else 'no'}")
    typer.echo(f"  - cluster reachable: {'yes' if access.get('cluster-info') else 'no'}")
    typer.echo(
        f"  - can create jobs: {'yes' if access.get('can-create-jobs') else 'no'}"
    )

    kueue = report.get("checks", {}).get("kueue", {})
    typer.echo("Kueue health:")
    typer.echo(f"  - namespace: {kueue.get('namespace', 'kueue-system')}")
    typer.echo(f"  - available replicas: {kueue.get('available_replicas', 0)}")
    _echo_list("Controller pods", list(kueue.get("pods", [])))

    queues = report.get("checks", {}).get("queues", {})
    typer.echo("Queue checks:")
    typer.echo(f"  - namespace: {queues.get('target_namespace', '')}")
    typer.echo(f"  - target LocalQueue: {queues.get('target_localqueue', '')}")
    typer.echo(f"  - target ClusterQueue: {queues.get('target_clusterqueue', '')}")
    typer.echo(f"  - auto-applied missing config: {'yes' if queues.get('applied') else 'no'}")
    if queues.get("missing"):
        typer.echo(f"  - missing checks: {', '.join(queues['missing'])}")
    inventory = queues.get("inventory", {})
    _echo_list("ClusterQueues", list(inventory.get("clusterqueues", [])))
    _echo_list("LocalQueues", list(inventory.get("localqueues", [])))
    _echo_list("PriorityClasses", list(inventory.get("workloadpriorityclasses", [])))

    if report.get("errors"):
        typer.echo("Errors:")
        for error in report["errors"]:
            typer.echo(f"  - {error}")
    if report.get("remediation"):
        typer.echo("Remediation:")
        for item in report["remediation"]:
            typer.echo(f"  - {item}")


def preflight(
    artifacts_dir: str = typer.Option(DEFAULT_ARTIFACTS_DIR, "--output-dir"),
    run_id: str = typer.Option("", "--run-id"),
    namespace: str = typer.Option(DEFAULT_WORKLOAD_NAMESPACE, "--namespace"),
    localqueue: str = typer.Option(DEFAULT_LOCAL_QUEUE, "--localqueue"),
    clusterqueue: str = typer.Option(DEFAULT_CLUSTER_QUEUE, "--clusterqueue"),
    apply_if_missing: bool = typer.Option(
        True,
        "--apply-if-missing/--no-apply-if-missing",
        help="Attempt to apply queue YAML when objects are missing.",
    ),
) -> None:
    """Run access, Kueue health, and queue readiness checks."""
    effective = run_id or default_run_id()
    report = run_cluster_preflight(
        namespace=namespace,
        localqueue=localqueue,
        clusterqueue=clusterqueue,
        apply_if_missing=apply_if_missing,
    )
    _write_manifest_step(artifacts_dir, effective, "preflight", report["ok"], report)
    typer.echo(f"preflight {'ok' if report['ok'] else 'failed'} for run {effective}")
    print_preflight_report(report)
    if not report["ok"]:
        raise typer.Exit(code=1)


def validate_kueue(
    artifacts_dir: str = typer.Option(DEFAULT_ARTIFACTS_DIR, "--output-dir"),
    run_id: str = typer.Option("", "--run-id"),
) -> None:
    """Validate Kueue control-plane readiness and persist the step report."""
    effective = run_id or default_run_id()
    report = validate_kueue_health()
    _write_manifest_step(
        artifacts_dir,
        effective,
        "validate-kueue",
        report["ok"],
        report,
    )
    typer.echo(
        f"validate-kueue {'ok' if report['ok'] else 'failed'} for run {effective}"
    )
    if not report["ok"]:
        for error in report["errors"]:
            typer.echo(f"- {error}")
        for cmd in report["remediation"]:
            typer.echo(f"  {cmd}")
        raise typer.Exit(code=1)


def ensure_queues(
    artifacts_dir: str = typer.Option(DEFAULT_ARTIFACTS_DIR, "--output-dir"),
    run_id: str = typer.Option("", "--run-id"),
    namespace: str = typer.Option(DEFAULT_WORKLOAD_NAMESPACE, "--namespace"),
    localqueue: str = typer.Option(DEFAULT_LOCAL_QUEUE, "--localqueue"),
    clusterqueue: str = typer.Option(DEFAULT_CLUSTER_QUEUE, "--clusterqueue"),
    apply_if_missing: bool = typer.Option(
        True,
        "--apply-if-missing/--no-apply-if-missing",
        help="Attempt to apply queue YAML when objects are missing.",
    ),
) -> None:
    """Ensure required queue objects exist and persist the step report."""
    effective = run_id or default_run_id()
    cluster_config, local_config = default_config_paths()
    report = ensure_queues_state(
        namespace=namespace,
        localqueue=localqueue,
        clusterqueue=clusterqueue,
        apply_if_missing=apply_if_missing,
        cluster_config=cluster_config,
        local_config=local_config,
    )
    _write_manifest_step(
        artifacts_dir,
        effective,
        "ensure-queues",
        report["ok"],
        report,
    )
    typer.echo(f"ensure-queues {'ok' if report['ok'] else 'failed'} for run {effective}")
    if not report["ok"]:
        for error in report["errors"]:
            typer.echo(f"- {error}")
        if report["manual_commands"]:
            typer.echo("Manual remediation:")
            for cmd in report["manual_commands"]:
                typer.echo(f"  {cmd}")
        raise typer.Exit(code=1)


def collect(
    artifacts_dir: str = typer.Option(DEFAULT_ARTIFACTS_DIR, "--output-dir"),
    run_id: str = typer.Option("", "--run-id"),
    performance_csv: str = typer.Option("", "--performance-csv"),
    evictions_yaml: str = typer.Option("", "--evictions-yaml"),
) -> None:
    """Collect plots and summary artifacts and persist the step report."""
    effective = run_id or default_run_id()
    run_root = Path(artifacts_dir) / effective
    perf_path = performance_csv or _resolve_suite_path(
        run_root, "performance", "performance.csv", "performance_results.csv"
    ).as_posix()
    evict_path = evictions_yaml or _resolve_suite_path(
        run_root, "evictions", "evictions.yaml", "evictions.yaml"
    ).as_posix()
    report = collect_outputs(
        performance_csv=perf_path,
        evictions_yaml=evict_path,
        output_dir=run_root.as_posix(),
    )
    collect_ok = bool(report.get("ok", True))
    _write_manifest_step(artifacts_dir, effective, "collect", collect_ok, report)
    typer.echo(f"collect {'ok' if collect_ok else 'failed'} for run {effective}")
    if not collect_ok:
        raise typer.Exit(code=1)
    typer.echo(f"Artifacts written under {run_root.as_posix()}")
    typer.echo(f"uv run kr plot performance {perf_path} --show")
    typer.echo(f"uv run kr plot evictions {evict_path} --show")
    observe_timeseries = run_root / "observe" / "timeseries.csv"
    if observe_timeseries.exists():
        typer.echo(f"uv run kr plot observations {observe_timeseries.as_posix()} --show")
    if report.get("performance_plot_dir"):
        typer.echo(f"Performance plots: {report['performance_plot_dir']}")
    if report.get("evictions_plot_dir"):
        typer.echo(f"Eviction plots: {report['evictions_plot_dir']}")
    if report.get("observe_plot_dir"):
        typer.echo(f"Observation plots: {report['observe_plot_dir']}")
    if report.get("observe_report_json"):
        typer.echo(f"Observation report: {report['observe_report_json']}")
    if report.get("report_md"):
        typer.echo(f"Run report: {report['report_md']}")


def teardown(
    artifacts_dir: str = typer.Option(DEFAULT_ARTIFACTS_DIR, "--output-dir"),
    run_id: str = typer.Option("", "--run-id"),
    namespace: str = typer.Option(DEFAULT_WORKLOAD_NAMESPACE, "--namespace"),
    prefixes: List[str] = typer.Option(  # noqa: B008
        ["direct-", "kueue-", "kueue-eviction"],
        "--prefix",
        help="Job prefixes to delete; repeat flag for multiple values.",
    ),
    delete_queues: bool = typer.Option(
        False,
        "--delete-queues",
        help="Also delete queue objects defined in dev YAML.",
    ),
) -> None:
    """Delete benchmark jobs (and optionally queues) and persist the step report."""
    effective = run_id or default_run_id()
    cleanup_report = cleanup_benchmark_jobs(namespace=namespace, prefixes=prefixes)
    queues_report = {"ok": True, "results": []}
    if delete_queues:
        queues_report = cleanup_queues()
    report = {"jobs": cleanup_report, "queues": queues_report}

    ok = cleanup_report["ok"] and queues_report["ok"]
    _write_manifest_step(artifacts_dir, effective, "teardown", ok, report)
    typer.echo(f"teardown {'ok' if ok else 'failed'} for run {effective}")
    if not ok:
        if cleanup_report["remaining"]:
            typer.echo("Remaining benchmark jobs:")
            for name in cleanup_report["remaining"]:
                typer.echo(f"- {name}")
        raise typer.Exit(code=1)


def run_benchmark_e2e(
    artifacts_dir: str,
    run_id: str,
    namespace: str,
    localqueue: str,
    clusterqueue: str,
    priority: str,
    scenario: str,
    performance_options: Dict[str, Any],
    eviction_options: Dict[str, Any],
    observe: bool = True,
    observe_interval_seconds: float = DEFAULT_OBSERVATION_INTERVAL_SECONDS,
    observe_output_subdir: str = DEFAULT_OBSERVATION_SUBDIR,
    skip_queue_apply: bool = False,
    skip_teardown: bool = False,
) -> Dict[str, Any]:
    """Run the internal benchmark end-to-end workflow and persist its manifest."""
    effective = run_id or default_run_id()
    run_root = Path(artifacts_dir) / effective
    cluster_config, local_config = default_config_paths()

    pipeline_report = execute_e2e_pipeline(
        preflight_fn=lambda: run_preflight(namespace=namespace),
        validate_kueue_fn=lambda: validate_kueue_health(),
        ensure_queues_fn=lambda: ensure_queues_state(
            namespace=namespace,
            localqueue=localqueue,
            clusterqueue=clusterqueue,
            apply_if_missing=not skip_queue_apply,
            cluster_config=cluster_config,
            local_config=local_config,
        ),
        run_suite_fn=lambda: run_benchmark_suite(
            artifacts_dir=run_root.as_posix(),
            namespace=namespace,
            localqueue=localqueue,
            clusterqueue=clusterqueue,
            priority=priority,
            performance_options=performance_options,
            eviction_options=eviction_options,
            scenario=scenario,
            observe=observe,
            observe_interval_seconds=observe_interval_seconds,
            observe_output_subdir=observe_output_subdir,
        ),
        collect_fn=lambda: collect_outputs(
            performance_csv=_resolve_suite_path(
                run_root, "performance", "performance.csv", "performance_results.csv"
            ).as_posix(),
            evictions_yaml=_resolve_suite_path(
                run_root, "evictions", "evictions.yaml", "evictions.yaml"
            ).as_posix(),
            output_dir=run_root.as_posix(),
        ),
        teardown_fn=(
            (lambda: {"ok": True, "skipped": True})
            if skip_teardown
            else (
                lambda: cleanup_benchmark_jobs(
                    namespace=namespace,
                    prefixes=["direct-", "kueue-", "kueue-eviction"],
                )
            )
        ),
    )

    _write_manifest_step(
        artifacts_dir,
        effective,
        "e2e",
        bool(pipeline_report.get("ok", False)),
        pipeline_report,
    )

    if not pipeline_report["ok"]:
        return {
            **pipeline_report,
            "run_id": effective,
            "run_root": run_root.as_posix(),
        }

    perf_path = _resolve_suite_path(
        run_root, "performance", "performance.csv", "performance_results.csv"
    ).as_posix()
    evict_path = _resolve_suite_path(
        run_root, "evictions", "evictions.yaml", "evictions.yaml"
    ).as_posix()

    report: Dict[str, Any] = {
        **pipeline_report,
        "run_id": effective,
        "run_root": run_root.as_posix(),
        "performance_csv": perf_path,
        "evictions_yaml": evict_path,
    }
    observe_timeseries = run_root / "observe" / "timeseries.csv"
    if observe_timeseries.exists():
        report["observe_timeseries"] = observe_timeseries.as_posix()
    return report
