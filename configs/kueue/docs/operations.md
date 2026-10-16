# CANFAR Kueue operations appendix

This document defines the operational model for the CANFAR Kueue architecture.
It covers SLOs, observability, alerting, runbooks, rollout, and rollback. Use
it together with [architecture.md](./architecture.md), [roadmap.md](./roadmap.md),
[ui-spec.md](./ui-spec.md), and [the ADR index](./adrs/README.md).

## 1. Operational objectives

The Kueue platform must remain understandable and recoverable under pressure.
Operators need to know whether the problem is in Kueue, the Kubernetes API, the
submission path, or the workload mix itself.

This appendix therefore focuses on:

- service-level objectives
- the metrics and dashboards that support those objectives
- incident runbooks
- safe rollout and rollback mechanics

## 2. Service Level Indicators (SLIs) and Objectives (SLOs)

The following SLOs form the initial operating contract. They are subject to
refinement after benchmark evidence is gathered.

### 2.1 Submission and admission SLOs

| SLI | Target |
| --- | ------ |
| `skaha` successful submission response rate | `>= 99.9%` over 30 days |
| `skaha` P95 create-session latency under nominal load | `<= 2s` |
| Kueue P95 admission wait for interactive workloads under nominal conditions | `<= 30s` |
| Kueue P95 admission wait for standard batch under nominal backlog | `<= 10m` |
| Visibility API P95 latency for paged pending queries | `<= 2s` |

### 2.2 Control-plane health SLOs

| SLI | Target |
| --- | ------ |
| Kueue controller availability | `>= 99.95%` over 30 days |
| Zero unplanned controller crash loops | Required |
| Kubernetes API P99 write latency for workload creation under nominal load | `<= 1s` |
| Kubernetes API P99 read latency for queue visibility queries | `<= 1s` |

### 2.3 Fairness and stability SLOs

| SLI | Target |
| --- | ------ |
| Unexplained pending-state responses in UI | `0` |
| Preemptions without user-visible reason category | `0` |
| Queue-policy changes without rollback path | `0` |
| Benchmark-backed backlog ceiling published and current | Required |

## 3. Metrics and dashboards

The platform needs dashboards that show both tenant policy and control-plane
health. Kueue metrics alone are not enough.

### 3.1 Required metrics

Use Kueue, Kubernetes, and platform metrics together. Important Kueue metrics
include:

- `kueue_pending_workloads`
- `kueue_admission_wait_time_seconds`
- `kueue_cluster_queue_resource_usage`
- `kueue_cluster_queue_nominal_quota`
- `kueue_evicted_workloads_total`
- `kueue_local_queue_evicted_workloads_total`
- `kueue_admitted_workloads_total`
- `kueue_finished_workloads_total`

Important Kubernetes and control-plane metrics include:

- apiserver request latency and error metrics
- etcd latency and saturation indicators
- controller pod restart count and RSS memory
- scheduler latency for admitted workloads
- `Skaha` request latency and error rate

### 3.2 Required dashboards

Create the following dashboards at minimum:

- Community ownership and quota view
- Project fair-share and queue-position view
- Pending workload health by class and queue
- Admission latency and throughput
- Preemption and eviction reason view
- Controller and API-server health
- End-to-end submission latency

### 3.3 Ownership

Dashboard ownership must be explicit:

- Platform team owns Kueue, Kubernetes API, and rollout health dashboards
- `Skaha` owners own submission-path latency and error dashboards
- Future control-service owners own tenant and override workflow dashboards

## 4. Alerts

Alerts must drive action, not noise. Each alert needs a linked runbook.

### 4.1 High-severity alerts

- Kueue controller unavailable or crash looping
- Kubernetes API write latency above threshold for sustained periods
- Visibility API unavailable or returning sustained errors
- Preemption storm above agreed threshold
- Shared `workloads` namespace submission failures above threshold

### 4.2 Medium-severity alerts

- Kueue controller memory growth beyond normal envelope
- Pending backlog growing while admission throughput collapses
- Community reclaim behavior not restoring owned capacity in time
- Fair-share override still active past approved window

### 4.3 Low-severity alerts

- Project or community configuration drift
- Dashboard ingestion gaps
- Non-critical benchmark regression signals

## 5. Runbooks

These runbooks define the minimum operational response set.

### 5.1 API slowness or admission collapse

Symptoms:

- `Skaha` create requests slow down
- Kueue admission wait time rises across multiple workload classes
- Kubernetes API latency or error rate rises

Actions:

1. Confirm whether the bottleneck is `Skaha`, Kueue, apiserver, or etcd.
2. Check Kueue controller restarts, memory, and work-queue saturation.
3. Check apiserver latency and request load by verb and resource.
4. Reduce new batch pressure if the submission path is part of the problem.
5. Capture the incident state for later benchmark comparison.

### 5.2 Kueue memory pressure

Symptoms:

- controller RSS grows rapidly
- controller pod restarts or is OOM-killed

Actions:

1. Inspect backlog size, active queue count, and recent submission burst.
2. Check whether API latency is causing request buildup.
3. Reduce submission pressure if required.
4. Apply emergency queue hold or drain policy only if the system cannot recover
   safely.
5. Record controller configuration and backlog context for follow-up analysis.

### 5.3 Queue stall or unfairness complaint

Symptoms:

- users report that workloads are not moving
- one project appears to dominate or starve unexpectedly

Actions:

1. Inspect the affected `LocalQueue` and community `ClusterQueue`.
2. Confirm project fair-share weights and recent usage history.
3. Confirm workload priorities inside the project.
4. Confirm whether the issue is community reclaim, project fair share, or lack
   of physical resources.
5. Communicate the cause using the standard pending explanation categories.

### 5.4 Preemption storm

Symptoms:

- rapid increase in preempted or evicted workloads
- user complaints about unstable interactive or persistent work

Actions:

1. Confirm whether the preemptions are due to community reclaim, project-local
   priority, or protection policy misconfiguration.
2. Check recent weight overrides and policy changes.
3. Pause further policy rollout until the behavior is understood.
4. Revert the triggering policy if needed.

### 5.5 Visibility failure

Symptoms:

- UI cannot explain pending reasons
- pending-workloads visibility API times out or returns errors

Actions:

1. Confirm whether the failure is in the UI, metrics layer, or visibility API.
2. Fall back to `kubectl` and Grafana-based diagnosis.
3. Restore the visibility service before resuming major policy changes.

## 6. Rollout

Every Kueue upgrade or policy change must follow a controlled rollout.

### 6.1 Rollout steps

1. Validate the change in a non-production environment.
2. Capture pre-change benchmarks and key health metrics.
3. Apply the change through the source-of-truth deployment method.
4. Watch controller health, admission timing, and API latency.
5. Verify queue visibility and pending explanation behavior.
6. Run a defined smoke test for interactive and batch submission.
7. Mark the rollout complete only after the health window closes cleanly.

### 6.2 Rollout guardrails

- Do not change fairness and preemption policy during an unresolved incident.
- Do not combine Kueue upgrades with unrelated tenant policy changes unless the
  rollback method covers both.
- Do not announce a new backlog ceiling without fresh benchmark evidence.

## 7. Rollback

Rollback must be designed before rollout begins.

### 7.1 Rollback triggers

- repeated controller restarts
- sustained admission collapse
- unacceptable API latency regression
- broken queue visibility
- unexpected preemption of protected workload classes

### 7.2 Rollback steps

1. Stop further policy changes.
2. Revert the deployment or configuration to the last known-good state.
3. Confirm controller stability and API recovery.
4. Verify that queue visibility still works.
5. Record the incident details and the exact rollback trigger.

## 8. Evidence and reporting

Operational claims must be backed by evidence. Keep the following artifacts for
major changes:

- benchmark results and plots
- controller and API latency dashboards
- admission wait time summaries by workload class
- preemption and eviction summaries
- incident notes and rollback evidence when applicable

These artifacts are release inputs, not optional attachments.
