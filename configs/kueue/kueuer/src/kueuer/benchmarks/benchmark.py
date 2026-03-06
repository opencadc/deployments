"""Benchmark module for comparing Kubernetes job execution with and without Kueue."""

import time
from click import get_current_context
from click.core import Context, ParameterSource
from datetime import datetime
from time import sleep
from typing import Any, Dict, List, Optional

import typer
from kubernetes import client, config

from kueuer.benchmarks import DEFAULT_JOBSPEC_FILEPATH, analyze, k8s, track
from kueuer.utils import io
from kueuer.utils.artifacts import resolve_output_root, default_run_id
from kueuer.utils.logging import logger

benchmark_cli: typer.Typer = typer.Typer(help="Launch Benchmarks")

PERFORMANCE_PROFILES: Dict[str, Dict[str, float]] = {
    "local-safe": {
        "duration": 5,
        "cores": 0.1,
        "ram": 0.25,
        "storage": 0.25,
        "wait": 5,
    },
    "cluster-scale": {
        "duration": 1,
        "cores": 1.0,
        "ram": 1.0,
        "storage": 1.0,
        "wait": 60,
    },
}

EVICTION_PROFILES: Dict[str, Dict[str, float]] = {
    "local-safe": {
        "jobs": 8,
        "cores": 2.0,
        "ram": 2.0,
        "storage": 2.0,
        "duration": 60,
    },
    "cluster-scale": {
        "jobs": 8,
        "cores": 8.0,
        "ram": 8.0,
        "storage": 8.0,
        "duration": 120,
    },
}

def _default_run_id() -> str:
    """Expose the default run-id generator for tests and CLI helpers."""
    return default_run_id()


def _normalize_profile_name(profile: str) -> str:
    """Return the canonical profile name."""
    return profile


def _resolve_value(value: Optional[Any], default: float, caster: Any) -> Any:
    """Resolve an optional CLI override value against a profile default."""
    return caster(default if value is None else value)


def _cli_override_or_none(
    ctx: Context | None,
    name: str,
    value: Any,
) -> Any:
    """Return CLI overrides only when the user explicitly set the option."""
    if ctx is None:
        return value
    if ctx.get_parameter_source(name) == ParameterSource.COMMANDLINE:
        return value
    return None


def _performance_output_paths(output_dir: str, run_id: str) -> tuple[str, str, str]:
    effective_input = run_id or (_default_run_id() if output_dir == "artifacts" else "")
    root, effective_run_id = resolve_output_root(
        output_dir=output_dir,
        run_id=effective_input,
    )
    root.mkdir(parents=True, exist_ok=True)
    return (
        root.as_posix(),
        (root / "performance.csv").as_posix(),
        effective_run_id,
    )


def _eviction_output_paths(output_dir: str, run_id: str) -> tuple[str, str, str]:
    effective_input = run_id or (_default_run_id() if output_dir == "artifacts" else "")
    root, effective_run_id = resolve_output_root(
        output_dir=output_dir,
        run_id=effective_input,
    )
    root.mkdir(parents=True, exist_ok=True)
    return (
        root.as_posix(),
        (root / "evictions.yaml").as_posix(),
        effective_run_id,
    )


def parse_counts_csv(value: str) -> List[int]:
    """Parse and normalize comma-separated job counts."""
    counts: List[int] = []
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        parsed = int(item)
        if parsed <= 0:
            raise ValueError("counts must be positive integers")
        counts.append(parsed)
    if not counts:
        raise ValueError("at least one job count is required")
    return sorted(set(counts))


def resolve_performance_parameters(
    profile: str,
    duration: Optional[int],
    cores: Optional[float],
    ram: Optional[float],
    storage: Optional[float],
    wait: Optional[int],
) -> Dict[str, float]:
    """Resolve performance benchmark parameters using profile defaults."""
    profile = _normalize_profile_name(profile)
    if profile not in PERFORMANCE_PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    defaults = PERFORMANCE_PROFILES[profile]
    resolved_duration = _resolve_value(duration, defaults["duration"], int)
    resolved_cores = _resolve_value(cores, defaults["cores"], float)
    resolved_ram = _resolve_value(ram, defaults["ram"], float)
    resolved_storage = _resolve_value(storage, defaults["storage"], float)
    resolved_wait = _resolve_value(wait, defaults["wait"], int)
    if resolved_duration <= 0 or resolved_wait < 0:
        raise ValueError("duration must be > 0 and wait must be >= 0")
    if resolved_cores <= 0 or resolved_ram <= 0 or resolved_storage <= 0:
        raise ValueError("cores, ram, and storage must be > 0")
    return {
        "duration": float(resolved_duration),
        "cores": resolved_cores,
        "ram": resolved_ram,
        "storage": resolved_storage,
        "wait": float(resolved_wait),
    }


def resolve_eviction_parameters(
    profile: str,
    jobs: Optional[int],
    cores: Optional[float],
    ram: Optional[float],
    storage: Optional[float],
    duration: Optional[int],
) -> Dict[str, float]:
    """Resolve eviction benchmark parameters using profile defaults."""
    profile = _normalize_profile_name(profile)
    if profile not in EVICTION_PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    defaults = EVICTION_PROFILES[profile]
    resolved_jobs = _resolve_value(jobs, defaults["jobs"], int)
    resolved_cores = _resolve_value(cores, defaults["cores"], float)
    resolved_ram = _resolve_value(ram, defaults["ram"], float)
    resolved_storage = _resolve_value(storage, defaults["storage"], float)
    resolved_duration = _resolve_value(duration, defaults["duration"], int)
    if resolved_jobs <= 0 or resolved_duration <= 0:
        raise ValueError("jobs and duration must be > 0")
    if resolved_cores <= 0 or resolved_ram <= 0 or resolved_storage <= 0:
        raise ValueError("cores, ram, and storage must be > 0")
    return {
        "jobs": float(resolved_jobs),
        "cores": resolved_cores,
        "ram": resolved_ram,
        "storage": resolved_storage,
        "duration": float(resolved_duration),
    }


def experiment(
    count: int,
    duration: int,
    cores: float,
    ram: float,
    storage: float,
    namespace: str,
    filepath: str,
    use_kueue: bool = False,
    kueue: Optional[str] = None,
    priority: Optional[str] = None,
    apply_chunk_size: int = 25,
    apply_retries: int = 2,
    apply_backoff: float = 2.0,
) -> Dict[str, Any]:
    """Run a single experiment with the specified configuration.

    Args:
        job_count: Number of jobs to create
        job_duration: Duration of each job in seconds
        cores: Number of CPU cores per job
        ram: RAM in GB per job
        storage: Storage in GB per job
        namespace: Kubernetes namespace
        template_file: Path to the job template file
        use_kueue: Whether to use Kueue for job queueing
        kueue_queue: Kueue queue name (required if use_kueue is True)
        kueue_priority: Kueue priority (optional, used if use_kueue is True)

    Returns:
        Dict containing experiment results and timing information
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    prefix = f"{'kueue' if use_kueue else 'direct'}-{timestamp}-{count}"
    logger.info("=" * 80)
    logger.info("Starting experiment with %d jobs, duration %ds", count, duration)
    logger.info("Configuration: %s", "With Kueue" if use_kueue else "Direct Kubernetes")
    if use_kueue:
        logger.info("Kueue Queue: %s, Priority: %s", kueue, priority)
    logger.info(
        "Namespace: %s, Cores: %s, RAM: %sGB, Storage: %sGB",
        namespace,
        cores,
        ram,
        storage,
    )
    logger.info("=" * 80)

    # Start measuring time
    start_time = time.time()

    # Execute the launcher
    restarts_before = k8s.kueue_controller_restarts()
    submission = k8s.run(
        filepath=filepath,
        namespace=namespace,
        prefix=prefix,
        jobs=count,
        duration=duration,
        cores=cores,
        ram=ram,
        storage=storage,
        kueue=kueue,
        priority=priority,
        apply_chunk_size=apply_chunk_size,
        apply_retries=apply_retries,
        apply_backoff=apply_backoff,
    )

    # Track jobs to completion and get timing statistics
    logger.info("Jobs launched, tracking completion...")
    times = track.jobs(namespace, prefix, "Complete")
    logger.info("All jobs completed, computing statistics...")
    stats = track.compute_statistics(times)
    pod_outcomes = k8s.collect_pod_outcomes(namespace, prefix)
    job_outcomes = k8s.collect_job_outcomes(namespace, prefix)
    restarts_after = k8s.kueue_controller_restarts()

    # End time measurement
    end_time = time.time()
    total_execution_time = end_time - start_time

    # Prepare result
    result: Dict[str, Optional[Any]] = {
        "timestamp": timestamp,
        "job_count": count,
        "use_kueue": use_kueue,
        "kueue_queue": kueue if use_kueue else None,
        "kueue_priority": priority if use_kueue else None,
        "job_duration": duration,
        "cores": cores,
        "ram": ram,
        "storage": storage,
        "namespace": namespace,
        "completed_jobs_tracked": len(times),
        "completion_ratio": (len(times) / count) if count else 0.0,
        "total_execution_time": total_execution_time,
        # Extract values from stats dictionary with fallbacks to None
        "first_creation_time": stats.get("first_creation_time"),
        "last_creation_time": stats.get("last_creation_time"),
        "first_completion_time": stats.get("first_completion_time"),
        "last_completion_time": stats.get("last_completion_time"),
        "avg_time_from_creation_completion": stats.get(
            "avg_time_from_creation_completion"
        ),
        "total_time_from_first_creation_to_last_completion": stats.get(
            "total_time_from_first_creation_to_last_completion"
        ),
        "median_time_from_creation_completion": stats.get(
            "median_time_from_creation_completion"
        ),
        "std_dev_time_from_creation_completion": stats.get(
            "std_dev_time_from_creation_completion"
        ),
        "kueue_controller_restarts_before": restarts_before,
        "kueue_controller_restarts_after": restarts_after,
        "kueue_controller_restarts_delta": restarts_after - restarts_before,
    }
    result.update({f"submission_{key}": value for key, value in submission.items()})
    result.update(pod_outcomes)
    result.update(job_outcomes)

    logger.info("Experiment completed in %.2fs", total_execution_time)
    total = result["total_time_from_first_creation_to_last_completion"]
    if total is not None:
        logger.info("Total time from first creation to last completion: %.2fs", total)

    # Cleanup jobs
    logger.info("Cleaning up jobs...")
    k8s.delete_jobs(namespace, prefix)
    return result


def benchmark(
    counts: List[int],
    duration: int,
    cores: float,
    ram: float,
    storage: float,
    namespace: str,
    filepath: str,
    kueue: Optional[str],
    priority: Optional[str],
    resultsfile: str,
    wait: int,
    apply_chunk_size: int,
    apply_retries: int,
    apply_backoff: float,
) -> List[Dict[str, Any]]:
    """
    Run a complete benchmark comparing direct Kubernetes jobs vs Kueue jobs.

    Args:
        job_counts: List of job counts to test
        job_duration: Duration of each job in seconds
        cores: Number of CPU cores per job
        ram: RAM in GB per job
        storage: Storage in GB per job
        namespace: Kubernetes namespace
        template_file: Path to the job template file
        kueue_queue: Kueue queue name
        kueue_priority: Kueue priority
        results_file: Path to save results CSV
        wait_between_runs: Time to wait between experiment runs in seconds

    Returns:
        List of dictionaries containing all experiment results
    """
    results: List[Dict[str, Optional[Any]]] = []

    # Ensure job counts are sorted
    counts = sorted(counts)

    for count in counts:
        # Run without Kueue
        result = experiment(
            count=count,
            duration=duration,
            cores=cores,
            ram=ram,
            storage=storage,
            namespace=namespace,
            filepath=filepath,
            use_kueue=False,
            apply_chunk_size=apply_chunk_size,
            apply_retries=apply_retries,
            apply_backoff=apply_backoff,
        )
        results.append(result)

        # Save intermediate results
        io.save_performance_to_csv(results, resultsfile)

        # Wait between experiments
        logger.info("Waiting %ss before next experiment...", wait)
        sleep(wait)

        # Run with Kueue
        kueue_result = experiment(
            count=count,
            duration=duration,
            cores=cores,
            ram=ram,
            storage=storage,
            namespace=namespace,
            filepath=filepath,
            use_kueue=True,
            kueue=kueue,
            priority=priority,
            apply_chunk_size=apply_chunk_size,
            apply_retries=apply_retries,
            apply_backoff=apply_backoff,
        )
        results.append(kueue_result)

        # Save intermediate results
        io.save_performance_to_csv(results, resultsfile)

        # Wait between experiments
        if count != counts[-1]:  # Don't wait after the last experiment
            logger.info("Waiting %s seconds before next experiment...", wait)
            sleep(wait)

    return results


@benchmark_cli.command("performance")
def performance(
    filepath: str = (
        typer.Option(
            DEFAULT_JOBSPEC_FILEPATH, "-f", "--filepath", help="K8s job template."
        )
    ),
    namespace: str = (
        typer.Option(
            "skaha-workload", "-n", "--namespace", help="Namespace to launch jobs in."
        )
    ),
    kueue: str = (
        typer.Option(
            "skaha-local-queue",
            "-k",
            "--kueue",
            help="Local kueue to launch jobs in.",
        )
    ),
    priority: str = (
        typer.Option(
            "high", "-p", "--priority", help="Kueue priority to launch jobs with."
        )
    ),
    profile: str = typer.Option(
        "local-safe",
        "--profile",
        help="Benchmark profile defaults. Use local-safe for fast local runs.",
    ),
    counts_csv: Optional[str] = typer.Option(
        "2,4,8,16,32,64",
        "--counts",
        help="Comma-separated explicit job counts. Leave blank to use exponent range.",
    ),
    e0: int = typer.Option(
        1,
        "-el",
        "--exponent-lower",
        help="Lower bound exponent for job count range [2^el, ..., 2^eh].",
    ),
    exponent: int = typer.Option(
        3,
        "-eh",
        "--exponent-higher",
        help="Higher bound exponent for job count range [2^el, ..., 2^eh].",
    ),
    duration: int = (
        typer.Option(5, "-d", "--duration", help="Duration for each job in seconds.")
    ),
    cores: float = (
        typer.Option(
            0.1, "-c", "--cores", help="Number of CPU cores to allocate to each job."
        )
    ),
    ram: float = (
        typer.Option(
            0.25, "-r", "--ram", help="Amount of RAM to allocate to each job in GB."
        )
    ),
    storage: float = (
        typer.Option(
            0.25,
            "-s",
            "--storage",
            help="Amount of ephemeral-storage to allocate to each job in GB.",
        )
    ),
    output_dir: str = typer.Option(
        "artifacts",
        "-o",
        "--output-dir",
        help="Directory where benchmark artifacts are written.",
    ),
    run_id: str = typer.Option(
        "",
        "--run-id",
        help="Run identifier used under the default artifacts directory.",
    ),
    wait: int = (
        typer.Option(5, "-w", "--wait", help="Time to wait between experiments.")
    ),
    apply_chunk_size: int = typer.Option(
        25, "--apply-chunk-size", help="Number of jobs per kubectl apply chunk."
    ),
    apply_retries: int = typer.Option(
        2, "--apply-retries", help="Retries per apply chunk on kubectl failures."
    ),
    apply_backoff: float = typer.Option(
        2.0,
        "--apply-backoff",
        help="Backoff base (seconds) between apply retries.",
    ),
):
    """Compare native K8s job scheduling vs. Kueue."""
    profile = _normalize_profile_name(profile)
    ctx = get_current_context(silent=True)
    if counts_csv:
        try:
            counts = parse_counts_csv(counts_csv)
        except ValueError as error:
            raise typer.BadParameter(str(error), param_hint="--counts") from error
    else:
        counts = [2**i for i in range(e0, exponent + 1)]
    if not counts:
        raise typer.BadParameter(
            "No job counts resolved. Check --counts or exponent bounds.",
            param_hint="--counts",
        )
    try:
        resolved = resolve_performance_parameters(
            profile=profile,
            duration=_cli_override_or_none(ctx, "duration", duration),
            cores=_cli_override_or_none(ctx, "cores", cores),
            ram=_cli_override_or_none(ctx, "ram", ram),
            storage=_cli_override_or_none(ctx, "storage", storage),
            wait=_cli_override_or_none(ctx, "wait", wait),
        )
    except ValueError as error:
        raise typer.BadParameter(str(error), param_hint="--profile") from error
    final_duration = int(resolved["duration"])
    final_cores = float(resolved["cores"])
    final_ram = float(resolved["ram"])
    final_storage = float(resolved["storage"])
    final_wait = int(resolved["wait"])
    artifact_root, output, effective_run_id = _performance_output_paths(
        output_dir=output_dir,
        run_id=run_id,
    )
    plot_dir = f"{artifact_root}/plots/performance"

    logger.info("Starting benchmark with the following configuration:")
    logger.info("Profile  : %s", profile)
    logger.info("Jobs     : %s", counts)
    logger.info("Duration : %ss", final_duration)
    logger.info(
        "Cores    : %s, RAM: %sGB, Storage: %sGB",
        final_cores,
        final_ram,
        final_storage,
    )
    logger.info("Namespace: %s", namespace)
    logger.info("Template : %s", filepath)
    logger.info("Kueue    : %s", kueue)
    logger.info("Priority : %s", priority)
    logger.info("Run ID   : %s", effective_run_id or "(custom output-dir)")
    logger.info("Output   : %s", output)
    logger.info("Wait     : %ss", final_wait)
    logger.info(
        "Apply    : chunk=%s retries=%s backoff=%ss",
        apply_chunk_size,
        apply_retries,
        apply_backoff,
    )

    if not k8s.check(namespace, kueue, priority):
        logger.error("Please check your Kueue configuration.")
        raise typer.Exit(code=1)

    benchmark(
        counts=counts,
        duration=final_duration,
        cores=final_cores,
        ram=final_ram,
        storage=final_storage,
        namespace=namespace,
        filepath=filepath,
        kueue=kueue,
        priority=priority,
        resultsfile=output,
        wait=final_wait,
        apply_chunk_size=apply_chunk_size,
        apply_retries=apply_retries,
        apply_backoff=apply_backoff,
    )
    logger.info("Benchmark completed successfully.")
    logger.info("Results saved to %s", output)
    typer.echo(f"Artifacts written under {artifact_root}")
    typer.echo(
        f"uv run kr plot performance {output} --output-dir {plot_dir} --show"
    )


@benchmark_cli.command("evictions")
def eviction(
    filepath: str = (
        typer.Option(
            DEFAULT_JOBSPEC_FILEPATH, "-f", "--filepath", help="K8s job template."
        )
    ),
    namespace: str = (
        typer.Option(
            "skaha-workload", "-n", "--namespace", help="Namespace to launch jobs in."
        )
    ),
    kueue: str = (
        typer.Option(
            "skaha-local-queue",
            "-k",
            "--kueue",
            help="Local Kueue queue to launch jobs in.",
        )
    ),
    priorities: List[str] = (
        typer.Option(  # noqa: B008
            ["low", "medium", "high"],
            "-p",
            "--priorities",
            help="Ordered Kueue priorities to launch jobs with, from low to high.",
        )
    ),
    profile: str = typer.Option(
        "local-safe",
        "--profile",
        help="Eviction profile defaults. Use local-safe for local reliability.",
    ),
    jobs: int = (
        typer.Option(8, "-j", "--jobs", help="Jobs per priority level to launch.")
    ),
    cores: float = (
        typer.Option(
            2.0,
            "-c",
            "--cores",
            help="Total number of CPU cores in the kueue ClusterQueue.",
        )
    ),
    ram: float = (
        typer.Option(
            2.0,
            "-r",
            "--ram",
            help="Total amount of RAM in the kueue ClusterQueue in GB.",
        )
    ),
    storage: float = (
        typer.Option(
            2.0,
            "-s",
            "--storage",
            help="Total amount of storage in the kueue ClusterQueue in GB.",
        )
    ),
    duration: int = (
        typer.Option(
            60, "-d", "--duration", help="Longest duration for jobs in seconds."
        )
    ),
    output_dir: str = typer.Option(
        "artifacts",
        "-o",
        "--output-dir",
        help="Directory where benchmark artifacts are written.",
    ),
    run_id: str = typer.Option(
        "",
        "--run-id",
        help="Run identifier used under the default artifacts directory.",
    ),
    apply_chunk_size: int = typer.Option(
        25, "--apply-chunk-size", help="Number of jobs per kubectl apply chunk."
    ),
    apply_retries: int = typer.Option(
        2, "--apply-retries", help="Retries per apply chunk on kubectl failures."
    ),
    apply_backoff: float = typer.Option(
        2.0,
        "--apply-backoff",
        help="Backoff base (seconds) between apply retries.",
    ),
):
    """Run a benchmark to test eviction behavior of Kueue in a packed cluster queue."""
    profile = _normalize_profile_name(profile)
    ctx = get_current_context(silent=True)
    try:
        resolved = resolve_eviction_parameters(
            profile=profile,
            jobs=_cli_override_or_none(ctx, "jobs", jobs),
            cores=_cli_override_or_none(ctx, "cores", cores),
            ram=_cli_override_or_none(ctx, "ram", ram),
            storage=_cli_override_or_none(ctx, "storage", storage),
            duration=_cli_override_or_none(ctx, "duration", duration),
        )
    except ValueError as error:
        raise typer.BadParameter(str(error), param_hint="--profile") from error

    final_jobs = int(resolved["jobs"])
    final_cores = float(resolved["cores"])
    final_ram = float(resolved["ram"])
    final_storage = float(resolved["storage"])
    final_duration = int(resolved["duration"])
    artifact_root, output, effective_run_id = _eviction_output_paths(
        output_dir=output_dir,
        run_id=run_id,
    )
    plot_dir = f"{artifact_root}/plots/evictions"

    config.load_kube_config()
    crd = client.CustomObjectsApi()
    snapshot = crd.list_namespaced_custom_object(  # type: ignore
        group="kueue.x-k8s.io",
        version="v1beta1",
        namespace=namespace,
        plural="workloads",
    )
    resource_id = str(snapshot.get("metadata", {}).get("resourceVersion", ""))

    logger.info("Starting eviction benchmarks with the following configuration:")
    logger.info("Template     : %s", filepath)
    logger.info("Namespace    : %s", namespace)
    logger.info("Kueue        : %s", kueue)
    logger.info("Profile      : %s", profile)
    logger.info("Run ID       : %s", effective_run_id or "(custom output-dir)")
    logger.info("Priorities   : %s", priorities)
    logger.info("Total Cores  : %s", final_cores)
    logger.info("Total RAM    : %sGB", final_ram)
    logger.info("Total Storage: %sGB", final_storage)
    logger.info("Job Duration : %ss", final_duration)
    logger.info("Job Count    : %s", final_jobs)
    logger.info(
        "Apply       : chunk=%s retries=%s backoff=%ss",
        apply_chunk_size,
        apply_retries,
        apply_backoff,
    )
    logger.info("K8s Resource : %s", resource_id)

    for priority in priorities:
        if not k8s.check(namespace, kueue, priority):
            logger.error("Please check your Kueue configuration.")
            raise typer.Exit(code=1)
    logger.info("Kueue configuration is valid.")

    prefix: str = "kueue-eviction"
    job_count = final_jobs
    job_core: float = max(final_cores / job_count, 0.1)
    job_ram: float = max(final_ram / job_count, 0.1)
    job_storage: float = max(final_storage / job_count, 0.1)

    for index, priority in enumerate(priorities):
        job_duration = max(int(final_duration / (2**index)), 1)
        logger.info(
            "Job Parameters: Cores: %s, RAM: %.3fGB, Storage: %.3fGB",
            job_core,
            job_ram,
            job_storage,
        )
        logger.info(
            "Launching %s jobs with %s priority and duration of %ss",
            job_count,
            priority,
            job_duration,
        )
        k8s.run(
            filepath=filepath,
            namespace=namespace,
            prefix=f"{prefix}-{priority}-job",
            jobs=job_count,
            duration=job_duration,
            cores=job_core,
            ram=job_ram,
            storage=job_storage,
            kueue=kueue,
            priority=priority,
            apply_chunk_size=apply_chunk_size,
            apply_retries=apply_retries,
            apply_backoff=apply_backoff,
        )

    logger.info("All jobs launched successfully.")
    logger.info("Tracking jobs to completion...")
    results = track.evictions(
        namespace=namespace,
        revision=resource_id,
        prefix=prefix,
    )

    logger.info("Saving results to %s", output)
    io.save_evictions_to_yaml(results=results, filename=output)
    logger.info("Results saved successfully.")
    logger.info("Analyzing eviction results...")

    issues: bool = analyze.evictions(results)
    if issues:
        logger.error("Eviction issues detected!")
    else:
        logger.info("No eviction issues detected.")
    logger.info("Eviction tracking completed.")
    logger.info("Cleaning up jobs...")
    k8s.delete_jobs(namespace, prefix)
    logger.info("Jobs cleaned up successfully.")
    logger.info("Eviction benchmark completed.")
    typer.echo(f"Artifacts written under {artifact_root}")
    typer.echo(
        f"uv run kr plot evictions {output} --output-dir {plot_dir} --show"
    )


if __name__ == "__main__":
    benchmark_cli()
