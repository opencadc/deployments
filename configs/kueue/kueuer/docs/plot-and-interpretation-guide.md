# Plot and interpretation guide

This guide explains what the generated plots mean and how to read them in the
context of large-job-count Kueue validation. The goal is not only to see
whether jobs complete, but also to understand whether Kueue changes throughput,
queue behavior, or control-plane stability in unacceptable ways.

## Generate plots

Standalone benchmark plot commands infer `artifacts/<run_id>/plots/` from the
input artifact path.

```bash
RUN_ID="<your-run-id>"

uv run kr plot performance \
  "artifacts/$RUN_ID/performance/performance.csv" \
  --show

uv run kr plot evictions \
  "artifacts/$RUN_ID/evictions/evictions.yaml" \
  --show

uv run kr plot observations \
  "artifacts/$RUN_ID/observe/timeseries.csv" \
  --show
```

Lifecycle `collect` and `e2e` generate the same plot families automatically
when the required input files exist.

## Performance plots

Performance plots now focus on the four questions that matter most for queue
scale validation.

1. `performance_overview.png`: Read this first. It combines throughput,
   completion ratio, tail turnaround, and non-runtime overhead into one
   decision dashboard.
2. `throughput_by_job_count.png`: Higher is better. This is the clearest signal
   for whether Kueue keeps up with very large queues.
3. `completion_ratio_by_job_count.png`: This must stay close to `100%`. Any
   drop means the system is not reliably finishing the requested work.
4. `tail_turnaround_by_job_count.png`: Lower is better. This is the best plot
   for spotting backlog drag as the queue gets large.
5. `turnaround_overhead_by_job_count.png`: Lower is better. This isolates
   queueing and scheduling overhead from the actual job runtime.

## Eviction plots

Eviction plots now focus on whether Kueue preserves priority behavior under
pressure instead of emitting loosely related summaries.

1. `eviction_pressure_by_priority.png`: Lower-priority workloads should absorb
   most eviction and requeue pressure.
2. `workload_runtime_timeline.png`: Use this to see when workloads are admitted,
   when they finish, and where eviction events interrupt them.
3. `eviction_heatmap.png`: Concentrated hot spots reveal bursty pressure or
   unstable preemption waves.

## Observation plots

Observation plots are the control-plane view of the same run. They answer the
second core question: whether Kueue overloads Kubernetes while handling queue
scale.

1. `observation_overview.png`: Read this first. It provides the compact view of
   controller memory, controller CPU, API server p95, and pending workloads.
2. `controller_resource_overview.png`: Watch for sustained high memory growth,
   crossing the 2 GiB memory guardrail, or CPU spikes that stay elevated.
3. `apiserver_pressure.png`: Rising non-watch p95 latency is the clearest
   control-plane risk signal. Inflight request counts help explain why.
4. `queue_pressure.png`: Queue depth and queue-wait signals show whether
   latency changes match admission backlog.

## Read plots against policy

Do not read plots in isolation. Cross-check them with the consolidated
observation report artifact:

1. `observe/report.json` for aggregate metrics, pass/fail checks, and
   violations
