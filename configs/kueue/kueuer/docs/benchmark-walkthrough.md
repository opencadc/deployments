# Benchmark walkthrough

This walkthrough shows the shortest safe path from cluster checks to
interpretable artifacts. It uses explicit run IDs so the output paths are easy
to inspect afterward.

## Prepare one run ID

Choose one run ID and reuse it for every command in the walkthrough.

```bash
cd /Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer
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

Plot commands require an explicit output directory. A common layout is one
subdirectory per plot family.

```bash
uv run kr plot performance \
  "artifacts/$RUN_ID/performance.csv" \
  --output-dir "artifacts/$RUN_ID/plots/performance" \
  --show

uv run kr plot evictions \
  "artifacts/$RUN_ID/evictions.yaml" \
  --output-dir "artifacts/$RUN_ID/plots/evictions" \
  --show
```

## Run the lifecycle workflow

Use lifecycle when you want readiness checks, benchmark execution, collection,
and teardown tied to one run directory.

```bash
uv run kr lifecycle preflight --run-id "$RUN_ID"

uv run kr lifecycle e2e \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --counts 2,4,8,16,32,64 \
  --observe
```

The end-to-end workflow writes benchmark outputs, plots, observation data, and
manifest state under `artifacts/$RUN_ID/`.

## Work with observation data directly

Use the observation commands when you want to inspect control-plane behavior
without rerunning the full suite.

```bash
uv run kr observe collect \
  --run-id "$RUN_ID" \
  --namespace skaha-workload \
  --duration-seconds 60

uv run kr observe plot \
  --run-id "$RUN_ID" \
  --output-dir "artifacts/$RUN_ID/plots/observe" \
  --show

uv run kr observe analyze --run-id "$RUN_ID"
uv run kr observe report --run-id "$RUN_ID"
```

## Inspect the run directory

At the end of a run, inspect the directory structure directly:

```bash
find "artifacts/$RUN_ID" -maxdepth 3 -type f | sort
```

Typical outputs include:

1. `artifacts/$RUN_ID/performance.csv`
2. `artifacts/$RUN_ID/evictions.yaml`
3. `artifacts/$RUN_ID/plots/performance/*.png`
4. `artifacts/$RUN_ID/plots/evictions/*.png`
5. `artifacts/$RUN_ID/observe/timeseries.csv`
6. `artifacts/$RUN_ID/observe/summary.json`
7. `artifacts/$RUN_ID/observe/policy.json`
8. `artifacts/$RUN_ID/observe/report.md`
