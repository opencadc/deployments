# Kueuer CLI reference

This page explains the public CLI surface in task order. The examples use the
same artifact contract as the implementation: artifact-producing commands write
to `artifacts/<run_id>/...` by default. Each run keeps benchmark inputs under
`performance/`, `evictions/`, and `observe/`, and all plots under `plots/`.
Standalone plot commands derive their output directory automatically from the
input artifact path.

## Core concepts

You only need two concepts before you read the commands:

1. `--profile` chooses a named bundle of defaults. `local-safe` is the light
   smoke-test profile. `cluster-scale` is the heavier profile for more realistic
   pressure.
2. `--run-id` controls the directory name under `artifacts/`. If you omit it,
   `kueuer` generates a UTC timestamp automatically.

## Benchmark commands

Use benchmark commands when you want raw benchmark data without the rest of the
lifecycle workflow.

### `kr benchmark performance`

This command compares direct Kubernetes job execution with Kueue-managed job
execution and writes `performance/performance.csv`.

| Option | Meaning |
| --- | --- |
| `--filepath` | Path to the Job manifest template used for generated jobs. |
| `--namespace` | Namespace where benchmark jobs are created. |
| `--kueue` | LocalQueue name used for the Kueue half of the comparison. |
| `--priority` | Workload priority class for Kueue-managed jobs. |
| `--profile` | Named default bundle for duration and resource requests. |
| `--counts` | Explicit job counts to test, in comma-separated form. |
| `--exponent-lower` | Lower power-of-two bound when `--counts` is blank. |
| `--exponent-higher` | Upper power-of-two bound when `--counts` is blank. |
| `--duration` | Runtime for each stress job, in seconds. |
| `--cores` | CPU requested and limited for each job. |
| `--ram` | Memory requested and limited for each job, in GiB. |
| `--storage` | Ephemeral storage requested and limited for each job, in GiB. |
| `--output-dir` | Run root where `performance/performance.csv` is written. |
| `--run-id` | Run directory name when `--output-dir` is left at `artifacts`. |
| `--wait` | Delay between experiments so the cluster can settle. |
| `--apply-chunk-size` | Number of Job manifests per `kubectl apply` batch. |
| `--apply-retries` | Retry count for failed apply batches. |
| `--apply-backoff` | Backoff base in seconds between apply retries. |

### `kr benchmark evictions`

This command fills a queue with mixed priorities and writes
`evictions/evictions.yaml`.

| Option | Meaning |
| --- | --- |
| `--filepath` | Path to the Job manifest template used for generated jobs. |
| `--namespace` | Namespace where benchmark jobs are created. |
| `--kueue` | LocalQueue name used for submitted jobs. |
| `--priorities` | Ordered priority classes from lowest to highest importance. |
| `--profile` | Named default bundle for queue pressure settings. |
| `--jobs` | Number of jobs launched per priority level. |
| `--cores` | Total CPU budget assumed for the packed ClusterQueue. |
| `--ram` | Total memory budget assumed for the packed ClusterQueue. |
| `--storage` | Total ephemeral storage budget assumed for the queue. |
| `--duration` | Longest runtime assigned before per-priority scaling. |
| `--output-dir` | Run root where `evictions/evictions.yaml` is written. |
| `--run-id` | Run directory name when `--output-dir` is left at `artifacts`. |
| `--apply-chunk-size` | Number of Job manifests per `kubectl apply` batch. |
| `--apply-retries` | Retry count for failed apply batches. |
| `--apply-backoff` | Backoff base in seconds between apply retries. |

## Plot commands

Use plot commands when you already have benchmark outputs and want PNG files.

### `kr plot performance`

This command reads a `performance.csv` file and renders the performance
dashboard plus the primary scale-decision plots: throughput, completion ratio,
tail turnaround, and non-runtime overhead under
`<run_root>/plots/performance/`.

| Option | Meaning |
| --- | --- |
| `FILEPATH` | Input `performance.csv` file to read. |
| `--show` | Open the plots interactively in addition to writing files. |

### `kr plot evictions`

This command reads an `evictions.yaml` file and renders eviction pressure,
timeline, and heatmap plots under `<run_root>/plots/evictions/`.

| Option | Meaning |
| --- | --- |
| `FILEPATH` | Input `evictions.yaml` file to read. |
| `--show` | Open the plots interactively in addition to writing files. |

### `kr plot observations`

This command reads an `observe/timeseries.csv` file and renders the
observation overview plus controller, API server, and queue-pressure plots
under `<run_root>/plots/observe/`.

| Option | Meaning |
| --- | --- |
| `FILEPATH` | Input `observe/timeseries.csv` file to read. |
| `--show` | Open the plots interactively in addition to writing files. |

## Workflow commands

Use these commands when you want one run directory that contains readiness
checks, benchmark outputs, plots, observation artifacts, and cleanup state.

### `kr preflight`

This command validates cluster access, Kueue health, and required queue objects
in one step.

| Option | Meaning |
| --- | --- |
| `--output-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--output-dir`. |
| `--namespace` | Namespace used for benchmark jobs and LocalQueue checks. |
| `--localqueue` | LocalQueue that benchmark jobs target. |
| `--clusterqueue` | ClusterQueue that the LocalQueue must reference. |
| `--apply-if-missing` | Apply queue YAML automatically when objects are missing. |

### `kr teardown`

This command removes benchmark jobs and optionally queue objects.

| Option | Meaning |
| --- | --- |
| `--output-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--output-dir`. |
| `--namespace` | Namespace where benchmark jobs are deleted. |
| `--prefix` | Repeatable Job name prefix used for deletion matching. |
| `--delete-queues` | Delete queue objects defined in the development YAML. |

### `kr benchmark e2e`

This command runs the full workflow: preflight, suite execution, observation
collection, plot and report generation, and teardown.

Precedence is explicit: profile defaults `<` shared e2e overrides `<`
eviction-specific overrides. `--counts` remains performance-only. `--duration`
applies to both performance and eviction.

| Option | Meaning |
| --- | --- |
| `--output-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--output-dir`. |
| `--namespace` | Namespace used for the end-to-end workflow. |
| `--localqueue` | LocalQueue used for Kueue-managed jobs. |
| `--clusterqueue` | ClusterQueue name used for queue checks and scenarios. |
| `--priority` | Priority class used for the performance benchmark. |
| `--profile` | Named default bundle for both performance and eviction settings. |
| `--counts` | Explicit job counts for the performance benchmark only. |
| `--scenario` | Queue scenario to apply before the suite starts. `control` keeps the normal queues. `backlog` creates temporary constrained `*-backlog` queues. |
| `--duration` | Shared duration override for both performance jobs and eviction jobs. |
| `--cores` | Shared CPU override for performance jobs and eviction queue capacity. |
| `--ram` | Shared RAM override for performance jobs and eviction queue capacity. |
| `--storage` | Shared storage override for performance jobs and eviction queue capacity. |
| `--eviction-jobs` | Override the eviction job count only. |
| `--eviction-cores` | Override eviction queue CPU capacity only. |
| `--eviction-ram` | Override eviction queue RAM capacity only. |
| `--eviction-storage` | Override eviction queue storage capacity only. |
| `--observe` / `--no-observe` | Collect observation data during the run. Enabled by default. |
| `--observe-interval-seconds` | Sampling cadence for observation data. |
| `--observe-output-subdir` | Relative subdirectory for observation files. |
| `--skip-queue-apply` | Do not auto-apply queue YAML during preflight. |
| `--skip-teardown` | Keep benchmark jobs after the suite finishes. |
| `--keep-artifacts` | Keep the run directory on disk after completion. |
