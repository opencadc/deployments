"""Scenario helpers for lifecycle suite execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List

from kueuer.lifecycle.shell import run_command


def _constrained_queue_manifest(
    namespace: str,
    localqueue: str,
    clusterqueue: str,
) -> str:
    return "\n".join(
        [
            "apiVersion: kueue.x-k8s.io/v1beta1",
            "kind: ClusterQueue",
            "metadata:",
            f"  name: {clusterqueue}",
            "spec:",
            "  namespaceSelector: {}",
            "  resourceGroups:",
            "  - coveredResources: [\"cpu\", \"memory\", \"ephemeral-storage\"]",
            "    flavors:",
            "    - name: default",
            "      resources:",
            "      - name: cpu",
            '        nominalQuota: "1"',
            "      - name: memory",
            '        nominalQuota: "1Gi"',
            "      - name: ephemeral-storage",
            '        nominalQuota: "2Gi"',
            "---",
            "apiVersion: kueue.x-k8s.io/v1beta1",
            "kind: LocalQueue",
            "metadata:",
            f"  name: {localqueue}",
            f"  namespace: {namespace}",
            "spec:",
            f"  clusterQueue: {clusterqueue}",
            "",
        ]
    )


def _scenario_queue_names(
    localqueue: str,
    clusterqueue: str,
) -> tuple[str, str]:
    return (f"{localqueue}-backlog", f"{clusterqueue}-backlog")


def apply_scenario(
    scenario: str,
    output_dir: str,
    namespace: str,
    localqueue: str,
    clusterqueue: str,
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    if scenario == "control":
        return {
            "scenario": scenario,
            "applied": False,
            "queue_before": "",
            "queue_after": "",
            "errors": [],
        }

    if scenario != "backlog":
        return {
            "scenario": scenario,
            "applied": False,
            "queue_before": "",
            "queue_after": "",
            "errors": [f"Unsupported scenario: {scenario}"],
        }

    before_path = root / "queue-before.yaml"
    after_path = root / "queue-after.yaml"
    errors: List[str] = []
    scenario_localqueue, scenario_clusterqueue = _scenario_queue_names(
        localqueue=localqueue,
        clusterqueue=clusterqueue,
    )
    before_path.write_text("# no shared queue state modified\n", encoding="utf-8")

    after_path.write_text(
        _constrained_queue_manifest(
            namespace=namespace,
            localqueue=scenario_localqueue,
            clusterqueue=scenario_clusterqueue,
        ),
        encoding="utf-8",
    )

    apply_res = run_cmd(["kubectl", "apply", "-f", after_path.as_posix()])
    if apply_res.returncode != 0:
        errors.append("failed to apply backlog queue manifest")

    return {
        "scenario": scenario,
        "applied": apply_res.returncode == 0,
        "queue_before": before_path.as_posix(),
        "queue_after": after_path.as_posix(),
        "localqueue": scenario_localqueue,
        "clusterqueue": scenario_clusterqueue,
        "errors": errors,
    }


def restore_scenario(
    context: Dict[str, Any],
    run_cmd: Callable[[List[str]], Any] = run_command,
) -> Dict[str, Any]:
    before = str(context.get("queue_before", ""))
    after = str(context.get("queue_after", ""))
    if after:
        result = run_cmd(["kubectl", "delete", "-f", after, "--ignore-not-found=true"])
        if result.returncode != 0:
            return {
                "restored": False,
                "error": result.stderr.strip() or "failed to delete scenario queues",
            }
        return {"restored": True, "error": ""}
    if not before:
        return {"restored": False, "error": ""}

    result = run_cmd(["kubectl", "apply", "-f", before])
    if result.returncode != 0:
        return {
            "restored": False,
            "error": result.stderr.strip() or "failed to restore queue manifests",
        }
    return {"restored": True, "error": ""}
