"""Launches a job in a Kubernetes cluster."""

import asyncio
from time import time
from typing import Any, Awaitable, Dict, List, Optional

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


async def apply(data: Dict[Any, Any], prefix: str, count: int) -> bool:
    """Kubernetes job apply.

    Args:
        data (Dict[Any, Any]): K8s job template.
        name (str): Name of the job.

    """
    async with aiofiles.tempfile.NamedTemporaryFile(
        delete=False, mode="w", suffix=".yaml"
    ) as temp:
        for num in range(count):
            name: str = f"{prefix}-{num}"
            data["metadata"]["name"] = name
            for container in data["spec"]["template"]["spec"]["containers"]:
                container["name"] = name
            await temp.write(yaml.dump(data))
            await temp.write("\n---\n")
    logger.debug("Applying %s", temp.name)
    now = time()
    try:
        command = f"kubectl apply -f {temp.name}"
        proc = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        logger.debug("stdout: %s", stdout.decode())
        if stderr:
            logger.info("stderr: %s", stderr.decode())
        if proc.returncode != 0:
            logger.error("Error applying %s", temp.name)
            return False
        return True
    finally:
        logger.info("Took %ss to apply k8s manifest", time() - now)
        await temp.close()
        await aiofiles.os.remove(str(temp.name))
        logger.debug("Deleted %s", temp.name)


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
    cores: int = (
        typer.Option(
            1, "-c", "--cores", help="Number of CPU cores to allocate to each job."
        )
    ),
    ram: int = (
        typer.Option(
            1, "-r", "--ram", help="Amount of RAM to allocate to each job in GB."
        )
    ),
    storage: int = (
        typer.Option(
            1,
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
) -> None:
    """Run jobs to stress k8s cluster."""
    ram_mb: float = ram * 1024.0
    args: List[str] = [
        "--cpu",
        f"{cores}",
        "--cpu-method",
        "matrixprod",
        "--vm",
        "1",
        "--vm-bytes",
        f"{ram_mb * 0.8}M",
        "--temp-path",
        "/tmp",
        "--timeout",
        f"{duration}",
        "--metrics-brief",
    ]
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
        container["resources"]["limits"]["cpu"] = f"{cores}"
        container["resources"]["limits"]["memory"] = f"{ram_mb}Mi"
        container["resources"]["limits"]["ephemeral-storage"] = f"{storage}Gi"
        container["resources"]["requests"] = {}
        container["resources"]["requests"]["cpu"] = f"{cores}"
        container["resources"]["requests"]["memory"] = f"{ram_mb}Mi"
        container["resources"]["requests"]["ephemeral-storage"] = f"{storage}Gi"

    tasks: List[Awaitable[bool]] = []
    tasks.append(apply(job, prefix, jobs))
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.gather(*tasks))


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
