"""Analyze Kueue Workload Eviction Data."""

from typing import Any, Dict

from kueuer.utils.logging import logger


def evictions(workloads: Dict[str, Dict[str, Any]]) -> bool:
    """Analyzes Kueue workload data, printing the outcome of each preemption
    (eviction) returns a list of priority rule violations.

    Args:
        workloads: A dictionary where keys are workload UIDs (str) and values are
            dictionaries containing workload information.

    Returns:
        bool: True if any priority violations are found, False otherwise.
    """
    logger.info("🕵️ Starting Preemption Priority Analysis")
    violations: bool = False

    for uid, workload in workloads.items():
        # Only check workloads that were actually requeued (implying preemption)
        if workload.get("requeues", 0) > 0:
            preempted_priority = int(workload.get("priority"))  # type: ignore
            preempted_name = workload.get("name", uid)  # Use name if available

            logger.info(
                "🧐 Checking: '%s' (%s) - Priority %d",
                preempted_name,
                uid,
                preempted_priority,
            )

            for preemptor in workload.get("preemptors", []):
                preemptor_uid, _eviction_time = preemptor[0], preemptor[1]

                # Find the data for the preempting workload
                data = workloads.get(preemptor_uid)
                if not data:
                    logger.warning(
                        "⚠️  Missing preemptor metadata for UID '%s'; skipping priority comparison.",
                        preemptor_uid,
                    )
                    continue
                name = str(data.get("name", preemptor_uid))
                priority = int(data.get("priority", 0))  # type: ignore

                # *** The Core Analysis Logic & Printing ***
                if priority > preempted_priority:
                    # Correct Preemption
                    logger.info(
                        " ✅ OK: Evicted by '%s' (%s) with %d",
                        name,
                        preemptor_uid,
                        priority,
                    )
                else:
                    violations = True
                    logger.error(
                        "  ❌ VIOLATION: Evicted by '%s' (%s) with %d",
                        name,
                        preemptor_uid,
                        priority,
                    )
    if violations:
        logger.info("🔴 Found potential priority violations.")
    else:
        logger.info("🟢 No preemption priority violations detected.")
    return violations
