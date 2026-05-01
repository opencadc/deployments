"""Launches a job in a Kubernetes cluster."""

import asyncio
import copy
import math
import random
from time import time
from typing import Any, Dict, List, Optional, Tuple, cast

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
DEFAULT_SPAWN_MECHANISM = "kubectl"

# Cache API connectivity mode per process.
_API_CLIENT_READY: bool = False


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


def _load_client_config_best_effort() -> bool:
    """Try kubeconfig first, then in-cluster config."""
    try:
        config.load_kube_config()
        return True
    except Exception:  # noqa: BLE001
        try:
            config.load_incluster_config()
            return True
        except Exception:  # noqa: BLE001
            return False


def collect_pod_outcomes(namespace: str, prefix: str) -> Dict[str, int]:
    """Collect pod outcome summary for jobs with the given name prefix."""
    empty = summarize_pod_statuses([])
    if not _load_client_config_best_effort():
        logger.warning("Unable to configure Kubernetes client while collecting pod outcomes.")
        return empty

    v1 = client.CoreV1Api()
    try:
        pod_list = v1.list_namespaced_pod(namespace=namespace)
        pods = list(getattr(pod_list, "items", None) or [])
    except Exception as error:  # noqa: BLE001
        logger.warning(
            "Unable to collect pod outcomes in namespace %s: %s",
            namespace,
            error,
        )
        return empty

    selected = [
        pod
        for pod in pods
        if (pod.metadata and pod.metadata.name and pod.metadata.name.startswith(prefix))
    ]
    return summarize_pod_statuses(selected)


def collect_job_outcomes(namespace: str, prefix: str) -> Dict[str, int]:
    """Collect job outcome counters for jobs with the given name prefix."""
    empty: Dict[str, int] = {
        "jobs_total": 0,
        "jobs_succeeded": 0,
        "jobs_failed": 0,
        "jobs_active": 0,
    }
    if not _load_client_config_best_effort():
        logger.warning("Unable to configure Kubernetes client while collecting job outcomes.")
        return empty

    batch_v1 = client.BatchV1Api()
    try:
        job_list = batch_v1.list_namespaced_job(namespace=namespace)
        jobs = list(getattr(job_list, "items", None) or [])
    except Exception as error:  # noqa: BLE001
        logger.warning(
            "Unable to collect job outcomes in namespace %s: %s",
            namespace,
            error,
        )
        return empty

    selected = [
        job
        for job in jobs
        if (job.metadata and job.metadata.name and job.metadata.name.startswith(prefix))
    ]
    outcomes = {**empty, "jobs_total": len(selected)}
    for job in selected:
        outcomes["jobs_succeeded"] += int(getattr(job.status, "succeeded", 0) or 0)
        outcomes["jobs_failed"] += int(getattr(job.status, "failed", 0) or 0)
        outcomes["jobs_active"] += int(getattr(job.status, "active", 0) or 0)
    return outcomes


def kueue_controller_restarts(namespace: str = "kueue-system") -> int:
    """Return aggregate restart count of kueue-system pods."""
    try:
        if not _load_client_config_best_effort():
            raise RuntimeError("unable to configure kubernetes client")
        v1 = client.CoreV1Api()
        pod_list = v1.list_namespaced_pod(namespace=namespace)
        pods = list(getattr(pod_list, "items", None) or [])
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
        "chunk_spawn_seconds": [],
        "last_error": "",
        "spawn_mechanism": "kubectl",
    }
    for start, end in chunk_ranges(count, chunk_size):
        chunk_start = time()
        report["chunks_total"] += 1
        chunk_jobs = end - start
        async with aiofiles.tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".yaml"
        ) as temp:
            for manifest in render_job_manifests(data, prefix, start, end):
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
        report["chunk_spawn_seconds"].append(time() - chunk_start)
    report["manifest_apply_seconds"] = time() - now
    logger.info("Took %ss to apply k8s manifest", report["manifest_apply_seconds"])
    return report


def render_job_manifest(
    template: Dict[Any, Any],
    name: str,
) -> Dict[Any, Any]:
    """Return a deep-copied job manifest with name and container names set."""
    manifest = copy.deepcopy(template)
    manifest["metadata"]["name"] = name
    for container in manifest["spec"]["template"]["spec"]["containers"]:
        container["name"] = name
    return manifest


def render_job_manifests(
    template: Dict[Any, Any],
    prefix: str,
    start: int,
    end: int,
) -> List[Dict[Any, Any]]:
    """Render job manifests for indices in [start, end)."""
    return [render_job_manifest(template, f"{prefix}-{num}") for num in range(start, end)]


def _is_transient_api_error(error: ApiException) -> bool:
    try:
        status = int(getattr(error, "status", 0) or 0)
    except Exception:  # noqa: BLE001
        return False
    return status in {429, 500, 502, 503, 504}


def _api_preflight_check(namespace: str) -> None:
    """Perform a lightweight namespace-scoped API check."""
    v1 = client.CoreV1Api()
    # Prefer a namespaced call to ensure auth scopes match workload permissions.
    v1.list_namespaced_pod(namespace=namespace, limit=1)  # type: ignore[arg-type]


def ensure_api_client_ready(namespace: str) -> None:
    """Ensure Kubernetes Python client is configured (kubeconfig or incluster)."""
    global _API_CLIENT_READY
    if _API_CLIENT_READY:
        return

    errors: List[str] = []
    try:
        config.load_kube_config()
        _api_preflight_check(namespace)
        _API_CLIENT_READY = True
        logger.info("Kubernetes API client configured using kubeconfig.")
        return
    except Exception as error:  # noqa: BLE001
        errors.append(f"kubeconfig: {error}")

    try:
        config.load_incluster_config()
        _api_preflight_check(namespace)
        _API_CLIENT_READY = True
        logger.info("Kubernetes API client configured using in-cluster service account.")
        return
    except Exception as error:  # noqa: BLE001
        errors.append(f"incluster: {error}")

    msg = "Unable to configure Kubernetes API client. " + "; ".join(errors)
    raise RuntimeError(msg)


async def _create_job_with_retries(
    batch: client.BatchV1Api,
    namespace: str,
    manifest: Dict[Any, Any],
    retries: int,
    backoff_seconds: float,
) -> Tuple[bool, str]:
    """Create a job with transient retries. Returns (ok, error_message)."""
    name = str(manifest.get("metadata", {}).get("name", ""))
    for attempt in range(1, retries + 2):
        try:
            batch.create_namespaced_job(namespace=namespace, body=manifest)  # type: ignore[arg-type]
            return True, ""
        except ApiException as error:
            if getattr(error, "status", None) == 409:
                # Create-only semantics: treat existing job as a failure.
                return False, f"{name}: already exists (409)"
            if not _is_transient_api_error(error) or attempt > retries:
                return False, f"{name}: {error}"
            sleep_s = backoff_seconds * attempt
            # Add jitter to avoid thundering herd.
            sleep_s *= 0.8 + (0.4 * random.random())
            await asyncio.sleep(sleep_s)
        except Exception as error:  # noqa: BLE001
            if attempt > retries:
                return False, f"{name}: {error}"
            sleep_s = backoff_seconds * attempt
            sleep_s *= 0.8 + (0.4 * random.random())
            await asyncio.sleep(sleep_s)
    return False, f"{name}: unknown failure"


async def apply_api(
    data: Dict[Any, Any],
    prefix: str,
    count: int,
    chunk_size: int = 25,
    retries: int = 2,
    backoff_seconds: float = 2.0,
    api_concurrency: int = 10,
    namespace: str = "default",
) -> Dict[str, Any]:
    """Create Kubernetes Jobs using the Python API client."""
    ensure_api_client_ready(namespace=namespace)
    batch = client.BatchV1Api()
    semaphore = asyncio.Semaphore(max(int(api_concurrency), 1))

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
        "chunk_spawn_seconds": [],
        "last_error": "",
        "spawn_mechanism": "api",
        "api_concurrency": api_concurrency,
    }

    async def _guarded_create(manifest: Dict[Any, Any]) -> Tuple[bool, str]:
        async with semaphore:
            ok, err = await _create_job_with_retries(
                batch=batch,
                namespace=namespace,
                manifest=manifest,
                retries=retries,
                backoff_seconds=backoff_seconds,
            )
            report["apply_attempts"] += 1
            if not ok and err:
                report["last_error"] = err
            return ok, err

    for start, end in chunk_ranges(count, chunk_size):
        chunk_start = time()
        report["chunks_total"] += 1
        manifests = render_job_manifests(data, prefix, start, end)
        results = await asyncio.gather(*[_guarded_create(m) for m in manifests])
        failures = [err for ok, err in results if not ok]
        if failures:
            report["chunks_failed"] += 1
            report["jobs_failed_to_apply"] += len(failures)
            report["last_error"] = failures[0]
        else:
            report["chunks_succeeded"] += 1
            report["jobs_applied"] += len(results)
        report["chunk_spawn_seconds"].append(time() - chunk_start)

    report["manifest_apply_seconds"] = time() - now
    logger.info("Took %ss to submit jobs via API", report["manifest_apply_seconds"])
    return report


async def submit_jobs(
    template: Dict[Any, Any],
    prefix: str,
    jobs: int,
    spawn_mechanism: str,
    namespace: str,
    apply_chunk_size: int,
    apply_retries: int,
    apply_backoff: float,
) -> Dict[str, Any]:
    """Submit rendered jobs using the selected spawn mechanism."""
    if spawn_mechanism == "api":
        return await apply_api(
            template,
            prefix,
            jobs,
            chunk_size=apply_chunk_size,
            retries=apply_retries,
            backoff_seconds=apply_backoff,
            namespace=namespace,
        )
    return await apply(
        template,
        prefix,
        jobs,
        chunk_size=apply_chunk_size,
        retries=apply_retries,
        backoff_seconds=apply_backoff,
    )


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
    spawn_mechanism: str = (
        typer.Option(
            DEFAULT_SPAWN_MECHANISM,
            "--spawn-mechanism",
            help="Job spawn mechanism to use: kubectl (apply) or api (client create).",
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
        submit_jobs(
            template=job,
            prefix=prefix,
            jobs=jobs,
            spawn_mechanism=spawn_mechanism,
            namespace=namespace,
            apply_chunk_size=apply_chunk_size,
            apply_retries=apply_retries,
            apply_backoff=apply_backoff,
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
