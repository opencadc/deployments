"""Benchmark suite orchestration for lifecycle workflows."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List

from kueuer.benchmarks import DEFAULT_JOBSPEC_FILEPATH, benchmark
from kueuer.lifecycle.scenarios import apply_scenario, restore_scenario
from kueuer.lifecycle.shell import run_command
from kueuer.observe.collector import ObservationCollector


def _suite_commands(
    profile: str,
    counts_csv: str,
    namespace: str,
    localqueue: str,
    priority: str,
    artifacts_dir: str,
) -> List[str]:
    """Build the command transcript recorded in lifecycle suite reports."""
    return [
        (
            "kr benchmark performance "
            f"--profile {profile} --counts {counts_csv} "
            f"-n {namespace} -k {localqueue} -p {priority} "
            f"-o {artifacts_dir}"
        ),
        (
            "kr benchmark evictions "
            f"--profile {profile} -n {namespace} -k {localqueue} "
            "-p low -p medium -p high "
            f"-o {artifacts_dir}"
        ),
    ]


def run_suite(
    artifacts_dir: str,
    namespace: str,
    localqueue: str,
    priority: str,
    clusterqueue: str = "skaha-cluster-queue",
    profile: str = "local-safe",
    counts_csv: str = "2,4,8,16,32,64",
    scenario: str = "control",
    observe: bool = False,
    observe_interval_seconds: float = 5.0,
    observe_output_subdir: str = "observe",
    collector_factory: Callable[..., Any] = ObservationCollector,
    scenario_apply_fn: Callable[..., Dict[str, Any]] = apply_scenario,
    scenario_restore_fn: Callable[..., Dict[str, Any]] = restore_scenario,
    run_cmd: Callable[[List[str]], Any] = run_command,
    performance_runner: Callable[..., Any] = benchmark.performance,
    eviction_runner: Callable[..., Any] = benchmark.eviction,
) -> Dict[str, Any]:
    """Run performance and eviction benchmark suites with optional observation."""
    run_root = Path(artifacts_dir)
    performance_output = (run_root / "performance" / "performance.csv").as_posix()
    evictions_output = (run_root / "evictions" / "evictions.yaml").as_posix()
    commands = _suite_commands(
        profile=profile,
        counts_csv=counts_csv,
        namespace=namespace,
        localqueue=localqueue,
        priority=priority,
        artifacts_dir=artifacts_dir,
    )
    with tempfile.TemporaryDirectory(prefix="kueuer-scenario-") as scenario_tmp:
        scenario_context = scenario_apply_fn(
            scenario=scenario,
            output_dir=scenario_tmp,
            namespace=namespace,
            localqueue=localqueue,
            clusterqueue=clusterqueue,
            run_cmd=run_cmd,
        )
        scenario_errors = [str(item) for item in scenario_context.get("errors", []) if item]
        if scenario_errors:
            if scenario_context.get("applied"):
                restore_report = scenario_restore_fn(scenario_context, run_cmd=run_cmd) or {}
                scenario_context["restore"] = restore_report
                if restore_report.get("error"):
                    scenario_errors.append(str(restore_report["error"]))
            return {
                "ok": False,
                "performance_output": performance_output,
                "evictions_output": evictions_output,
                "commands": commands,
                "scenario": scenario_context,
                "errors": scenario_errors,
            }
        if scenario_context.get("applied"):
            commands.insert(0, f"kr lifecycle scenario {scenario}")
        effective_localqueue = str(scenario_context.get("localqueue") or localqueue)
        effective_clusterqueue = str(scenario_context.get("clusterqueue") or clusterqueue)

        collector = None
        observe_report: Dict[str, Any] = {}
        observe_error: Exception | None = None
        if observe:
            collector = collector_factory(
                namespace=namespace,
                interval_seconds=observe_interval_seconds,
            )
            collector.start()

        try:
            performance_runner(
                filepath=DEFAULT_JOBSPEC_FILEPATH,
                namespace=namespace,
                kueue=effective_localqueue,
                priority=priority,
                profile=profile,
                counts_csv=counts_csv,
                e0=1,
                exponent=6,
                duration=None,
                cores=None,
                ram=None,
                storage=None,
                output_dir=artifacts_dir,
                run_id="",
                wait=None,
                apply_chunk_size=25,
                apply_retries=2,
                apply_backoff=2.0,
            )
            eviction_runner(
                filepath=DEFAULT_JOBSPEC_FILEPATH,
                namespace=namespace,
                kueue=effective_localqueue,
                priorities=["low", "medium", "high"],
                profile=profile,
                jobs=None,
                cores=None,
                ram=None,
                storage=None,
                duration=None,
                output_dir=artifacts_dir,
                run_id="",
                apply_chunk_size=25,
                apply_retries=2,
                apply_backoff=2.0,
            )
        finally:
            if collector is not None:
                collector.stop()
            restore_report = scenario_restore_fn(scenario_context, run_cmd=run_cmd) or {}
            scenario_context["restore"] = restore_report
            if scenario_context.get("applied") and restore_report.get("error"):
                scenario_errors.append(str(restore_report["error"]))
            if collector is not None:
                observe_dir = Path(artifacts_dir) / observe_output_subdir
                try:
                    observe_report = collector.write_series(observe_dir.as_posix())
                except Exception as error:  # noqa: BLE001
                    observe_error = error

    if observe_error is not None:
        raise observe_error

    report: Dict[str, Any] = {
        "ok": not scenario_errors,
        "performance_output": performance_output,
        "evictions_output": evictions_output,
        "commands": commands,
        "scenario": scenario_context,
        "localqueue": effective_localqueue,
        "clusterqueue": effective_clusterqueue,
        "errors": scenario_errors,
    }
    if observe:
        report["observe"] = observe_report
    return report
