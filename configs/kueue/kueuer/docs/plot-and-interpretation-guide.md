# Plot and interpretation guide

This guide explains what the generated plots mean and how to read them in the
context of large-job-count Kueue validation. The goal is not only to see
whether jobs complete, but also to understand whether Kueue changes throughput,
queue behavior, or control-plane stability in unacceptable ways.

## Generate plots

Standalone benchmark plots require an explicit output directory.

```bash
RUN_ID="<your-run-id>"

uv run kr plot performance \
  "artifacts/$RUN_ID/performance.csv" \
  --output-dir "artifacts/$RUN_ID/plots/performance" \
  --show

uv run kr plot evictions \
  "artifacts/$RUN_ID/evictions.yaml" \
  --output-dir "artifacts/$RUN_ID/plots/evictions" \
  --show

uv run kr observe plot \
  --run-id "$RUN_ID" \
  --output-dir "artifacts/$RUN_ID/plots/observe" \
  --show
```

Lifecycle `collect` and `e2e` generate the same plot families automatically
when the required input files exist.

## Performance plots

Performance plots help you decide whether Kueue changes throughput or
completion behavior under increasing job counts.

1. `throughput_comparison.png`: Higher is better. This is the main signal for
   whether Kueue keeps up with queue load.
2. `first_job_turnaround_comparison.png`: Lower is better. A rising first-job
   turnaround can indicate admission or controller overhead.
3. `tail_job_turnaround_comparison.png`: Lower is better. This matters more
   than the first-job plot for large queues because it exposes backlog drag.
4. `cv_of_job_durations.png`: Lower is better. High variance can indicate
   unstable admission or noisy cluster conditions.
5. `job_duration_distribution.png`: Look for shifts or widening tails between
   direct and Kueue-managed runs.
6. `job_completion_times.png`: Use this to see how completion time scales with
   job count and whether the Kueue trend diverges.
7. `scaling_efficiency.png`: Flattening or dropping throughput at higher counts
   can indicate scheduler or API bottlenecks.
8. `scheduling_overhead.png`: Higher overhead means more time spent outside the
   actual stress-job runtime.

## Eviction plots

Eviction plots help you verify that queue pressure does not produce obviously
wrong priority behavior.

1. `evictions_by_priority.png`: Lower-priority jobs should absorb more
   preemption pressure than higher-priority jobs.
2. `job_start_end_timeline.png`: Use the time ordering to spot bursty or
   stalled admission patterns.
3. `evictions_heatmap.png`: Concentrated hot spots can reveal unstable queue
   behavior during pressure spikes.
4. `requeues_by_priority.png`: High-priority jobs should not show a surprising
   amount of requeue churn.

## Observation plots

Observation plots are the control-plane view of the same run. They matter when
Kueue appears functionally correct but may still overload the cluster.

1. `kueue_controller_memory.png`: Watch for sustained high memory growth or
   step changes that suggest controller pressure.
2. `kueue_controller_cpu.png`: Use this to correlate queue events with
   controller activity.
3. `apiserver_latency.png`: Rising non-watch p95 latency is one of the clearest
   signals that the benchmark is stressing the control plane too hard.
4. `queue_depth.png`: Queue depth helps explain whether latency increases are
   tied to admission backlog.

## Read plots against policy

Do not read plots in isolation. Cross-check them with the observation policy
artifacts:

1. `observe/summary.json` for aggregated metrics
2. `observe/policy.json` for pass/fail policy evaluation
3. `observe/report.md` for a compact Markdown summary
