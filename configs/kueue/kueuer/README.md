# Kueuer

`kueuer` is a Python CLI for evaluating Kueue on real Kubernetes clusters.
It is built around two operational questions:

1. Can Kueue handle very large batch queues without breaking admission and
   eviction behavior?
2. Does Kueue add unacceptable load to the Kubernetes control plane while it
   does that work?

The package gives you benchmark commands, lifecycle automation, and observation
tools that write their artifacts under `artifacts/` by default.

## Install

Install the package in a virtual environment before you run benchmarks.

```bash
cd /Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer
uv sync
uv run kr --help
```

## Quick start

Use an explicit run ID when you want reproducible paths in notes or issue
reports. If you do not pass `--run-id`, artifact-producing commands create a
UTC timestamped directory under `artifacts/`.

```bash
cd /Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer
RUN_ID="$(date -u +%Y%m%d-%H%M%S)"

uv run kr benchmark performance \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --counts 2,4,8,16,32,64

uv run kr plot performance \
  "artifacts/$RUN_ID/performance.csv" \
  --output-dir "artifacts/$RUN_ID/plots/performance" \
  --show
```

For an end-to-end cluster check with control-plane observations:

```bash
uv run kr lifecycle preflight --run-id "$RUN_ID"

uv run kr lifecycle e2e \
  --run-id "$RUN_ID" \
  --profile local-safe \
  --counts 2,4,8,16,32,64 \
  --observe
```

## Documentation

The package-local docs under [`docs/`](/Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer/docs)
are the authoritative reference for `kueuer`.

Start with:

1. [`docs/README.md`](/Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer/docs/README.md)
2. [`docs/tool-overview.md`](/Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer/docs/tool-overview.md)
3. [`docs/cli-reference.md`](/Users/brars/Workspace/opencadc/deployments/configs/kueue/kueuer/docs/cli-reference.md)
