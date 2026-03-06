# Metrics semantics

This page defines the most important benchmark and observation metrics in plain
language. Use it when you need to explain what a CSV column, observation field,
or policy check is actually measuring.

## Primary decision metrics

These metrics are the ones that most directly answer the two package goals:
whether Kueue scales to very large queues, and whether it creates unacceptable
control-plane pressure while doing so.

### Performance benchmark metrics

These metrics appear in `performance.csv` or are derived directly from it.

1. `throughput`: Completed jobs per second for the full experiment.
2. `completion_ratio`: Completed jobs divided by requested jobs.
3. `tail_job_turnaround_s`: Time from the last Job creation to the last Job
   completion.
4. `turnaround_overhead_s`: Average turnaround minus requested job runtime.
   This isolates queueing and scheduling overhead from the stress workload
   itself.

### Observation metrics

These metrics appear in observation samples, summaries, and plots.

1. `kueue_controller_memory_working_set_bytes`: Controller working-set memory
   reported by `kubectl top`.
2. `kueue_controller_cpu_cores`: Controller CPU usage reported by `kubectl top`.
3. `apiserver_non_watch_request_p95_seconds`: Estimated API server non-watch
   request p95 from `/metrics`.
4. `pending_workloads`: Sum of LocalQueue pending workloads.
5. `workload_queue_wait_p95_seconds`: P95 time from workload creation to
   admission.

## Supporting raw metrics

These metrics are still useful, but they are better for diagnosis than for the
top-level pass or fail decision.

### Performance benchmark supporting metrics

1. `completed_jobs_tracked`: Number of Jobs observed to completion by the
   tracker.
2. `total_execution_time`: Wall-clock time for the whole experiment.
3. `avg_time_from_creation_completion`: Average job turnaround from Job object
   creation to completion.
4. `median_time_from_creation_completion`: Median job turnaround.
5. `std_dev_time_from_creation_completion`: Standard deviation of turnaround.
6. `total_time_from_first_creation_to_last_completion`: End-to-end span of the
   entire experiment.
7. `submission_jobs_applied`: Number of Job manifests successfully applied.
8. `submission_jobs_failed_to_apply`: Number of Jobs that never made it into
   the cluster because apply failed.
9. `pods_oomkilled`: Number of benchmark pods that terminated with
   `OOMKilled`.
10. `kueue_controller_restarts_delta`: Change in controller restart count
   during the experiment.

## Eviction benchmark metrics

These metrics appear in `evictions.yaml`.

1. `priority`: Numeric priority class value for the workload.
2. `admitted_at`: Timestamp when Kueue admitted the workload.
3. `finished_at`: Timestamp when the workload reached terminal state.
4. `requeues`: Number of times the workload was requeued.
5. `preemptors`: List of preempting workloads and timestamps.

### Observation supporting metrics

1. `kueue_controller_restart_count`: Sum of controller container restart
   counters.
2. `apiserver_non_watch_request_p99_seconds`: Estimated API server non-watch
   request p99 from `/metrics`.
3. `apiserver_current_inflight_read_requests`: Current read-only inflight
   request count.
4. `apiserver_current_inflight_write_requests`: Current mutating inflight
   request count.
5. `admitted_workloads`: Sum of LocalQueue admitted workloads.
6. `workload_queue_wait_p50_seconds`: Median time from workload creation to
   admission.
7. `benchmark_oomkilled_pods`: Count of benchmark pods observed with
   `OOMKilled`.

## Metrics no longer treated as first-class plots

The tool still preserves raw benchmark and observation data, but it no longer
elevates every derivable field into a top-level plot. In particular, the
earlier first-job turnaround, generic duration distribution, and CV views were
weaker decision signals than completion ratio, tail turnaround, and queue wait
pressure, so they are no longer the default emphasis in the plot set.

## Policy interpretation

The observation policy is intentionally conservative because the tool is meant
to detect scale and control-plane risk early.

1. Missing telemetry does not count as success.
2. Controller memory above 2 GiB is a failure.
3. Non-zero controller restart delta is a failure.
4. Any benchmark pod OOM kill is a failure.
5. API server non-watch p95 latency growth above 20 percent relative to the
   optional baseline is a failure.
