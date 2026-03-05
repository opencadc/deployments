"""Benchmark module for comparing Kubernetes job execution with and without Kueue."""

import math
import time
from datetime import datetime
from time import sleep
from typing import Any, Dict, List, Optional

import typer
from kubernetes import client, config

from kueuer.benchmarks import DEFAULT_JOBSPEC_FILEPATH, analyze, k8s, track
from kueuer.utils import io
from kueuer.utils.logging import logger

benchmark_cli: typer.Typer = typer.Typer(help="Launch Benchmarks")


def experiment(
    count: int,
    duration: int,
    cores: int,
    ram: float,
    storage: float,
    namespace: str,
    filepath: str,
    use_kueue: bool = False,
    kueue: Optional[str] = None,
    priority: Optional[str] = None,
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
    k8s.run(
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
    )

    # Track jobs to completion and get timing statistics
    logger.info("Jobs launched, tracking completion...")
    times = track.jobs(namespace, prefix, "Complete")
    logger.info("All jobs completed, computing statistics...")
    stats = track.compute_statistics(times)

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
    }

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
    cores: int,
    ram: float,
    storage: float,
    namespace: str,
    filepath: str,
    kueue: Optional[str],
    priority: Optional[str],
    resultsfile: str,
    wait: int,
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
        typer.Option(1, "-d", "--duration", help="Duration for each job in seconds.")
    ),
    cores: int = (
        typer.Option(
            1, "-c", "--cores", help="Number of CPU cores to allocate to each job."
        )
    ),
    ram: float = (
        typer.Option(
            1.0, "-r", "--ram", help="Amount of RAM to allocate to each job in GB."
        )
    ),
    storage: float = (
        typer.Option(
            1.0,
            "-s",
            "--storage",
            help="Amount of ephemeral-storage to allocate to each job in GB.",
        )
    ),
    output: str = (
        typer.Option("results.csv", "-o", "--output", help="File to save results to.")
    ),
    wait: int = (
        typer.Option(60, "-w", "--wait", help="Time to wait between experiments.")
    ),
):
    """Compare native K8s job scheduling vs. Kueue."""
    counts = [2**i for i in range(e0, exponent + 1)]
    logger.info("Starting benchmark with the following configuration:")
    logger.info("Jobs     : %s", counts)
    logger.info("Duration : %ss", duration)
    logger.info("Cores    : %s, RAM: %sGB, Storage: %sGB", cores, ram, storage)
    logger.info("Namespace: %s", namespace)
    logger.info("Template : %s", filepath)
    logger.info("Kueue    : %s", kueue)
    logger.info("Priority : %s", priority)
    logger.info("Output   : %s", output)
    logger.info("Wait     : %ss", wait)

    if not k8s.check(namespace, kueue, priority):
        logger.error("Please check your Kueue configuration.")
        raise typer.Exit(code=1)

    benchmark(
        counts=counts,
        duration=duration,
        cores=cores,
        ram=ram,
        storage=storage,
        namespace=namespace,
        filepath=filepath,
        kueue=kueue,
        priority=priority,
        resultsfile=output,
        wait=wait,
    )
    logger.info("Benchmark completed successfully.")
    logger.info("Results saved to %s", output)
    logger.info(
        "You can now run 'kr plot performance %s' to visualize the results.", output
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
    jobs: int = (
        typer.Option(8, "-j", "--jobs", help="Jobs per priority level to launch.")
    ),
    cores: int = (
        typer.Option(
            8,
            "-c",
            "--cores",
            help="Total number of CPU cores in the kueue ClusterQueue.",
        )
    ),
    ram: float = (
        typer.Option(
            8.0,
            "-r",
            "--ram",
            help="Total amount of RAM in the kueue ClusterQueue in GB.",
        )
    ),
    storage: float = (
        typer.Option(
            8.0,
            "-s",
            "--storage",
            help="Total amount of storage in the kueue ClusterQueue in GB.",
        )
    ),
    duration: int = (
        typer.Option(
            120, "-d", "--duration", help="Longest duration for jobs in seconds."
        )
    ),
    output: str = (
        typer.Option(
            "evictions.yaml", "-o", "--output", help="Filen to save results to."
        )
    ),
):
    """Run a benchmark to test eviction behavior of Kueue in a packed cluster queue."""
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
    logger.info("Priorities   : %s", priorities)
    logger.info("Total Cores  : %s", cores)
    logger.info("Total RAM    : %sGB", ram)
    logger.info("Total Storage: %sGB", storage)
    logger.info("Job Duration : %ss", duration)
    logger.info("Job Count    : %s", jobs)
    logger.info("K8s Resource : %s", resource_id)

    for priority in priorities:
        if not k8s.check(namespace, kueue, priority):
            logger.error("Please check your Kueue configuration.")
            raise typer.Exit(code=1)
    logger.info("Kueue configuration is valid.")

    prefix: str = "kueue-eviction"
    job_count = jobs
    job_core: int = max(math.ceil(cores / job_count), 1)
    job_ram: float = max(ram / job_count, 0.1)
    job_storage: float = max(storage / job_count, 0.1)

    for index, priority in enumerate(priorities):
        job_duration = max(int(duration / (2**index)), 1)
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
    logger.info(
        "You can now run 'kr plot evictions %s' to visualize the results.", output
    )


if __name__ == "__main__":
    benchmark_cli()
