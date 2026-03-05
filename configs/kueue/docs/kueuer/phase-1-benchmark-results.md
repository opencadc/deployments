# Phase 1 benchmark results

This document summarizes baseline and post-change benchmark results for Phase 1.
The purpose is to validate data integrity fixes first, then discuss observed
runtime behavior.

## integrity outcomes

Phase 1 fixed the primary output integrity issue in performance results.

- Baseline performance rows: `78`
- Post performance rows: `12`
- Baseline duplicate rows: `66`
- Post duplicate rows: `0`
- Duplicate reduction: `66`

These values are generated in:

- `artifacts/phase1/comparison/phase1_delta_summary.json`
- `artifacts/phase1/comparison/phase1_delta_report.md`

## performance means (context only)

Mean values below are informational. Baseline values are biased by duplicate
rows from pre-fix behavior, so they are not clean performance regressions.

- Direct baseline mean total execution: `12.54s`
- Direct post mean total execution: `13.02s`
- Kueue baseline mean total execution: `10.28s`
- Kueue post mean total execution: `14.84s`

## eviction tracking outcomes

Eviction tracking quality improved materially.

- Baseline tracked workloads: `1`
- Post tracked workloads: `18`
- Post tuned tracked workloads: full multi-priority set with clean completion
  signal in runtime logs

Both untuned runs experienced intermittent API/webhook instability under burst
load. Post-change tracking still captured targeted workload progression, which
was not true in baseline.

## OOM and local profile guidance

During untuned runs, `OOMKilled` pods were observed in the local environment.
That behavior is expected when aggregate memory pressure is high relative to
node capacity.

The tuned profile used in this phase reduces per-job resources:

- Total eviction RAM: `2GB` for `8` jobs
- Effective RAM per job: `0.25GB`
- Total eviction storage: `2GB` for `8` jobs
- Effective storage per job: `0.25GB`

Use this tuned profile for local reproducibility before moving to larger stress
profiles.

A post-phase pod snapshot is stored in `artifacts/phase1/post/pods_after_phase1.txt`.
That snapshot also showed Kueue controller restarts, which should be tracked as
an explicit stability signal in the next phase.

## what this phase proves

Phase 1 proves measurement correctness improvements:

1. Performance checkpoints are now idempotent.
2. Eviction tracking no longer collapses to minimal stale workload data.
3. Condition replay no longer inflates counters from repeated watch updates.

Phase 1 does not yet prove production-scale scheduler efficiency. That requires
Phase 2 and later observability phases with stronger control-plane telemetry.
