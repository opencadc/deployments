# Kueuer tool overview

`kueuer` is a Python CLI toolkit for benchmarking Kubernetes batch execution with
and without Kueue. It is designed to help platform teams validate queueing,
admission behavior, and stress response before production rollout changes.

## command groups

`kr` exposes these command groups.

1. `benchmark`: performance and eviction benchmarks.
2. `jobs`: raw job launch and cleanup helpers.
3. `plot`: plotting utilities for benchmark outputs.
4. `cluster`: node resource aggregation helper.

## main benchmark modes

### performance benchmark

This mode runs paired experiments for each job count.

- direct Kubernetes scheduling run
- Kueue-enabled run

It collects wall-clock and job-level turnaround metrics into CSV output.

### eviction benchmark

This mode launches multi-priority workloads to observe preemption and requeue
behavior in packed conditions. It tracks Workload condition transitions and
writes YAML output for analysis.

## intended usage in this repository

In this repository, `kueuer` is the measurement tool used to evaluate the
Kueue deployment behavior defined in `dev/` and `prod/` configuration sets.

Use `docs/kueuer/phase-1-implementation.md` for concrete commands and
`docs/kueuer/metrics-semantics.md` for interpretation details.

## plotting behavior after phase 1

Plot commands now support non-interactive output by default and can save image
files directly.

- `kr plot performance <results.csv> --output-dir <dir> --no-show`
- `kr plot evictions <evictions.yaml> --output-dir <dir> --no-show`

Use `--show` if you explicitly want interactive windows.
