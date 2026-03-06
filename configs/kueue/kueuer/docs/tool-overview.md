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

`benchmark` focuses on job behavior and scheduling outcomes. `observe` focuses
on control-plane attribution. `lifecycle` ties them together into a repeatable
workflow for preflight checks, suite execution, artifact collection, and
cleanup.

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
subdirectory. Plot commands are different: they always require an explicit
`--output-dir`.

## Command groups

These are the user-facing command groups:

1. `benchmark`: Produce performance and eviction benchmark data.
2. `plot`: Render performance and eviction plots from benchmark outputs.
3. `lifecycle`: Run cluster preflight checks, execute suites, collect outputs,
   and tear down benchmark resources.
4. `observe`: Collect, plot, analyze, and report control-plane observations.
5. `jobs`: Launch or delete benchmark jobs directly.
6. `cluster`: Inspect aggregate node resources.

## Next steps

Use the CLI reference to choose the right command surface for your workflow:

1. [`cli-reference.md`](/Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer/docs/cli-reference.md)
2. [`benchmark-walkthrough.md`](/Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer/docs/benchmark-walkthrough.md)
