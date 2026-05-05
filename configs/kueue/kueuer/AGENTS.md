## Learned User Preferences
- Prefer testing workflows that continue under restricted production RBAC by treating control-plane visibility checks as optional and collecting partial metrics.
- Prefer practical workarounds for production constraints over cluster-level changes that require broader platform modifications.
- Prefer inspecting node or cluster-wide inventory via the Kubernetes API (or other narrowly scoped API calls) instead of broad `kubectl get nodes` when that matches environment constraints.
- Prefer `kr cluster resources` output that uses IEC binary byte units (B, KiB, …, PiB) and at most three decimal places for displayed CPU and byte quantities.

## Learned Workspace Facts
- Benchmarking and preflight work for this area is centered in `configs/kueue/kueuer`.
- The production context used for tests has workload namespace access (for example, `canfar-kueue-testing`) but limited visibility into `kueue-system`, which restricts control-plane metric collection.
- Default stress VM memory fraction for benchmark jobs is `0.33` (`DEFAULT_STRESS_VM_MEMORY_FRACTION`); override with `--vm-memory-fraction` when needed.
- Benchmark job submission supports `--spawn-mechanism kubectl` (default, chunked `kubectl apply`) or `api` (Python client create-only with bounded concurrency and retries).
- `kr cluster resources` groups totals by `--node-label-key` (CLI default `skaha.opencadc.org/node-type`); `kueuer.resources.total()` requires `node_label_key` explicitly and does not default it in library code.
- Grouped results include per-bucket `count` (nodes) and per-product GPU lists; when `nvidia.com/gpu` capacity is zero or missing, counts may come from `nvidia.com/gpu.count` with kind from `nvidia.com/gpu.product` (e.g. MIG-style nodes).
