# Kueuer CLI reference

This page explains the public CLI surface in task order. The examples use the
same artifact contract as the implementation: artifact-producing commands write
to `artifacts/<run_id>/...` by default, and plot commands require an explicit
`--output-dir`.

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
execution and writes `performance.csv`.

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
| `--output-dir` | Directory where `performance.csv` is written. |
| `--run-id` | Run directory name when `--output-dir` is left at `artifacts`. |
| `--wait` | Delay between experiments so the cluster can settle. |
| `--apply-chunk-size` | Number of Job manifests per `kubectl apply` batch. |
| `--apply-retries` | Retry count for failed apply batches. |
| `--apply-backoff` | Backoff base in seconds between apply retries. |

### `kr benchmark evictions`

This command fills a queue with mixed priorities and writes `evictions.yaml`.

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
| `--output-dir` | Directory where `evictions.yaml` is written. |
| `--run-id` | Run directory name when `--output-dir` is left at `artifacts`. |
| `--apply-chunk-size` | Number of Job manifests per `kubectl apply` batch. |
| `--apply-retries` | Retry count for failed apply batches. |
| `--apply-backoff` | Backoff base in seconds between apply retries. |

## Plot commands

Use plot commands when you already have benchmark outputs and want PNG files.

### `kr plot performance`

This command reads a `performance.csv` file and renders the performance
dashboard plus the primary scale-decision plots: throughput, completion ratio,
tail turnaround, and non-runtime overhead.

| Option | Meaning |
| --- | --- |
| `FILEPATH` | Input `performance.csv` file to read. |
| `--output-dir` | Required directory where the PNG files are written. |
| `--show` | Open the plots interactively in addition to writing files. |

### `kr plot evictions`

This command reads an `evictions.yaml` file and renders eviction pressure,
timeline, and heatmap plots.

| Option | Meaning |
| --- | --- |
| `FILEPATH` | Input `evictions.yaml` file to read. |
| `--output-dir` | Required directory where the PNG files are written. |
| `--show` | Open the plots interactively in addition to writing files. |

## Lifecycle commands

Use lifecycle commands when you want one run directory that contains readiness
checks, benchmark outputs, plots, observation artifacts, and cleanup state.

### `kr lifecycle preflight`

This command validates cluster access, Kueue health, and required queue objects
in one step.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--namespace` | Namespace used for benchmark jobs and LocalQueue checks. |
| `--localqueue` | LocalQueue that benchmark jobs target. |
| `--clusterqueue` | ClusterQueue that the LocalQueue must reference. |
| `--apply-if-missing` | Apply queue YAML automatically when objects are missing. |

### `kr lifecycle run-suite`

This command executes the performance and eviction benchmark suite for one run.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--namespace` | Namespace used for benchmark jobs. |
| `--localqueue` | LocalQueue used for Kueue-managed jobs. |
| `--clusterqueue` | ClusterQueue name used by scenario helpers. |
| `--priority` | Priority class used for the performance benchmark. |
| `--profile` | Named default bundle for benchmark resource settings. |
| `--counts` | Explicit job counts for the performance benchmark. |
| `--scenario` | Queue scenario to apply before the suite starts. |
| `--observe` | Start the observation collector during the suite. |
| `--observe-interval-seconds` | Sampling cadence for observation data. |
| `--observe-output-subdir` | Relative subdirectory for observation files. |

### `kr lifecycle collect`

This command reads suite outputs and generates plots, summaries, and observation
reports under the run directory.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--performance-csv` | Override path for the suite performance CSV. |
| `--evictions-yaml` | Override path for the suite evictions YAML. |

### `kr lifecycle teardown`

This command removes benchmark jobs and optionally queue objects.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--namespace` | Namespace where benchmark jobs are deleted. |
| `--prefix` | Repeatable Job name prefix used for deletion matching. |
| `--delete-queues` | Delete queue objects defined in the development YAML. |

### `kr lifecycle e2e`

This command runs the full workflow: preflight, suite, collection, and
teardown.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--namespace` | Namespace used for the end-to-end workflow. |
| `--localqueue` | LocalQueue used for Kueue-managed jobs. |
| `--clusterqueue` | ClusterQueue name used for queue checks and scenarios. |
| `--priority` | Priority class used for the performance benchmark. |
| `--profile` | Named default bundle for benchmark resource settings. |
| `--counts` | Explicit job counts for the performance benchmark. |
| `--scenario` | Queue scenario to apply before the suite starts. |
| `--observe` | Start the observation collector during the suite. |
| `--observe-interval-seconds` | Sampling cadence for observation data. |
| `--observe-output-subdir` | Relative subdirectory for observation files. |
| `--skip-queue-apply` | Do not auto-apply queue YAML during preflight. |
| `--skip-teardown` | Keep benchmark jobs after the suite finishes. |
| `--keep-artifacts` | Keep the run directory on disk after completion. |

## Observation commands

Use observation commands when you want control-plane data without rerunning the
full lifecycle suite.

### `kr observe collect`

This command collects raw observation samples and writes them under
`observe/`.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--namespace` | Namespace used for queue and benchmark-pod sampling. |
| `--interval-seconds` | Sampling cadence when collecting for a duration. |
| `--duration-seconds` | Collection duration. `0` means collect one snapshot. |

### `kr observe plot`

This command renders the observation overview plus controller, API server, and
queue pressure plots from `observe/timeseries.csv`.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--output-dir` | Required directory where observation plots are written. |
| `--show` | Open the plots interactively in addition to writing files. |

### `kr observe analyze`

This command summarizes observation samples and evaluates the rollout policy.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
| `--baseline-summary` | Optional baseline summary JSON for latency comparison. |

### `kr observe report`

This command renders a Markdown report from `summary.json` and `policy.json`.

| Option | Meaning |
| --- | --- |
| `--artifacts-dir` | Root directory that holds run directories. |
| `--run-id` | Run directory name under `--artifacts-dir`. |
