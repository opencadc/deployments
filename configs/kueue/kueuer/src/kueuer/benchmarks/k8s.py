"""Launches a job in a Kubernetes cluster."""

import asyncio
import copy
import math
from time import time
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
import aiofiles.os
import typer
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from kueuer.benchmarks import DEFAULT_JOBSPEC_FILEPATH
from kueuer.utils import io
from kueuer.utils.logging import logger

app = typer.Typer(help="Launch K8s Jobs")
DEFAULT_STRESS_VM_MEMORY_FRACTION = 0.33


def check(namespace: str, kueue: str, priority: str) -> bool:
    """Check if the namespace, kueue, and priority exist.

    Args:
        namespace (str): K8s namespace.
        kueue (str): Kueue name.
        priority (str): Kueue priority.

    Returns:
        bool: True if all checks pass, False otherwise.
    """

    # Check if the namespace exists
    config.load_kube_config()
    crd: client.CustomObjectsApi = client.CustomObjectsApi()
    v1 = client.CoreV1Api()
    checks: Dict[str, bool] = {}
    try:
        v1.read_namespace(name=namespace)  # type: ignore
        checks["namespace"] = True
    except ApiException as error:
        if error.status == 404:
            logger.error("Namespace %s not found", namespace)

    try:
        localkueues = crd.list_namespaced_custom_object(  # type: ignore
            group="kueue.x-k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="localqueues",
        )
        for localqueue in localkueues.get("items", []):
            if localqueue.get("metadata", {}).get("name") == kueue:
                logger.info("LocalQueue %s found in namespace %s", kueue, namespace)
                checks["kueue"] = True
                break
    except ApiException as error:
        logger.error(
            "Error checking for Kueue LocalQueue %s in namespace %s: %s",
            kueue,
            namespace,
            error,
        )

    try:
        priorities = crd.list_cluster_custom_object(
            group="kueue.x-k8s.io", version="v1beta1", plural="workloadpriorityclasses"
        )
        for priorityclass in priorities.get("items", []):
            if priorityclass.get("metadata", {}).get("name") == priority:
                logger.info("Kueue PriorityClass %s found.", priority)
                checks["priority"] = True
                break
    except ApiException as error:
        logger.error(
            "Error checking for Kueue PriorityClass %s: %s",
            priority,
            error,
        )
    if len(checks) != 3:
        logger.error("Not all checks passed")
        return False
    else:
        logger.info("All checks passed")
        return True


def clusterqueue(kueue: str) -> Optional[str]:
    """Get the clusterqueue name for the given kueue.

    Args:
        kueue (str): Kueue name.

    Returns:
        Optional[str]: Clusterqueue name.
    """
    config.load_kube_config()
    crd: client.CustomObjectsApi = client.CustomObjectsApi()
    try:
        queues = crd.list_cluster_custom_object(  # type: ignore
            group="kueue.x-k8s.io",
            version="v1beta1",
            plural="clusterqueues",
        )
        for queue in queues.get("items", []):
            if queue.get("metadata", {}).get("name") == kueue:
                return queue.get("spec", {}).get("clusterqueue")
    except ApiException as error:
        logger.error(
            "Error checking for Kueue ClusterQueue %s: %s",
            kueue,
            error,
        )
    return None


def chunk_ranges(total: int, chunk_size: int) -> List[Tuple[int, int]]:
    """Split total jobs into [start, end) chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    return [
        (start, min(start + chunk_size, total))
        for start in range(0, total, chunk_size)
    ]


def stress_cpu_workers(cores: float) -> int:
    """Map requested CPU to a stress-ng worker count."""
    return max(int(math.ceil(cores)), 1)


def stress_vm_bytes_mb(ram_gb: float, vm_memory_fraction: float) -> float:
    """Return stress-ng vm-bytes value in megabytes.

    Args:
        ram_gb: Pod memory limit/request in GiB.
        vm_memory_fraction: Fraction of pod memory allocated to stress-ng vm worker.

    Returns:
        float: vm-bytes value in MB.
    """
    if not 0.0 < vm_memory_fraction < 1.0:
        raise ValueError("vm_memory_fraction must be between 0 and 1 (exclusive)")
    ram_mb = ram_gb * 1024.0
    return ram_mb * vm_memory_fraction


def is_high_oom_risk(ram_gb: float, vm_memory_fraction: float) -> bool:
    """Heuristic for tight memory headroom likely to trigger OOM.

    This warns when stress-ng memory pressure leaves too little room for process/runtime
    overhead under pod cgroup limits.
    """
    vm_bytes_mb = stress_vm_bytes_mb(ram_gb=ram_gb, vm_memory_fraction=vm_memory_fraction)
    # For small pods, keep additional safety headroom to avoid allocator/runtime spikes.
    return vm_memory_fraction >= 0.75 or (ram_gb <= 1.0 and vm_bytes_mb >= 600.0)


def _format_cpu_quantity(cores: float) -> str:
    """Format CPU cores into Kubernetes CPU quantity syntax."""
    if float(cores).is_integer():
        return str(int(cores))
    return f"{cores:.3f}".rstrip("0").rstrip(".")


def _contains_oomkilled(container_statuses: Any) -> bool:
    """Return True when any container was terminated due to OOMKilled."""
    for container in container_statuses or []:
        state = getattr(container, "state", None)
        terminated = getattr(state, "terminated", None)
        reason = getattr(terminated, "reason", None)
        if reason == "OOMKilled":
            return True
    return False


def summarize_pod_statuses(pods: List[Any]) -> Dict[str, int]:
    """Summarize phase and OOMKilled outcomes for a pod collection."""
    summary: Dict[str, int] = {
        "pods_total": len(pods),
        "pods_pending": 0,
        "pods_running": 0,
        "pods_succeeded": 0,
        "pods_failed": 0,
        "pods_oomkilled": 0,
        "pods_unknown": 0,
    }
    for pod in pods:
        phase = str(getattr(pod.status, "phase", "Unknown"))
        key = f"pods_{phase.lower()}"
        if key in summary:
            summary[key] += 1
        else:
            summary["pods_unknown"] += 1
        if _contains_oomkilled(getattr(pod.status, "container_statuses", None)):
            summary["pods_oomkilled"] += 1
    return summary


def collect_pod_outcomes(namespace: str, prefix: str) -> Dict[str, int]:
    """Collect pod outcome summary for jobs with the given name prefix."""
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=namespace).items
    selected = [
        pod
        for pod in pods
        if (pod.metadata and pod.metadata.name and pod.metadata.name.startswith(prefix))
    ]
    return summarize_pod_statuses(selected)


def collect_job_outcomes(namespace: str, prefix: str) -> Dict[str, int]:
    """Collect job outcome counters for jobs with the given name prefix."""
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    jobs = batch_v1.list_namespaced_job(namespace=namespace).items
    selected = [
        job
        for job in jobs
        if (job.metadata and job.metadata.name and job.metadata.name.startswith(prefix))
    ]
    outcomes: Dict[str, int] = {
        "jobs_total": len(selected),
        "jobs_succeeded": 0,
        "jobs_failed": 0,
        "jobs_active": 0,
    }
    for job in selected:
        outcomes["jobs_succeeded"] += int(getattr(job.status, "succeeded", 0) or 0)
        outcomes["jobs_failed"] += int(getattr(job.status, "failed", 0) or 0)
        outcomes["jobs_active"] += int(getattr(job.status, "active", 0) or 0)
    return outcomes


def kueue_controller_restarts(namespace: str = "kueue-system") -> int:
    """Return aggregate restart count of kueue-system pods."""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace).items
        total = 0
        for pod in pods:
            for status in getattr(pod.status, "container_statuses", None) or []:
                total += int(getattr(status, "restart_count", 0) or 0)
        return total
    except Exception as error:  # noqa: BLE001
        logger.warning(
            "Unable to sample Kueue controller restarts in namespace %s: %s",
            namespace,
            error,
        )
        return 0


async def apply(
    data: Dict[Any, Any],
    prefix: str,
    count: int,
    chunk_size: int = 25,
    retries: int = 2,
    backoff_seconds: float = 2.0,
) -> Dict[str, Any]:
    """Kubernetes job apply.

    Args:
        data (Dict[Any, Any]): K8s job template.
        name (str): Name of the job.

    """
    now = time()
    report: Dict[str, Any] = {
        "requested_jobs": count,
        "chunk_size": chunk_size,
        "chunks_total": 0,
        "chunks_succeeded": 0,
        "chunks_failed": 0,
        "jobs_applied": 0,
        "jobs_failed_to_apply": 0,
        "apply_attempts": 0,
        "apply_retries": 0,
        "manifest_apply_seconds": 0.0,
        "last_error": "",
    }
    for start, end in chunk_ranges(count, chunk_size):
        report["chunks_total"] += 1
        chunk_jobs = end - start
        async with aiofiles.tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".yaml"
        ) as temp:
            for num in range(start, end):
                manifest = copy.deepcopy(data)
                name: str = f"{prefix}-{num}"
                manifest["metadata"]["name"] = name
                for container in manifest["spec"]["template"]["spec"]["containers"]:
                    container["name"] = name
                await temp.write(yaml.dump(manifest))
                await temp.write("\n---\n")
        logger.debug("Applying %s", temp.name)
        try:
            applied = False
            for attempt in range(1, retries + 2):
                report["apply_attempts"] += 1
                proc = await asyncio.create_subprocess_exec(
                    "kubectl",
                    "apply",
                    "-f",
                    str(temp.name),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    logger.debug("stdout: %s", stdout.decode())
                if stderr:
                    logger.info("stderr: %s", stderr.decode())
                if proc.returncode == 0:
                    applied = True
                    report["chunks_succeeded"] += 1
                    report["jobs_applied"] += chunk_jobs
                    break
                report["last_error"] = stderr.decode().strip() or stdout.decode().strip()
                if attempt <= retries:
                    report["apply_retries"] += 1
                    sleep_s = backoff_seconds * attempt
                    logger.warning(
                        "kubectl apply failed for %s (attempt %s/%s), retrying in %.1fs",
                        temp.name,
                        attempt,
                        retries + 1,
                        sleep_s,
                    )
                    await asyncio.sleep(sleep_s)
            if not applied:
                report["chunks_failed"] += 1
                report["jobs_failed_to_apply"] += chunk_jobs
                logger.error("Failed to apply manifest chunk %s", temp.name)
        finally:
            await temp.close()
            await aiofiles.os.remove(str(temp.name))
            logger.debug("Deleted %s", temp.name)
    report["manifest_apply_seconds"] = time() - now
    logger.info("Took %ss to apply k8s manifest", report["manifest_apply_seconds"])
    return report


@app.command("run")
def run(
    filepath: str = (
        typer.Option(
            DEFAULT_JOBSPEC_FILEPATH, "-f", "--filepath", help="K8s job template."
        )
    ),
    namespace: str = (
        typer.Option(
            "default", "-n", "--namespace", help="Namespace to launch jobs in."
        )
    ),
    prefix: str = typer.Option(
        "kueuer-job", "-p", "--prefix", help="Prefix for job names."
    ),
    jobs: int = (typer.Option(1, "-j", "--jobs", help="Number of jobs to launch.")),
    duration: int = (
        typer.Option(60, "-d", "--duration", help="Duration for each job in seconds.")
    ),
    cores: float = (
        typer.Option(
            1.0, "-c", "--cores", help="Number of CPU cores to allocate to each job."
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
    kueue: Optional[str] = (
        typer.Option(None, "-k", "--kueue", help="Kueue queue to launch jobs in.")
    ),
    priority: Optional[str] = (
        typer.Option(
            None, "-p", "--priority", help="Kueue priority to launch jobs with."
        )
    ),
    apply_chunk_size: int = (
        typer.Option(
            25,
            "--apply-chunk-size",
            help="Number of jobs per kubectl apply chunk.",
        )
    ),
    apply_retries: int = (
        typer.Option(
            2, "--apply-retries", help="Retries per apply chunk on kubectl failures."
        )
    ),
    apply_backoff: float = (
        typer.Option(
            2.0,
            "--apply-backoff",
            help="Backoff base (seconds) used between apply retries.",
        )
    ),
    vm_memory_fraction: float = (
        typer.Option(
            DEFAULT_STRESS_VM_MEMORY_FRACTION,
            "--vm-memory-fraction",
            min=0.1,
            max=0.95,
            help=(
                "Fraction of pod memory assigned to stress-ng --vm-bytes. "
                "Lower values leave more headroom and reduce OOM risk."
            ),
        )
    ),
) -> Dict[str, Any]:
    """Run jobs to stress k8s cluster."""
    ram_mb: float = ram * 1024.0
    cpu_workers = stress_cpu_workers(cores)
    vm_bytes_mb = stress_vm_bytes_mb(
        ram_gb=ram,
        vm_memory_fraction=vm_memory_fraction,
    )
    cpu_quantity = _format_cpu_quantity(cores)
    args: List[str] = [
        "--cpu",
        f"{cpu_workers}",
        "--cpu-method",
        "matrixprod",
        "--vm",
        "1",
        "--vm-bytes",
        f"{vm_bytes_mb}M",
        "--temp-path",
        "/tmp",
        "--timeout",
        f"{duration}",
        "--metrics-brief",
    ]
    if is_high_oom_risk(ram_gb=ram, vm_memory_fraction=vm_memory_fraction):
        logger.warning(
            "High OOM risk: ram=%sGi, vm-memory-fraction=%s (vm-bytes=%sM). "
            "Consider reducing --vm-memory-fraction.",
            ram,
            vm_memory_fraction,
            f"{vm_bytes_mb:.1f}",
        )
    job = io.read_yaml(filepath)

    # Write common job parameters
    job["metadata"] = {}
    job["metadata"]["labels"] = {}
    job["metadata"]["namespace"] = namespace
    if kueue:
        job["metadata"]["labels"]["kueue.x-k8s.io/queue-name"] = kueue
        job["spec"]["suspend"] = True
    if priority:
        job["metadata"]["labels"]["kueue.x-k8s.io/priority-class"] = priority
    for container in job["spec"]["template"]["spec"]["containers"]:
        container["args"] = args
        container["resources"] = {}
        container["resources"]["limits"] = {}
        container["resources"]["limits"]["cpu"] = cpu_quantity
        container["resources"]["limits"]["memory"] = f"{ram_mb}Mi"
        container["resources"]["limits"]["ephemeral-storage"] = f"{storage}Gi"
        container["resources"]["requests"] = {}
        container["resources"]["requests"]["cpu"] = cpu_quantity
        container["resources"]["requests"]["memory"] = f"{ram_mb}Mi"
        container["resources"]["requests"]["ephemeral-storage"] = f"{storage}Gi"
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        apply(
            job,
            prefix,
            jobs,
            chunk_size=apply_chunk_size,
            retries=apply_retries,
            backoff_seconds=apply_backoff,
        )
    )
    return result


@app.command("delete")
def delete_jobs(
    namespace: str = (
        typer.Option(
            "default", "-n", "--namespace", help="Namespace to launch jobs in."
        )
    ),
    prefix: str = typer.Option(
        "kueuer-job", "-p", "--prefix", help="Prefix for job names."
    ),
) -> int:
    """Delete jobs with given prefix in a namespace.

    Args:
        namespace (str): Namespace to delete jobs in.
        prefix (str): Prefix for job names.

    Returns:
        int: Number of jobs deleted
    """
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    logger.info("Deleting jobs with prefix %s in namespace %s", prefix, namespace)
    try:
        jobs = batch_v1.list_namespaced_job(namespace)
        jobs_to_delete: List[str] = [
            job.metadata.name
            for job in jobs.items
            if job.metadata.name.startswith(prefix)
        ]

        if not jobs_to_delete:
            logger.info("No jobs with found")
            return 0
        num = len(jobs_to_delete)
        logger.info("Found %s jobs to delete", num)
        now = time()
        for job_name in jobs_to_delete:
            batch_v1.delete_namespaced_job(
                name=job_name,
                namespace=namespace,
                body=client.V1DeleteOptions(propagation_policy="Foreground"),
            )
        logger.info("Took %ss to delete %s jobs", time() - now, num)
        return len(jobs_to_delete)
    except ApiException as e:
        logger.error("Exception when deleting jobs: %s", e)
        return 0


if __name__ == "__main__":
    app()
