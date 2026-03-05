# Kueuer current state audit

This document captures the pre-Phase 1 state of `kueuer`, the key defects that
were confirmed from code and benchmark runs, and why those defects reduce trust
in performance and eviction conclusions.

## environment used for this audit

This audit and Phase 1 execution were run on March 4, 2026, in the `minikube`
context on a three-node local cluster. Kueue was installed from Helm chart
`0.11.6` with repository `dev/values.yaml`, except `enablePrometheus=false`
for local compatibility because the cluster does not include ServiceMonitor
CRDs.

## key pre-phase-1 defects

The following issues were present before code changes.

1. Performance CSV checkpoints duplicated rows. The benchmark repeatedly
   appended all previously collected rows, so early experiments were
   over-counted.
2. Eviction tracking reprocessed repeated conditions, inflating or corrupting
   `requeues` and related state.
3. Workload tracking could be reinitialized by repeated `Admitted=True`
   conditions, causing data loss and unstable eviction conclusions.
4. Eviction analysis assumed preemptor metadata was always present and could
   crash on missing entries.
5. Plot filtering used boolean identity checks that can break pandas filtering.
6. Some plotted metric labels implied startup/completion latency while the code
   actually computed turnaround proxies.

## baseline evidence

Phase 1 baseline runs are stored under `artifacts/phase1/baseline/`.

- `metadata.txt`: cluster and Kueue object state before baseline benchmark runs.
- `phase1_baseline_results.csv`: full performance suite output (contains
  duplicate rows by design of pre-fix code).
- `phase1_baseline_evictions.yaml`: baseline eviction tracking output.

## notable baseline run behavior

The baseline eviction run surfaced Kubernetes API and webhook instability under
burst job creation, including request timeouts and intermittent webhook connect
refusals. This behavior is directly relevant to production concerns about API
latency and control-plane stress.

## phase 1 audit goals

Phase 1 addresses data integrity and measurement semantics only. It does not
change deployment configs for `dev/` or `prod/` and does not introduce the
future lifecycle orchestration and observability extensions planned for later
phases.
