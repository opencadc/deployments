"""Track the status of Kubernetes Objects."""

import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import logfire
from kubernetes import client, config, watch

# Type alias for job tracking: (creation_time, completion_time, duration_in_seconds)
JobTiming = Tuple[datetime, Optional[datetime], Optional[float]]

logfire.configure(send_to_logfire=False)


def status(job: client.V1Job, state: str) -> bool:
    """Check if a k8s job has reached a certain state.

    Args:
        job (client.V1Job): Kubernetes Job object.
        stage (str): Desired status of the job.

    Returns:
        bool: True if the job has reached the desired status.
    """
    if job.status.conditions:  # type: ignore
        for condition in job.status.conditions:  # type: ignore
            if condition.type == state and condition.status == "True":  # type: ignore
                return True
    return False


def compute_statistics(data: Dict[str, JobTiming]) -> Dict[str, Any]:
    """Compute Job Statistics"""
    creations: List[datetime] = [
        data[0] for data in data.values() if data[0] is not None
    ]
    completions: List[datetime] = [
        data[1] for data in data.values() if data[1] is not None
    ]
    durations: List[float] = [data[2] for data in data.values() if data[2] is not None]

    if not creations or not completions or not durations:
        return {}

    first_creation_time: datetime = min(creations)
    last_creation_time: datetime = max(creations)
    first_completion_time: datetime = min(completions)
    last_completion_time: datetime = max(completions)
    avg_duration: float = statistics.mean(durations)
    total_duration: float = (last_completion_time - first_creation_time).total_seconds()
    median_duration: float = statistics.median(durations)
    stddev_duration: float = statistics.stdev(durations) if len(durations) > 1 else 0.0

    stats: Dict[str, Any] = {
        "first_creation_time": first_creation_time,
        "last_creation_time": last_creation_time,
        "first_completion_time": first_completion_time,
        "last_completion_time": last_completion_time,
        "avg_time_from_creation_completion": avg_duration,
        "total_time_from_first_creation_to_last_completion": total_duration,
        "median_time_from_creation_completion": median_duration,
        "std_dev_time_from_creation_completion": stddev_duration,
    }
    return stats


def jobs(
    namespace: str,
    prefix: str,
    to_state: str = "Complete",
) -> Dict[str, JobTiming]:
    """Track the status of Kubernetes Jobs.

    Args:
        namespace (str): Namespace of the jobs.
        prefix (str): Prefix of the job.metadata.name.
        to_state (str): Desired state of the job. Defaults to "Complete".

    Returns:
        Dict[str, JobTiming]: Dictionary of completed jobs. Where JobTiming is a tuple
            (creation_time, completion_time, duration_in_seconds).
    """
    config.load_kube_config()
    batch_v1: client.BatchV1Api = client.BatchV1Api()
    watcher = watch.Watch()

    logfire.info(f"Tracking jobs with prefix '{prefix}' in namespace '{namespace}'")

    pending: Dict[str, bool] = {}
    done: Dict[str, JobTiming] = {}
    data = batch_v1.list_namespaced_job(namespace)
    version: str = data.metadata.resource_version

    for item in data.items:
        if item.metadata.name.startswith(prefix):
            pending[item.metadata.name] = True

    if not pending:
        logfire.info(f"No jobs found with prefix '{prefix}' in namespace '{namespace}'")
        logfire.info("Exiting...")
        return done

    logfire.info(f"Found {len(pending)} jobs.")
    logfire.info(f"Starting to track jobs to state {to_state}...")

    while any(pending.values()):
        start = datetime.now()
        for event in watcher.stream(
            batch_v1.list_namespaced_job,
            namespace=namespace,
            resource_version=version,
            timeout_seconds=600,
        ):
            logfire.debug(f"K8s Event: {event['type']}")
            logfire.debug(f"Revision: {event['object']}")
            item: client.V1Job = event["object"]
            version = item.metadata.resource_version
            name: str = item.metadata.name

            if name not in pending:
                continue

            if status(item, to_state):
                completion: datetime = item.status.completion_time
                creation: datetime = item.metadata.creation_timestamp
                duration: float = (completion - creation).total_seconds()
                msg = f"{name} reached state {to_state} in {duration:.2f} seconds."
                logfire.info(msg)
                done[name] = (creation, completion, duration)
                pending[name] = False

            logfire.info(f"Pending Jobs Left: {sum(pending.values())}")

            if sum(pending.values()) == 0:
                logfire.info(f"All jobs with prefix {prefix} reached state {to_state}")
                watcher.stop()
                break
            
            if (datetime.now() - start).seconds > 600:
                logfire.info("Timeout reached. Exiting...")
                watcher.stop()
                break
    return done
