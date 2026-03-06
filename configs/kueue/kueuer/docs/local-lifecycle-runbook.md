# Local lifecycle runbook

This runbook is the shortest operational checklist for running `kueuer`
against a real cluster. It assumes the cluster already exists and Kueue is
meant to be validated, not installed by this tool.

## Before you start

Confirm the intent of the run before you start generating pressure.

1. Use `local-safe` when you want a smoke test on a shared or fragile cluster.
2. Use `cluster-scale` when you want heavier pressure and already understand
   the blast radius.
3. Pick an explicit `RUN_ID` when the results will be shared or compared later.

## Preflight

Start with the combined preflight command so cluster access, Kueue health, and
queue readiness are checked together.

```bash
RUN_ID="$(date -u +%Y%m%d-%H%M%S)"

uv run kr lifecycle preflight \
  --run-id "$RUN_ID" \
  --namespace skaha-workload \
  --localqueue skaha-local-queue \
  --clusterqueue skaha-cluster-queue
```

If preflight fails, fix that before you run any benchmark workload.

## Run the suite

Use `e2e` when you want one command that leaves behind a coherent artifact
directory.

```bash
uv run kr lifecycle e2e \
  --run-id "$RUN_ID" \
  --namespace skaha-workload \
  --localqueue skaha-local-queue \
  --clusterqueue skaha-cluster-queue \
  --profile local-safe \
  --counts 2,4,8,16,32,64 \
  --observe
```

If you want to separate execution and collection, use `run-suite` first and
`collect` afterward.

## Inspect the result

When the run completes, inspect the run directory:

1. `manifest.json` for step history
2. `suite/performance.csv` for throughput and turnaround metrics
3. `suite/evictions.yaml` for eviction behavior
4. `plots/` for rendered PNG files
5. `observe/` for raw and summarized control-plane observations

## Teardown

If you skipped teardown during the run, clean up benchmark jobs explicitly.

```bash
uv run kr lifecycle teardown \
  --run-id "$RUN_ID" \
  --namespace skaha-workload
```

Add `--delete-queues` only when you intentionally want to remove the queue
objects defined in the development YAML.
