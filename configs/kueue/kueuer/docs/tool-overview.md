# Kueuer tool overview

`kueuer` is a benchmarking and observation CLI for clusters that already have
Kueue installed. It helps you answer whether Kueue can survive large job
backlogs and whether Kueue changes control-plane behavior in ways that matter
for production.

## What the tool measures

The tool is organized around two concerns that matter for large batch systems:

1. **Scale handling:** Can Kueue admit, queue, preempt, and complete large
   numbers of jobs correctly?
2. **Control-plane load:** Do Kueue and the benchmark traffic increase API
   server latency, controller memory, restart counts, or queue wait times too
   much?

`benchmark` focuses on job behavior and scheduling outcomes. Top-level
`preflight` validates access and queue readiness, `benchmark e2e` collects the
control-plane observation data that explains those outcomes, and top-level
`teardown` cleans benchmark resources back up. `plot` renders the existing run
artifacts back into PNGs when you want to inspect or regenerate visuals.

## Profiles

Profiles give you named default resource settings for common use cases.

1. `local-safe` is the default profile. It uses short durations and small
   resource requests so you can validate behavior without putting heavy stress
   on a shared cluster.
2. `cluster-scale` is the larger profile. It uses more aggressive resource
   values and longer wait times so you can move closer to production-like
   pressure.

You can still override individual options such as `--duration`, `--cores`, or
`--jobs`. The profile only supplies the defaults.

## Run IDs and artifact layout

Artifact-producing commands default to `artifacts/<run_id>/...`. If you do not
pass `--run-id`, `kueuer` generates one from the current UTC time in
`YYYYMMDD-HHMMSS` format. This keeps separate runs isolated and makes it easy
to compare output directories.

If you pass a custom `--output-dir` to a standalone benchmark command, `kueuer`
writes directly into that directory instead of creating another run-id
subdirectory. Standalone benchmark plot commands are different: they derive
their output location from the input artifact path and write to a sibling
`plots/` directory automatically.

## Command groups

These are the user-facing command groups:

1. `benchmark`: Produce performance data, eviction data, or one fully processed
   end-to-end benchmark run.
2. `plot`: Render performance, eviction, and observation plots from benchmark
   outputs.
3. `jobs`: Launch or delete benchmark jobs directly.
4. `cluster`: Inspect aggregate node resources.

The public top-level workflow commands are:

1. `preflight`: Run access, Kueue health, and queue readiness checks.
2. `teardown`: Delete benchmark jobs and, optionally, queue objects.
