"""Track the status of Kubernetes Objects."""

import re
import statistics
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import logfire
from kubernetes import client, config, watch

# Type alias for job tracking: (creation_time, completion_time, duration_in_seconds)
JobTiming = Tuple[datetime, Optional[datetime], Optional[float]]

logfire.configure(send_to_logfire=False)

_PREEMPTOR_UID_RE = re.compile(r"UID:\s*([0-9a-fA-F-]+)")


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


def _parse_transition_time(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _extract_preemptor_uid(message: str) -> Optional[str]:
    match = _PREEMPTOR_UID_RE.search(message or "")
    if not match:
        return None
    return match.group(1).strip()


def _ensure_workload_record(
    workloads: Dict[str, Dict[str, Any]],
    uid: str,
    name: str,
    priority: int,
) -> Dict[str, Any]:
    if uid not in workloads:
        workloads[uid] = {
            "name": name,
            "priority": priority,
            "admitted_at": None,
            "finished_at": None,
            "requeues": 0,
            "preemptors": [],
            "eviction_reasons": [],
        }
    return workloads[uid]


def _apply_workload_conditions(
    workloads: Dict[str, Dict[str, Any]],
    seen_transitions: Dict[str, Set[Tuple[str, str, str, str, str]]],
    data: Dict[str, Any],
) -> bool:
    """Apply workload conditions once per state transition.

    Returns:
        bool: True if this update newly marked the workload as finished.
    """
    uid: str = str(data["metadata"]["uid"])
    name: str = str(data["metadata"]["name"])
    priority_raw = data.get("spec", {}).get("priority", 0)
    try:
        priority: int = int(priority_raw)
    except (TypeError, ValueError):
        priority = 0

    record = _ensure_workload_record(workloads, uid, name, priority)
    transitions = seen_transitions.setdefault(uid, set())
    newly_finished = False

    for condition in data.get("status", {}).get("conditions", []):
        ctype = str(condition.get("type", ""))
        cstatus = str(condition.get("status", ""))
        ctime = str(condition.get("lastTransitionTime", ""))
        creason = str(condition.get("reason", ""))
        cmessage = str(condition.get("message", ""))
        tkey = (ctype, cstatus, ctime, creason, cmessage)
        if tkey in transitions:
            continue
        transitions.add(tkey)

        transition_time = _parse_transition_time(condition.get("lastTransitionTime"))

        if ctype == "Admitted" and cstatus == "True":
            if record["admitted_at"] is None:
                record["admitted_at"] = transition_time
            logfire.info(f"{record.get('name')} admitted with priority {record.get('priority')}")

        elif ctype == "Evicted" and cstatus == "True":
            preemptor_uid = _extract_preemptor_uid(cmessage)
            if preemptor_uid:
                existing = {item[0] for item in record["preemptors"]}
                if preemptor_uid not in existing:
                    record["preemptors"].append((preemptor_uid, transition_time))
                    logfire.info(
                        f"{record.get('name')} evicted by {preemptor_uid}"
                    )
            if creason:
                record["eviction_reasons"].append(creason)

        elif ctype == "Finished" and cstatus == "True":
            if record["finished_at"] is None:
                record["finished_at"] = transition_time
                newly_finished = True
            logfire.info(f"{record.get('name')} succeeded.")

        elif ctype == "Requeued" and cstatus == "True":
            record["requeues"] += 1
            logfire.info(f"{record.get('name')} requeued.")

    return newly_finished


def evictions(
    namespace: str,
    revision: Optional[str] = None,
    prefix: Optional[str] = None,
):
    """Track the status of Kubernetes workloads.

    Args:
        namespace (str): Namespace of the workloads.
        revision (str): Optional starting resource version for watch.
        prefix (str): Optional name prefix filter for targeted benchmark workloads.

    Returns:
        Dict[str, Dict[str, Any]]: Workload information.
    """
    config.load_kube_config()
    crd: client.CustomObjectsApi = client.CustomObjectsApi()
    watcher = watch.Watch()
    workloads: Dict[str, Dict[str, Any]] = {}
    seen_transitions: Dict[str, Set[Tuple[str, str, str, str, str]]] = {}
    tracked: Set[str] = set()
    completed: Set[str] = set()

    initial = crd.list_namespaced_custom_object(  # type: ignore
        group="kueue.x-k8s.io",
        version="v1beta1",
        namespace=namespace,
        plural="workloads",
    )
    watch_version = (
        revision
        or str(initial.get("metadata", {}).get("resourceVersion", ""))
        or None
    )

    for item in initial.get("items", []):
        item_name = str(item.get("metadata", {}).get("name", ""))
        if prefix and prefix not in item_name:
            continue
        uid = str(item.get("metadata", {}).get("uid"))
        tracked.add(uid)
        if _apply_workload_conditions(workloads, seen_transitions, item):
            completed.add(uid)

    logfire.info(f"Tracking evictions in namespace '{namespace}'")
    for event in watcher.stream(  # type: ignore
        crd.list_namespaced_custom_object,  # type: ignore
        group="kueue.x-k8s.io",
        version="v1beta1",
        namespace=namespace,
        plural="workloads",
        resource_version=watch_version,
        timeout_seconds=600,
    ):
        logfire.debug(f"K8s Event: {event['type']}")
        data: Dict[str, Any] = event["object"]
        item_name = str(data.get("metadata", {}).get("name", ""))
        if prefix and prefix not in item_name:
            continue

        uid: str = str(data["metadata"]["uid"])
        tracked.add(uid)
        if _apply_workload_conditions(workloads, seen_transitions, data):
            completed.add(uid)

        if tracked and tracked.issubset(completed):
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
