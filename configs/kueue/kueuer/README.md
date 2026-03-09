# Kueuer

`kueuer` is a Python CLI for evaluating Kueue on real Kubernetes clusters.
It is built around two operational questions:

1. Can Kueue handle very large batch queues without breaking admission and
   eviction behavior?
2. Does Kueue add unacceptable load to the Kubernetes control plane while it
   does that work?

The package gives you benchmark commands, lifecycle automation, and plotting
tools that write their artifacts under `artifacts/` by default.

## What the tool does

`benchmark` measures queue behavior directly. `lifecycle` ties benchmark runs
to control-plane observation collection, analysis, reporting, preflight
checks, artifact collection, and cleanup. `plot` renders benchmark,
eviction, and observation PNGs from existing run artifacts.

That split maps directly to the two main concerns:

1. Queue-scale correctness: throughput, completion ratio, tail turnaround,
   evictions, and requeues.
2. Control-plane burden: controller CPU and memory, API server latency, and
   queue wait pressure.

## Profiles, Run IDs, and artifacts

Profiles are named bundles of benchmark defaults.

1. `local-safe` is the default, low-risk smoke-test profile.
2. `cluster-scale` is the heavier profile for more realistic queue pressure.

Run-producing commands write to `artifacts/<run_id>/...` by default. If you do
not pass `--run-id`, `kueuer` generates a UTC timestamp such as
`20260306-230629`. Standalone benchmark commands also accept `--output-dir`,
which defaults to `artifacts`.

## Install

Install the package in a virtual environment before you run benchmarks.

```bash
git clone https://github.com/opencadc/deployments.git
cd deployments/configs/kueue/kueuer
uv sync
uv run kr --help
```

## Quick start

Use an explicit `run-id` when you want reproducible paths in notes or issue
reports.

```bash
cd /Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer
RUN_ID="$(date -u +%Y%m%d-%H%M%S)"

uv run kr benchmark performance \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --counts 2,4,8,16,32,64

uv run kr plot performance \
  "artifacts/$RUN_ID/performance.csv" \
  --show
```

That plot command writes the performance overview dashboard plus the primary
scale-decision charts under `artifacts/$RUN_ID/plots/`.

## Observation data in lifecycle tests

Observation data exists to answer the second core question: whether Kueue adds
unacceptable control-plane pressure while it handles large queue backlogs.
During lifecycle runs, `kueuer` samples controller, API server, and queue
state into `artifacts/<run_id>/observe/`, then uses those files to render
plots and evaluate the observation policy.
For an end-to-end cluster check with control-plane observations:

```bash
uv run kr lifecycle preflight --run-id "$RUN_ID"

uv run kr lifecycle e2e \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --counts 2,4,8,16,32,64
```

That workflow runs preflight, executes the benchmarks, collects observation
data by default, renders plots, evaluates the observation policy, writes the
comparison and observation reports, and records cleanup state under one run
directory.

If you want to skip observations for a specific run, pass `--no-observe`.

`uv run kr lifecycle collect --run-id "$RUN_ID"` is the post-processing step.
It reads the suite outputs that already exist for that run and generates the
plot directories, comparison report, and observation-derived reports. After it
finishes, inspect the paths it prints, especially:

1. `artifacts/$RUN_ID/plots/performance/`
2. `artifacts/$RUN_ID/plots/evictions/`
3. `artifacts/$RUN_ID/plots/observe/` when observation data exists
4. `artifacts/$RUN_ID/comparison/report.md`

If you want to re-render standalone plot families from an existing lifecycle
run, use the plot commands directly:

```bash
uv run kr plot performance \
  "artifacts//performance.csv" \
  --show

uv run kr plot evictions \
  "artifacts/$RUN_ID/evictions.yaml" \
  --show

uv run kr plot observations \
  "artifacts/$RUN_ID/observe/timeseries.csv" \
  --show
```

These commands write PNGs into `artifacts/$RUN_ID/plots/` automatically.

`--scenario` controls the queue setup used during lifecycle suite execution:

1. `control` uses the normal configured queues.
2. `backlog` creates temporary constrained `*-backlog` queues so the suite runs
   under intentional admission pressure.
