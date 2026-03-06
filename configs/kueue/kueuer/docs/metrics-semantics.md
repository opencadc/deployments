# Metrics semantics

This page defines the most important benchmark and observation metrics in plain
language. Use it when you need to explain what a CSV column, observation field,
or policy check is actually measuring.

## Performance benchmark metrics

These metrics appear in `performance.csv`.

1. `completed_jobs_tracked`: Number of Jobs observed to completion by the
   tracker.
2. `completion_ratio`: Completed jobs divided by requested jobs.
3. `total_execution_time`: Wall-clock time for the whole experiment.
4. `avg_time_from_creation_completion`: Average job turnaround from Job object
   creation to completion.
5. `median_time_from_creation_completion`: Median job turnaround.
6. `std_dev_time_from_creation_completion`: Standard deviation of turnaround.
7. `total_time_from_first_creation_to_last_completion`: End-to-end span of the
   entire experiment.
8. `submission_jobs_applied`: Number of Job manifests successfully applied.
9. `submission_jobs_failed_to_apply`: Number of Jobs that never made it into
   the cluster because apply failed.
10. `pods_oomkilled`: Number of benchmark pods that terminated with
    `OOMKilled`.
11. `kueue_controller_restarts_delta`: Change in controller restart count
    during the experiment.

## Eviction benchmark metrics

These metrics appear in `evictions.yaml`.

1. `priority`: Numeric priority class value for the workload.
2. `admitted_at`: Timestamp when Kueue admitted the workload.
3. `finished_at`: Timestamp when the workload reached terminal state.
4. `requeues`: Number of times the workload was requeued.
5. `preemptors`: List of preempting workloads and timestamps.

## Observation metrics

These metrics appear in observation samples, summaries, and plots.

1. `kueue_controller_cpu_cores`: CPU usage reported by `kubectl top`.
2. `kueue_controller_memory_working_set_bytes`: Controller working-set memory
   reported by `kubectl top`.
3. `kueue_controller_restart_count`: Sum of controller container restart
   counters.
4. `apiserver_non_watch_request_p95_seconds`: Estimated API server non-watch
   request p95 from `/metrics`.
5. `apiserver_non_watch_request_p99_seconds`: Estimated API server non-watch
   request p99 from `/metrics`.
6. `apiserver_current_inflight_read_requests`: Current read-only inflight
   request count.
7. `apiserver_current_inflight_write_requests`: Current mutating inflight
   request count.
8. `pending_workloads`: Sum of LocalQueue pending workloads.
9. `admitted_workloads`: Sum of LocalQueue admitted workloads.
10. `workload_queue_wait_p50_seconds`: Median time from workload creation to
    admission.
11. `workload_queue_wait_p95_seconds`: P95 time from workload creation to
    admission.
12. `benchmark_oomkilled_pods`: Count of benchmark pods observed with
    `OOMKilled`.

## Policy interpretation

The observation policy is intentionally conservative because the tool is meant
to detect scale and control-plane risk early.

1. Missing telemetry does not count as success.
2. Controller memory above 2 GiB is a failure.
3. Non-zero controller restart delta is a failure.
4. Any benchmark pod OOM kill is a failure.
5. API server non-watch p95 latency growth above 20 percent relative to the
   optional baseline is a failure.
