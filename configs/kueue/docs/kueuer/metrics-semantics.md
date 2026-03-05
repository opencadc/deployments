# Kueuer metrics semantics

This document defines what `kueuer` metrics mean after Phase 1, what they do
not mean, and how you should interpret them.

## performance metrics

Performance outputs are written to CSV by `kr benchmark performance`.

### core fields

- `total_execution_time`: Wall-clock duration for one experiment from launch
  start to tracked completion.
- `avg_time_from_creation_completion`: Mean job-level turnaround from Kubernetes
  Job `creationTimestamp` to Job completion timestamp.
- `median_time_from_creation_completion`: Median of per-job turnaround values.
- `std_dev_time_from_creation_completion`: Standard deviation of per-job
  turnaround values.

### derived fields in plotting

- `throughput`: `job_count / total_execution_time`.
- `first_job_turnaround_s`: `first_completion_time - first_creation_time`.
- `tail_job_turnaround_s`: `last_completion_time - last_creation_time`.
- `startup_latency` and `completion_latency`: backward-compatible aliases for
  the two turnaround fields above.
- `scheduling_overhead`: `first_job_turnaround_s - configured_job_duration`.

### interpretation caveats

These are end-to-end workload timing proxies. They are not direct scheduler
latency metrics and they include queueing, scheduling, runtime, and control
plane effects.

## eviction metrics

Eviction outputs are written to YAML by `kr benchmark evictions`.

Each tracked workload includes:

- `name`
- `priority`
- `admitted_at`
- `finished_at`
- `requeues`
- `preemptors`
- `eviction_reasons`

### phase 1 semantic improvements

1. Condition handling is transition-aware. Replayed watch states are ignored.
2. `Admitted=True` no longer resets accumulated workload tracking state.
3. `requeues` increments only on new `Requeued=True` transitions.
4. `admitted_at` and `finished_at` prefer condition transition timestamps.
5. Missing preemptor metadata no longer crashes analysis.

## data integrity guarantees added in phase 1

- Repeated checkpoint writes to performance CSV are idempotent.
- Duplicate-row inflation from cumulative append behavior is removed.
- Eviction watch analysis is robust to partial metadata and replayed events.

## known limitations after phase 1

- Untuned local stress profiles can still trigger API and webhook instability.
- Current metrics are still benchmark-level proxies, not full apiserver/
  controller telemetry.
- Additional observability for control-plane latency and Kueue controller memory
  growth is planned for later phases.

## next steps

In the next phase, add explicit control-plane metrics and richer lifecycle
partitioning to separate queue wait, admission delay, and runtime effects.
