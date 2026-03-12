# Benchmark Walkthrough

This walkthrough shows the shortest safe path from cluster checks to
interpretable artifacts. It uses explicit run IDs so the output paths are easy
to inspect afterward.

## Prepare one run ID

Choose one run ID and reuse it for every command in the walkthrough.

```bash
cd deployments/configs/kueue/kueuer
RUN_ID="$(date -u +%Y%m%d-%H%M%S)"
```

## Run standalone benchmarks

Use standalone commands when you want to focus on benchmark outputs first and
decide later whether you need lifecycle automation.

```bash
uv run kr benchmark performance \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --counts 2,4,8,16,32,64

uv run kr benchmark evictions \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --priorities low --priorities medium --priorities high
```

Each command prints the exact follow-up plot command you can run next.

## Plot the standalone results

Standalone benchmark plot commands derive `artifacts/$RUN_ID/plots/`
automatically from the input artifact path.

```bash
uv run kr plot performance \
  "artifacts/$RUN_ID/performance/performance.csv" \
  --show

uv run kr plot evictions \
  "artifacts/$RUN_ID/evictions/evictions.yaml" \
  --show
```

## Run the end-to-end workflow

Use the workflow commands when you want readiness checks, benchmark execution,
observation collection, plotting, and teardown tied to one run directory.

```bash
uv run kr preflight --run-id "$RUN_ID"

uv run kr benchmark e2e \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --counts 2,4,8,16,32,64 \
  --duration 30 \
  --cores 0.4 \
  --eviction-ram 8
```

The end-to-end workflow writes benchmark outputs, plots, observation data, and
a run manifest under `artifacts/$RUN_ID/`. The manifest (`manifest.json`)
records each lifecycle step (preflight, e2e, collect, teardown) and its
outcome for that run.

Observation collection is enabled by default for `benchmark e2e`. Pass
`--no-observe` when you explicitly want a run without observation artifacts.

`--scenario` controls the queue setup used for the suite:

1. `control` runs against the normal queue objects.
2. `backlog` creates temporary constrained `*-backlog` queues to force
   admission pressure.

## Re-render observation plots

Use the observation plot command when you already have
`artifacts/$RUN_ID/observe/timeseries.csv` and want fresh PNGs without
rerunning the suite.

```bash
uv run kr plot observations \
  "artifacts/$RUN_ID/observe/timeseries.csv" \
  --show
```

If you already ran `uv run kr benchmark e2e`, the run directory already
contains the generated plots and reports. Use the plot commands above when you
want to regenerate a specific plot family from existing artifacts.

## Inspect the run directory

At the end of a run, inspect the directory structure directly:

```bash
find "artifacts/$RUN_ID" -maxdepth 3 -type f | sort
```

Typical outputs include:

1. `artifacts/$RUN_ID/performance/performance.csv`
2. `artifacts/$RUN_ID/evictions/evictions.yaml`
3. `artifacts/$RUN_ID/plots/performance/*.png`
4. `artifacts/$RUN_ID/plots/evictions/*.png`
5. `artifacts/$RUN_ID/plots/observe/*.png`
6. `artifacts/$RUN_ID/observe/timeseries.csv`
7. `artifacts/$RUN_ID/observe/report.json`
8. `artifacts/$RUN_ID/report.json`
9. `artifacts/$RUN_ID/report.md`
