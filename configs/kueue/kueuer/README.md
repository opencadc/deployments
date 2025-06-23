# Kueuer Benchmarking Toolkit

Kueuer is a python package for benchmarking the performance and behavior of the deploying containerized workloads on a Kubernetes cluster. It provides a command line interface (CLI) for launching benchmarks, running jobs, and plotting results.

## Installation

To install Kueuer, you can use pip:

```bash
git clone https://github.com/opencadc/deployments.git
cd deployments/configs/kueue/kueuer
pip install -e .
```

Alternatively, it is also highly reccommended to install and run Kueuer in a virtual environment to avoid any conflicts with other packages.
Provided below is an example to do this, using the tool `uv`;

```bash
# Install uv
pip3 --user install uv
cd deployments/configs/kueue/kueuer
uv sync
uv run kr --help
```

## Goals

The goal of Kueuer is to provide a simple and efficient way to benchmark the performance of Kubernetes job scheduling and eviction behavior against Kubernetes Kueue. It is designed to for cluster administrators and developers who want to test the performance of their Kubernetes clusters and workloads, and iterate on their configurations.

## Features
- *Benchmarks*: Kueuer provides benchamrks to test the performance of Kubernetes job scheduling and eviction behavior.
- *Jobs*: Kueuer provides a simple interface to launch and delete massive number of jobs on a Kubernetes cluster to simulate stress.
- *Plots*: For performance benchmarks, Kueuer provides a simple interface for generating plots from results.

## Cluster Requirements
- Kubernetes cluster with Kueue installed. See the [Kueue documentation](https://kueue.sigs.k8s.io).
- Kueue configuration used by CADC can be found under [opencadc/deployments/configs/kueue](https://github.com/opencadc/deployments/configs/kueue/README.md)
- Kubernetes cluster access to create and delete jobs, and to install Kueue.


## Benchmarks

Kueuer provides benchmarking to evaluate the performance of Kubernetes job scheduling and eviction behavior. The benchmarks are designed to compare native Kubernetes job scheduling with the advanced capabilities of Kubernetes Kueue. This allows users to assess the impact of Kueue on job throughput, latency, and resource utilization. The default job configuration is set to use 1 CPU core, 1 GB of RAM, and 1 GB of ephemeral storage. The benchmarks can be customized to test different job configurations varying CPU, RAM, and storage requirements through the CLI. If you wish to change the default job configuration outside of the options provided, you can modify the job template file located at `src/kueuer/benchmarks/job.yaml`. The job template is a standard Kubernetes job specification and can be customized to suit your needs.

1. **Performance Benchmarks**:
   - Compare the scheduling efficiency and job execution times between native Kubernetes and Kueue.
   - Measure metrics such as throughput, startup latency, completion latency, and coefficient of variation, etc.
   - Generate comparative improvement metrics to evaluate the benefits of using Kueue.

2. **Eviction Benchmarks**:
   - Test the eviction behavior of Kueue in a packed cluster queue.
   - Analyze priority rule violations during preemptions and ensure workloads with higher priorities are not evicted by lower-priority workloads.

To run benchmarks, use the `kr benchmark` command. This command provides two subcommands:

### Performance Benchmarks

The performance benchmark launches a series of jobs with increasing job counts, starting from 2^1 to 2^N. It launches each set of jobs twice, once without and once with kueue enabled. The benchmark then tails the Kubernetes API server to capture the job scheduling and completion events to generate metrics and saves them to a CSV file.

#### Developer Notes
- The performance benchmark uses the `--exponent-lower` and `--exponent-higher` options to determine the range of job counts to test. The job counts are calculated as shown below, where `-el 4 -eh 8` would result in job counts of `[16, 32, 64, 128]`.
  ```python
  job_counts = [2**i for i in range(exponent_lower, exponent_higher + 1)]
  ```
- The results are saved incrementaly, so if benchmmarks crash, you can rerun them from any completed job count.
- When testing the performance of the cluster, it is recommended to atleast spawn 10-20x times the core count of the cluster to fully stress the kubernetes components.
- The jobs are by default configured to run for 1 minute, but this can be changed using the `--duration` option, but you are encouraged to change it to smaller duration to test out the api server and scheduler performance and larger duration to test the cluster performance.
- The benchmark uses the `--wait` option to determine the time to wait between experiments. This is useful to allow the cluster to recover from the previous experiment before starting the next one. This is useful to allow the cluster to settle and recover from any cleanup tasks before starting the next experiment. The default value is set to 60 seconds, but this can be changed using the `--wait` option.
- The benchark results are saved to `results.csv` by default, but this can be changed using the `--output` option.

#### Performance Benchmark Options

| Option             | Shorthand | Type    | Description                                                                                     | Default                                                                                     |
|--------------------|-----------|---------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| `--filepath`       | `-f`      | TEXT    | K8s job template.                                                                              | `/src/kueuer/benchmarks/job.yaml` |
| `--namespace`      | `-n`      | TEXT    | Namespace to launch jobs in.                                                                   | `skaha-workload`                                                                            |
| `--kueue`          | `-k`      | TEXT    | Local kueue to launch jobs in.                                                                 | `skaha-local-queue`                                                                         |
| `--priority`       | `-p`      | TEXT    | Kueue priority to launch jobs with.                                                            | `high`                                                                                      |
| `--exponent-lower` | `-el`     | INTEGER | Lower bound exponent for job count range `[2^el, ..., 2^eh]`.                                  | `1`                                                                                         |
| `--exponent-higher`| `-eh`     | INTEGER | Higher bound exponent for job count range `[2^el, ..., 2^eh]`.                                  | `3`                                                                                         |
| `--duration`       | `-d`      | INTEGER | Duration for each job in seconds.                                                              | `1`                                                                                         |
| `--cores`          | `-c`      | INTEGER | Number of CPU cores to allocate to each job.                                                   | `1`                                                                                         |
| `--ram`            | `-r`      | INTEGER | Amount of RAM to allocate to each job in GB.                                                   | `1`                                                                                         |
| `--storage`        | `-s`      | INTEGER | Amount of ephemeral-storage to allocate to each job in GB.                                     | `1`                                                                                         |
| `--output`         | `-o`      | TEXT    | File to save results to.                                                                       | `results.csv`                                                                               |
| `--wait`           | `-w`      | INTEGER | Time to wait between experiments.                                                              | `60`                                                                                        |
| `--help`           |           |         | Show this message and exit.                                                                    |                                                                                             |

#### Example Usage
![perf](https://github.com/user-attachments/assets/68337c82-a4de-4710-85bf-ad201ec84c5a)



### Eviction Benchmarks

The eviction benchmark launches a series of jobs with different priority levels and monitors the eviction behavior of Kueue by tailing the events emitted from the Kubernetes API server and analyzes the events to determine if the eviction behavior is as expected.

#### Developer Notes
- Before performing the eviction benchmark, `namespace, kueue local queues, and kueue workload priorities` must exist on the cluster.
- The benchmark launches the `--jobs` number of jobs per priority level, and the total number of jobs is equal to `jobs * priorities`.
- The eviction benchmark requires a packed cluster queue to test the eviction behavior. For examples, you can modify the `--jobs` parameter in conjunction with the `--cores`, `--ram`, and `--storage` parameters to create a packed cluster queue.
- The eviction benchmark uses the `--priorities` option to determine the list of priorities to test, specified from lower to higher importance. These can be passed as multiple arguments to the CLI, e.g.
   ```console
    $ kr benchmark eviction -p bad -p good -p best
   ```
   This signifies that the `bad` priority is the lowest and `best` is the highest.
- The `--cores, --ram, and --storage` options are used to determine the total resources available in the cluster queue. The benchmark will use these values to calculate the size of each job based `resource / job_count`.
- The jobs are launched with a duration of `duration / 2^N` where N is the index of the priority level. So, with the default priority levels of `low, medium, high`, the jobs will be launched with durations of `60, 30, 15` seconds respectively. This is done to ensure that the higher priority jobs are launched with shorter durations to test the eviction behavior.
- The eviction results are saved to `evictions.yaml` by default, but this can be changed using the `--output` option.


#### Eviction Benchmark Options
| Option          | Shorthand | Type     | Description                                                                                     | Default                                                                                     |
|------------------|-----------|----------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| `--filepath`    | `-f`      | TEXT     | K8s job template.                                                                              | `/src/kueuer/benchmarks/job.yaml` |
| `--namespace`   | `-n`      | TEXT     | Namespace to launch jobs in.                                                                   | `skaha-workload`                                                                            |
| `--kueue`       | `-k`      | TEXT     | Local Kueue queue to launch jobs in.                                                           | `skaha-local-queue`                                                                         |
| `--priorities`  | `-p`      | TEXT     | Ordered Kueue priorities to launch jobs with, from low to high.                                | `low, medium, high`                                                                         |
| `--jobs`        | `-j`      | INTEGER  | Jobs per priority level to launch.                                                             | `8`                                                                                         |
| `--cores`       | `-c`      | INTEGER  | Total number of CPU cores in the Kueue ClusterQueue.                                           | `8`                                                                                         |
| `--ram`         | `-r`      | INTEGER  | Total amount of RAM in the Kueue ClusterQueue in GB.                                           | `8`                                                                                         |
| `--storage`     | `-s`      | INTEGER  | Total amount of storage in the Kueue ClusterQueue in GB.                                       | `8`                                                                                         |
| `--duration`    | `-d`      | INTEGER  | Longest duration for jobs in seconds.                                                          | `120`                                                                                       |
| `--output`      | `-o`      | TEXT     | File to save results to.                                                                       | `evictions.yaml`                                                                            |
| `--help`        |           |          | Show this message and exit.                                                                    |                                                                                             |

##### Example Usage

```console
kr benchmark eviction -n skaha-workload -k skaha-local-queue -p low -p high -j 100
```

## Plotting Tools

Kueuer provides a simple interface for generating plots from the results of the performance and eviction benchmarks. The plots are generated using the `seaborn` library and and are based on the `results.csv` and `eviction.yaml` output created by the benchmarks.

### Performance Plots
The performance plots offer a visual representation of the performance metrics captured during the performance benchmarks. The plots include:
- **Throughput**: The number of jobs completed per second for each job count.
- **Startup Latency**: The time taken to start a job.
- **Completion Latency**: The time taken to complete a job.
- **Coefficient of Variation**: The variation in job completion times for each job count.
- **Distriution of Job Durations**: The distribution of job durations for each job count.
- **Trends for Completion Times**: The trends for completion times with respect to job counts.
- **Scaling Efficiency**: The scaling efficiency of the cluster for each job count.
- **Scheduling Overhead**: The scheduling overhead for each job count.

### Eviction Plots
The eviction plots provide a visual representation of the eviction behavior of Kueue during the eviction benchmarks. The plots include:

- **Total Evictions by Priority**: The total number of evictions for each priority level.
- **Job start and end times by priority**: The start and end times for each job, color-coded by priority level.
- **Evictions Heatmap**: A heatmap showing the number of evictions for each priority level over time.
- **Requeues**: The number of jobs that were requeued after being evicted per job. (This number is currently 2x than expected due to a code issue.)

### Usage
To generate the plots, use the `kr plot` command. This command provides two subcommands:

```console
kr plot performance FILEPATH
```

```console
kr plot evictions FILEPATH
```

The `FILEPATH` argument is the path to the results file generated by the benchmarks. The plots are saved to the `plots` directory by default, but this can be changed using the `--output` option.

## Jobs

Kueuer also provides a simple interface to launch and delete massive number of jobs on a Kubernetes cluster to simulate stress. This is useful for testing the performance of Kueue and Kubernetes job scheduling under heavy load.

### `kr jobs run`
| Option         | Shorthand | Type     | Description                                                                                     | Default                                                                                     |
|----------------|-----------|----------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| `--filepath`   | `-f`      | TEXT     | K8s job template.                                                                              | `src/kueuer/benchmarks/job.yaml` |
| `--namespace`  | `-n`      | TEXT     | Namespace to launch jobs in.                                                                   | `default`                                                                                   |
| `--prefix`     | `-p`      | TEXT     | Prefix for job names.                                                                          | `kueuer-job`                                                                                |
| `--jobs`       | `-j`      | INTEGER  | Number of jobs to launch.                                                                      | `1`                                                                                         |
| `--duration`   | `-d`      | INTEGER  | Duration for each job in seconds.                                                              | `60`                                                                                        |
| `--cores`      | `-c`      | INTEGER  | Number of CPU cores to allocate to each job.                                                   | `1`                                                                                         |
| `--ram`        | `-r`      | INTEGER  | Amount of RAM to allocate to each job in GB.                                                   | `1`                                                                                         |
| `--storage`    | `-s`      | INTEGER  | Amount of ephemeral-storage to allocate to each job in GB.                                     | `1`                                                                                         |
| `--kueue`      | `-k`      | TEXT     | Kueue queue to launch jobs in.                                                                 | `None`                                                                                      |
| `--priority`   | `-p`      | TEXT     | Kueue priority to launch jobs with.                                                            | `None`                                                                                      |
| `--help`       |           |          | Show this message and exit.                                                                    | `None`                                                                                      |

### `kr jobs delete`

| Option         | Shorthand | Type | Description                              | Default       |
|----------------|-----------|------|------------------------------------------|---------------|
| `--namespace`  | `-n`      | TEXT | Namespace to launch jobs in.             | `default`     |
| `--prefix`     | `-p`      | TEXT | Prefix for job names.                    | `kueuer-job`  |
| `--help`       |           |      | Show this message and exit.              |               |
