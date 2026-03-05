# Phase 1 implementation

This document explains exactly what changed in Phase 1, why it changed, and how
you can reproduce the same results on a local cluster.

## what Phase 1 implements

Phase 1 hardens correctness and metric semantics in `kueuer`.

1. It fixes duplicate-row CSV checkpoint output.
2. It makes workload condition processing transition-aware for eviction runs.
3. It prevents workload reinitialization on repeated `Admitted=True` updates.
4. It handles missing preemptor metadata without crashing analysis.
5. It fixes pandas boolean filtering in plotting code.
6. It introduces clearer turnaround naming in latency calculations while keeping
   compatibility columns.
7. It adds support for fractional RAM and storage values in benchmark
   parameters so local runs can avoid OOM-heavy profiles.

## files changed

Code files changed in this phase:

- `kueuer/src/kueuer/utils/io.py`
- `kueuer/src/kueuer/benchmarks/track.py`
- `kueuer/src/kueuer/benchmarks/analyze.py`
- `kueuer/src/kueuer/benchmarks/plot.py`
- `kueuer/src/kueuer/benchmarks/benchmark.py`
- `kueuer/src/kueuer/benchmarks/k8s.py`

New tests added in this phase:

- `kueuer/tests/test_io_results_write.py`
- `kueuer/tests/test_track_condition_dedup.py`
- `kueuer/tests/test_analyze_preemption_robustness.py`
- `kueuer/tests/test_plot_filters_and_semantics.py`

## local setup used for this phase

This phase used `minikube` context with three nodes and `metrics-server`.

Kueue install command used:

```bash
cd deployments/configs/kueue/dev
helm upgrade --install kueue oci://registry.k8s.io/kueue/charts/kueue \
  --version 0.11.6 \
  --values values.yaml \
  --set enablePrometheus=false \
  --namespace kueue-system \
  --create-namespace
```

> **Note:** `enablePrometheus=true` fails on this cluster because
> `ServiceMonitor` CRDs are not installed.

Queue resources applied:

```bash
cd deployments/configs/kueue
kubectl create namespace skaha-workload || true
kubectl create namespace canfar-b-workload || true
kubectl apply -f dev/clusterQueue.config.yaml
kubectl apply -f dev/localQueue.config.yaml
```

## baseline and post commands

Performance baseline:

```bash
cd deployments/configs/kueue/kueuer
uv run kr benchmark performance \
  -el 1 -eh 6 \
  -n skaha-workload \
  -k skaha-local-queue \
  -p high \
  -w 5 \
  -o ../artifacts/phase1/baseline/phase1_baseline_results.csv
```

Eviction baseline:

```bash
uv run kr benchmark evictions \
  -n skaha-workload \
  -k skaha-local-queue \
  -p low -p medium -p high \
  -j 8 \
  -o ../artifacts/phase1/baseline/phase1_baseline_evictions.yaml
```

Post-change performance:

```bash
uv run kr benchmark performance \
  -el 1 -eh 6 \
  -n skaha-workload \
  -k skaha-local-queue \
  -p high \
  -w 5 \
  -o ../artifacts/phase1/post/phase1_post_results.csv
```

Post-change eviction:

```bash
uv run kr benchmark evictions \
  -n skaha-workload \
  -k skaha-local-queue \
  -p low -p medium -p high \
  -j 8 \
  -o ../artifacts/phase1/post/phase1_post_evictions.yaml
```

Tuned low-memory eviction profile:

```bash
uv run kr benchmark evictions \
  -n skaha-workload \
  -k skaha-local-queue \
  -p low -p medium -p high \
  -j 8 -r 2 -s 2 -d 60 \
  -o ../artifacts/phase1/post/phase1_post_evictions_tuned.yaml
```

Plot generation (non-interactive, saved locally):

```bash
uv run kr plot performance \\
  ../artifacts/phase1/post/phase1_post_results.csv \\
  --output-dir /tmp/kueuer-plots-perf \\
  --no-show

uv run kr plot evictions \\
  ../artifacts/phase1/post/phase1_post_evictions_tuned.yaml \\
  --output-dir /tmp/kueuer-plots-evict \\
  --no-show
```

## test execution

Install test dependency and run tests:

```bash
cd deployments/configs/kueue/kueuer
uv add --dev pytest
uv run pytest -q
```

## artifacts produced

Phase 1 artifacts are under `artifacts/phase1/`.

- `baseline/metadata.txt`
- `baseline/phase1_baseline_results.csv`
- `baseline/phase1_baseline_evictions.yaml`
- `post/phase1_post_results.csv`
- `post/phase1_post_evictions.yaml`
- `post/phase1_post_evictions_tuned.yaml`
- `post/pods_after_phase1.txt`
- `post/kueue_post_state.txt`
- `comparison/phase1_delta_summary.json`
- `comparison/phase1_delta_report.md`

## known local runtime behavior

The baseline and post untuned eviction runs still showed intermittent API and
webhook instability under burst workload creation. The tuned profile reduced
per-job memory and completed with full tracked workload coverage.

You can always inspect post-run pod state with:

```bash
kubectl get pods -A
```
