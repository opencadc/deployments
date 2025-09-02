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


def evictions(
    namespace: str,
    revision: str,
):
    """Track the status of Kubernetes workloads.

    Args:
        namespace (str): Namespace of the workloads.
        revision (str): K8s resource version to start tracking from.

    Returns:
        Dict[str, Dict[str, Any]]: Workload information.
    """
    config.load_kube_config()
    crd: client.CustomObjectsApi = client.CustomObjectsApi()
    watcher = watch.Watch()
    workloads: Dict[str, Dict[str, Any]] = {}
    completed: int = 0
    logfire.info(f"Tracking evictions in namespace '{namespace}'")
    for event in watcher.stream(  # type: ignore
        crd.list_namespaced_custom_object,  # type: ignore
        group="kueue.x-k8s.io",
        version="v1beta1",
        namespace=namespace,
        plural="workloads",
        resource_version=revision,
        timeout_seconds=600,
    ):
        logfire.debug(f"K8s Event: {event['type']}")
        data: Dict[str, Any] = event["object"]
        uid: str = str(data["metadata"]["uid"])

        for condition in data.get("status", {}).get("conditions", []):
            if condition["type"] == "Admitted" and condition["status"] == "True":
                name: str = str(data["metadata"]["name"])
                priority: str = str(data["spec"]["priority"])
                workloads[uid] = {
                    "name": name,
                    "priority": int(priority),
                    "admitted_at": datetime.now(),
                    "finished_at": None,
                    "requeues": 0,
                    "preemptors": [],
                }
                logfire.info(f"{name} admitted with priority {priority}")

            if condition["type"] == "Evicted" and condition["status"] == "True":
                preemptor: str = (
                    condition.get("message", "").split("UID: ")[1].split(")")[0].strip()
                )
                details: Tuple[str, datetime] = (preemptor, datetime.now())
                if details[0] not in [
                    preemptor[0] for preemptor in workloads[uid]["preemptors"]
                ]:
                    workloads[uid]["preemptors"].append(details)
                    logfire.info(
                        f"{workloads.get(uid, {}).get('name')} evicted by {preemptor}"
                    )

            elif condition["type"] == "Finished" and condition["status"] == "True":
                workloads[uid]["finished_at"] = datetime.now()
                completed += 1
                logfire.info(f"{workloads.get(uid, {}).get('name')} succeeded.")

            elif condition["type"] == "Requeued" and condition["status"] == "True":
                workloads[uid]["requeues"] += 1
                logfire.info(f"{workloads.get(uid, {}).get('name')} requeued.")

        if workloads and completed == len(workloads):
            logfire.info("All workloads finished.")
            watcher.stop()

    return workloads


def jobs(  # noqa: C901
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

    # There is an edge case, where jobs can finish even before we start tracking them.
    # So, we need to check if any of the jobs are already in the desired state.
    for item in data.items:
        if item.metadata.name in pending and status(item, to_state):
            completion: datetime = item.status.completion_time
            creation: datetime = item.metadata.creation_timestamp
            duration: float = (completion - creation).total_seconds()
            msg = f"{item.metadata.name} reached {to_state} in {duration:.2f} seconds."
            logfire.info(msg)
            done[item.metadata.name] = (creation, completion, duration)
            pending[item.metadata.name] = False

    logfire.info(f"{len(pending)} jobs need to be tracked.")
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

            logfire.debug(f"Pending Jobs Left: {sum(pending.values())}")

            if sum(pending.values()) == 0:
                logfire.info(f"All jobs with prefix {prefix} reached state {to_state}")
                watcher.stop()
                break

            if (datetime.now() - start).seconds > 600:
                logfire.info("Timeout reached. Exiting...")
                watcher.stop()
                break
    return done
